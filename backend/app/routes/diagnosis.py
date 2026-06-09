import json
from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from flask_login import login_required, current_user
from ..extensions import db
from ..models.consultation import Consultation
from ..services.groq_service import analyze_symptoms, chatbot_response, extract_patient_info_from_chat
from ..utils.decorators import login_required_api

diagnosis_bp = Blueprint('diagnosis', __name__)


# --------------- Page Routes ---------------

@diagnosis_bp.route('/diagnosis/form')
@login_required
def form_page():
    """Render form-based diagnosis page. Admin users are redirected."""
    if current_user.is_admin:
        return redirect(url_for('admin.dashboard_page'))
    return render_template('diagnosis/form.html')


@diagnosis_bp.route('/diagnosis/chatbot')
@login_required
def chatbot_page():
    """Render chatbot-based diagnosis page. Admin users are redirected."""
    if current_user.is_admin:
        return redirect(url_for('admin.dashboard_page'))
    return render_template('diagnosis/chatbot.html')


# --------------- API Routes ---------------

@diagnosis_bp.route('/api/diagnosis/form', methods=['POST'])
@login_required_api
def form_diagnosis():
    """Process form-based diagnosis request."""
    data = request.get_json()

    # Validate required fields
    required_fields = ['symptoms', 'duration', 'severity', 'age', 'gender']
    for field in required_fields:
        if not data.get(field):
            return jsonify({
                'success': False,
                'message': f'The field "{field}" is required.'
            }), 400

    # Validate age
    try:
        age = int(data['age'])
        if age < 0 or age > 150:
            return jsonify({
                'success': False,
                'message': 'Please enter a valid age between 0 and 150.'
            }), 400
    except (ValueError, TypeError):
        return jsonify({
            'success': False,
            'message': 'Age must be a valid number.'
        }), 400

    try:
        # Call Gemini AI service
        result = analyze_symptoms(
            symptoms=data['symptoms'],
            duration=data['duration'],
            severity=data['severity'],
            age=age,
            gender=data['gender'],
            medical_history=data.get('medical_history', '')
        )

        # Save consultation to database
        consultation = Consultation(
            user_id=current_user.id,
            age=age,
            gender=data['gender'],
            medical_history=data.get('medical_history', ''),
            symptoms=data['symptoms'],
            duration=data['duration'],
            severity=data['severity'],
            mode='form',
            ai_analysis=result['ai_analysis'],
            medication_recs=result['medication_recs'],
            food_recs=result['food_recs']
        )
        db.session.add(consultation)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Diagnosis completed successfully!',
            'consultation_id': consultation.id,
            'result': result['full_analysis']
        }), 200

    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 503

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'An error occurred during diagnosis. Please try again.'
        }), 500


@diagnosis_bp.route('/api/diagnosis/chat', methods=['POST'])
@login_required_api
def chat_message():
    """Process a chatbot message and return AI response."""
    data = request.get_json()

    if not data or not data.get('message'):
        return jsonify({
            'success': False,
            'message': 'Message is required.'
        }), 400

    user_message = data['message'].strip()
    conversation_history = data.get('history', [])
    patient_info = data.get('patient_info', None)

    try:
        result = chatbot_response(conversation_history, user_message, patient_info)

        return jsonify({
            'success': True,
            'reply': result['reply'],
            'ready_for_diagnosis': result['ready_for_diagnosis']
        }), 200

    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 503

    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'An error occurred. Please try again.'
        }), 500


@diagnosis_bp.route('/api/diagnosis/chat/finalize', methods=['POST'])
@login_required_api
def finalize_chat_diagnosis():
    """Finalize chatbot diagnosis - extract info and generate full analysis."""
    data = request.get_json()

    if not data or not data.get('history'):
        return jsonify({
            'success': False,
            'message': 'Conversation history is required.'
        }), 400

    conversation_history = data['history']

    try:
        # Extract patient info from conversation
        patient_info = extract_patient_info_from_chat(conversation_history)

        # Validate extracted info
        if not patient_info.get('symptoms'):
            return jsonify({
                'success': False,
                'message': 'Could not extract symptoms from conversation. Please provide more details.'
            }), 400

        # Default values if not extracted
        age = patient_info.get('age', '30')
        try:
            age = int(age) if age else 30
        except (ValueError, TypeError):
            age = 30

        gender = patient_info.get('gender', 'not specified') or 'not specified'
        duration = patient_info.get('duration', 'not specified') or 'not specified'
        severity = patient_info.get('severity', 'moderate') or 'moderate'
        medical_history = patient_info.get('medical_history', '') or ''

        # Generate full analysis
        result = analyze_symptoms(
            symptoms=patient_info['symptoms'],
            duration=duration,
            severity=severity,
            age=age,
            gender=gender,
            medical_history=medical_history
        )

        # Save consultation
        consultation = Consultation(
            user_id=current_user.id,
            age=age,
            gender=gender,
            medical_history=medical_history,
            symptoms=patient_info['symptoms'],
            duration=duration,
            severity=severity,
            mode='chatbot',
            chat_log=json.dumps(conversation_history),
            ai_analysis=result['ai_analysis'],
            medication_recs=result['medication_recs'],
            food_recs=result['food_recs']
        )
        db.session.add(consultation)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Diagnosis completed successfully!',
            'consultation_id': consultation.id,
            'result': result['full_analysis']
        }), 200

    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 503

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'An error occurred during diagnosis. Please try again.'
        }), 500
