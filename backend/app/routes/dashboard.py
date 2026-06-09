from flask import Blueprint, render_template, jsonify, redirect, url_for
from flask_login import login_required, current_user
from ..models.consultation import Consultation
from ..utils.decorators import login_required_api

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/dashboard')
@login_required
def dashboard_page():
    """Render dashboard page. Admin users are redirected to admin panel."""
    if current_user.is_admin:
        return redirect(url_for('admin.dashboard_page'))
    return render_template('dashboard/index.html')


@dashboard_bp.route('/api/dashboard/stats', methods=['GET'])
@login_required_api
def dashboard_stats():
    """Get dashboard statistics for the current user."""
    total_consultations = Consultation.query.filter_by(user_id=current_user.id).count()

    # Recent consultations (last 5)
    recent = Consultation.query.filter_by(user_id=current_user.id) \
        .order_by(Consultation.created_at.desc()) \
        .limit(5).all()

    # Last consultation date
    last_consultation = Consultation.query.filter_by(user_id=current_user.id) \
        .order_by(Consultation.created_at.desc()).first()

    last_date = last_consultation.created_at.strftime('%B %d, %Y') if last_consultation else 'No consultations yet'

    # Count by mode
    form_count = Consultation.query.filter_by(user_id=current_user.id, mode='form').count()
    chatbot_count = Consultation.query.filter_by(user_id=current_user.id, mode='chatbot').count()

    return jsonify({
        'success': True,
        'stats': {
            'total_consultations': total_consultations,
            'form_consultations': form_count,
            'chatbot_consultations': chatbot_count,
            'last_consultation_date': last_date
        },
        'recent_consultations': [c.to_dict() for c in recent]
    }), 200
