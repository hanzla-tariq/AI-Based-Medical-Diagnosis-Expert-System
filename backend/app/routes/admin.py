"""
ShifaBot - Admin Routes
All routes require admin role via @admin_required decorator.
"""
import json
import re
from datetime import datetime, timedelta
from collections import Counter

from flask import Blueprint, request, jsonify, render_template, make_response
from flask_login import current_user
from sqlalchemy import func

from ..extensions import db
from ..models.user import User
from ..models.consultation import Consultation
from ..utils.decorators import admin_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


# ================================================================
#  Page Routes (render templates)
# ================================================================

@admin_bp.route('/')
@admin_required
def dashboard_page():
    """Render admin dashboard page."""
    return render_template('admin/dashboard.html')


@admin_bp.route('/users')
@admin_required
def users_page():
    """Render admin user management page."""
    return render_template('admin/users.html')


@admin_bp.route('/consultations')
@admin_required
def consultations_page():
    """Render admin consultation management page."""
    return render_template('admin/consultations.html')


@admin_bp.route('/reports')
@admin_required
def reports_page():
    """Render admin report management page."""
    return render_template('admin/reports.html')


# ================================================================
#  Analytics / Stats API
# ================================================================

@admin_bp.route('/api/admin/stats')
@admin_required
def get_stats():
    """Summary card statistics."""
    total_users = User.query.filter(User.role != 'admin').count()
    total_consultations = Consultation.query.count()
    total_reports = Consultation.query.filter(Consultation.ai_analysis.isnot(None)).count()
    total_ai_requests = Consultation.query.count()  # every consultation is an AI request

    return jsonify({
        'success': True,
        'stats': {
            'total_users': total_users,
            'total_consultations': total_consultations,
            'total_reports': total_reports,
            'total_ai_requests': total_ai_requests
        }
    }), 200


@admin_bp.route('/api/admin/analytics/symptoms')
@admin_required
def symptom_analytics():
    """Top 10 most common symptoms from all consultations."""
    consultations = Consultation.query.with_entities(Consultation.symptoms).all()
    symptom_counter = Counter()

    for (symptoms_text,) in consultations:
        if not symptoms_text:
            continue
        # Split by comma, semicolon, newline, or bullet
        parts = re.split(r'[,;\n\u2022\-\*]', symptoms_text)
        for part in parts:
            cleaned = part.strip().lower()
            if cleaned and len(cleaned) > 2:
                symptom_counter[cleaned] += 1

    top_10 = symptom_counter.most_common(10)
    return jsonify({
        'success': True,
        'labels': [s[0].title() for s in top_10],
        'values': [s[1] for s in top_10]
    }), 200


@admin_bp.route('/api/admin/analytics/age-groups')
@admin_required
def age_group_analytics():
    """Age group distribution across all consultations."""
    ages = Consultation.query.with_entities(Consultation.age).all()

    groups = {'0-18': 0, '19-35': 0, '36-50': 0, '51-65': 0, '65+': 0}
    for (age,) in ages:
        if age <= 18:
            groups['0-18'] += 1
        elif age <= 35:
            groups['19-35'] += 1
        elif age <= 50:
            groups['36-50'] += 1
        elif age <= 65:
            groups['51-65'] += 1
        else:
            groups['65+'] += 1

    return jsonify({
        'success': True,
        'labels': list(groups.keys()),
        'values': list(groups.values())
    }), 200


@admin_bp.route('/api/admin/analytics/daily-diagnoses')
@admin_required
def daily_diagnoses():
    """Daily diagnosis count for the last 30 days."""
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)

    rows = (
        db.session.query(
            func.date(Consultation.created_at).label('day'),
            func.count(Consultation.id).label('count')
        )
        .filter(Consultation.created_at >= thirty_days_ago)
        .group_by(func.date(Consultation.created_at))
        .order_by(func.date(Consultation.created_at))
        .all()
    )

    labels = [str(row.day) for row in rows]
    values = [row.count for row in rows]

    return jsonify({
        'success': True,
        'labels': labels,
        'values': values
    }), 200


