import json
from flask import Blueprint, render_template, jsonify, make_response
from flask_login import login_required, current_user
from ..models.consultation import Consultation
from ..models.user import User
from ..utils.decorators import login_required_api

reports_bp = Blueprint('reports', __name__)


def _parse_recs_to_list(text):
    """Parse stored recommendations — could be JSON array or plain text — into a list."""
    if not text:
        return []
    # Try parsing as JSON array first
    try:
        parsed = json.loads(text)
        if isinstance(parsed, list):
            return [str(item) for item in parsed if item]
    except (json.JSONDecodeError, TypeError):
        pass
    # Fallback: split by newline or bullet-like patterns
    lines = [l.strip().lstrip('-•* ') for l in text.replace('\r', '').split('\n') if l.strip()]
    return lines if len(lines) > 1 else [text]


@reports_bp.route('/reports/<int:consultation_id>')
@login_required
def report_page(consultation_id):
    """Render the medical report page."""
    consultation = Consultation.query.filter_by(
        id=consultation_id,
        user_id=current_user.id
    ).first()

    if not consultation:
        return render_template('reports/report.html', error='Report not found.')

    user = User.query.get(current_user.id)

    # Parse AI analysis (it's stored as JSON string of possible conditions)
    try:
        conditions = json.loads(consultation.ai_analysis) if consultation.ai_analysis else []
    except json.JSONDecodeError:
        conditions = [consultation.ai_analysis] if consultation.ai_analysis else []

    return render_template('reports/report.html',
                           consultation=consultation,
                           user=user,
                           conditions=conditions,
                           medication_items=_parse_recs_to_list(consultation.medication_recs),
                           food_items=_parse_recs_to_list(consultation.food_recs))


@reports_bp.route('/api/reports/<int:consultation_id>', methods=['GET'])
@login_required_api
def get_report(consultation_id):
    """Get report data as JSON."""
    consultation = Consultation.query.filter_by(
        id=consultation_id,
        user_id=current_user.id
    ).first()

    if not consultation:
        return jsonify({
            'success': False,
            'message': 'Report not found.'
        }), 404

    data = consultation.to_dict()
    data['user'] = current_user.to_dict()

    try:
        data['conditions'] = json.loads(consultation.ai_analysis) if consultation.ai_analysis else []
    except json.JSONDecodeError:
        data['conditions'] = [consultation.ai_analysis] if consultation.ai_analysis else []

    return jsonify({
        'success': True,
        'report': data
    }), 200


@reports_bp.route('/reports/<int:consultation_id>/pdf')
@login_required
def download_pdf(consultation_id):
    """Generate and download PDF report."""
    consultation = Consultation.query.filter_by(
        id=consultation_id,
        user_id=current_user.id
    ).first()

    if not consultation:
        return jsonify({'success': False, 'message': 'Report not found.'}), 404

    user = User.query.get(current_user.id)

    # Parse conditions
    try:
        conditions = json.loads(consultation.ai_analysis) if consultation.ai_analysis else []
    except json.JSONDecodeError:
        conditions = [consultation.ai_analysis] if consultation.ai_analysis else []

    # Render HTML template for PDF
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
        # xhtml2pdf not installed — fallback to HTML download
        response = make_response(html_content)
        response.headers['Content-Type'] = 'text/html'
        return response
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error generating PDF: {str(e)}'
        }), 500