# ================================================================
#  User Management API
# ================================================================

def _parse_recs_to_list(text):
    """Parse stored recommendations into a list."""
    if not text:
        return []
    try:
        parsed = json.loads(text)
        if isinstance(parsed, list):
            return [str(item) for item in parsed if item]
    except (json.JSONDecodeError, TypeError):
        pass
    lines = [l.strip().lstrip('-\u2022* ') for l in text.replace('\r', '').split('\n') if l.strip()]
    return lines if len(lines) > 1 else [text]


@admin_bp.route('/api/admin/users')
@admin_required
def get_users():
    """List all non-admin users with optional search."""
    q = request.args.get('q', '').strip().lower()
    query = User.query.filter(User.role != 'admin')

    if q:
        query = query.filter(
            db.or_(
                User.name.ilike(f'%{q}%'),
                User.email.ilike(f'%{q}%')
            )
        )

    users = query.order_by(User.created_at.desc()).all()

    result = []
    for u in users:
        data = u.to_dict()
        data['consultation_count'] = u.consultations.count()
        result.append(data)

    return jsonify({'success': True, 'users': result}), 200


@admin_bp.route('/api/admin/users/<int:user_id>')
@admin_required
def get_user_detail(user_id):
    """Single user detail with consultation count."""
    user = User.query.get(user_id)
    if not user:
        return jsonify({'success': False, 'message': 'User not found'}), 404

    data = user.to_dict()
    data['consultation_count'] = user.consultations.count()
    return jsonify({'success': True, 'user': data}), 200


@admin_bp.route('/api/admin/users/<int:user_id>/toggle-active', methods=['PUT'])
@admin_required
def toggle_user_active(user_id):
    """Toggle a user's active status."""
    user = User.query.get(user_id)
    if not user:
        return jsonify({'success': False, 'message': 'User not found'}), 404
    if user.is_admin:
        return jsonify({'success': False, 'message': 'Cannot deactivate admin'}), 403

    user.is_active = not user.is_active
    db.session.commit()

    return jsonify({
        'success': True,
        'message': f'User {"activated" if user.is_active else "deactivated"} successfully.',
        'is_active': user.is_active
    }), 200


@admin_bp.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    """Delete a user and all their consultations (cascade)."""
    user = User.query.get(user_id)
    if not user:
        return jsonify({'success': False, 'message': 'User not found'}), 404
    if user.is_admin:
        return jsonify({'success': False, 'message': 'Cannot delete admin user'}), 403

    db.session.delete(user)
    db.session.commit()
    return jsonify({'success': True, 'message': 'User deleted successfully.'}), 200


# ================================================================
#  Consultation Management API
# ================================================================

@admin_bp.route('/api/admin/consultations')
@admin_required
def get_consultations():
    """List all consultations with optional search."""
    q = request.args.get('q', '').strip().lower()

    query = db.session.query(Consultation, User).join(User, Consultation.user_id == User.id)

    if q:
        query = query.filter(
            db.or_(
                User.name.ilike(f'%{q}%'),
                Consultation.symptoms.ilike(f'%{q}%'),
                func.date(Consultation.created_at).ilike(f'%{q}%')
            )
        )

    rows = query.order_by(Consultation.created_at.desc()).all()

    result = []
    for c, u in rows:
        data = c.to_dict()
        data['patient_name'] = u.name
        data['patient_email'] = u.email
        result.append(data)

    return jsonify({'success': True, 'consultations': result}), 200


@admin_bp.route('/api/admin/consultations/<int:consultation_id>')
@admin_required
def get_consultation_detail(consultation_id):
    """Single consultation detail."""
    c = Consultation.query.get(consultation_id)
    if not c:
        return jsonify({'success': False, 'message': 'Consultation not found'}), 404

    user = User.query.get(c.user_id)
    data = c.to_dict()
    data['patient_name'] = user.name if user else 'Unknown'
    data['patient_email'] = user.email if user else ''

    # Parse conditions
    try:
        data['conditions'] = json.loads(c.ai_analysis) if c.ai_analysis else []
    except json.JSONDecodeError:
        data['conditions'] = [c.ai_analysis] if c.ai_analysis else []

    data['medication_items'] = _parse_recs_to_list(c.medication_recs)
    data['food_items'] = _parse_recs_to_list(c.food_recs)

    return jsonify({'success': True, 'consultation': data}), 200


@admin_bp.route('/api/admin/consultations/<int:consultation_id>', methods=['DELETE'])
@admin_required
def delete_consultation(consultation_id):
    """Delete a consultation record."""
    c = Consultation.query.get(consultation_id)
    if not c:
        return jsonify({'success': False, 'message': 'Consultation not found'}), 404

    db.session.delete(c)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Consultation deleted successfully.'}), 200


# ================================================================
#  Report Management API
# ================================================================

@admin_bp.route('/api/admin/reports')
@admin_required
def get_reports():
    """List all consultations that have AI analysis (reports)."""
    q = request.args.get('q', '').strip().lower()

    query = (
        db.session.query(Consultation, User)
        .join(User, Consultation.user_id == User.id)
        .filter(Consultation.ai_analysis.isnot(None))
    )

    if q:
        query = query.filter(
            db.or_(
                User.name.ilike(f'%{q}%'),
                func.date(Consultation.created_at).ilike(f'%{q}%')
            )
        )

    rows = query.order_by(Consultation.created_at.desc()).all()

    result = []
    for c, u in rows:
        result.append({
            'id': c.id,
            'patient_name': u.name,
            'patient_email': u.email,
            'age': c.age,
            'gender': c.gender,
            'mode': c.mode,
            'created_at': c.created_at.isoformat()
        })

    return jsonify({'success': True, 'reports': result}), 200


@admin_bp.route('/reports/<int:consultation_id>/pdf')
@admin_required
def admin_download_pdf(consultation_id):
    """Admin can download any user's report PDF."""
    consultation = Consultation.query.get(consultation_id)
    if not consultation:
        return jsonify({'success': False, 'message': 'Report not found.'}), 404

    user = User.query.get(consultation.user_id)

    # Parse conditions
    try:
        conditions = json.loads(consultation.ai_analysis) if consultation.ai_analysis else []
    except json.JSONDecodeError:
        conditions = [consultation.ai_analysis] if consultation.ai_analysis else []

    html_content = render_template('reports/report_pdf.html',
                                   consultation=consultation,
                                   user=user,
                                   conditions=conditions,
                                   medication_items=_parse_recs_to_list(consultation.medication_recs),
                                   food_items=_parse_recs_to_list(consultation.food_recs))

    try:
        from xhtml2pdf import pisa
        from io import BytesIO

        pdf_buffer = BytesIO()
        pisa_status = pisa.CreatePDF(html_content, dest=pdf_buffer)

        if pisa_status.err:
            raise Exception(f"PDF generation failed with {pisa_status.err} errors")

        pdf_buffer.seek(0)
        response = make_response(pdf_buffer.read())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = (
            f'attachment; filename=ShifaBot_Report_{consultation_id}.pdf'
        )
        return response
    except ImportError:
        response = make_response(html_content)
        response.headers['Content-Type'] = 'text/html'
        return response
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error generating PDF: {str(e)}'}), 500


@admin_bp.route('/api/admin/reports/<int:consultation_id>', methods=['DELETE'])
@admin_required
def delete_report(consultation_id):
    """Delete a report (deletes the consultation record)."""
    c = Consultation.query.get(consultation_id)
    if not c:
        return jsonify({'success': False, 'message': 'Report not found'}), 404

    db.session.delete(c)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Report deleted successfully.'}), 200
