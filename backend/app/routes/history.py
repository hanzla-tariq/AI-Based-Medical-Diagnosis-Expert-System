from flask import Blueprint, render_template, jsonify, redirect, url_for
from flask_login import login_required, current_user
from ..models.consultation import Consultation
from ..utils.decorators import login_required_api

history_bp = Blueprint('history', __name__)


@history_bp.route('/history')
@login_required
def history_page():
    """Render consultation history page. Admin users are redirected."""
    if current_user.is_admin:
        return redirect(url_for('admin.dashboard_page'))
    return render_template('history/index.html')


@history_bp.route('/api/history', methods=['GET'])
@login_required_api
def get_history():
    """Get all consultations for the current user."""
    consultations = Consultation.query.filter_by(user_id=current_user.id) \
        .order_by(Consultation.created_at.desc()).all()

    return jsonify({
        'success': True,
        'consultations': [c.to_dict() for c in consultations]
    }), 200


@history_bp.route('/api/history/<int:consultation_id>', methods=['GET'])
@login_required_api
def get_consultation(consultation_id):
    """Get a single consultation by ID."""
    consultation = Consultation.query.filter_by(
        id=consultation_id,
        user_id=current_user.id
    ).first()

    if not consultation:
        return jsonify({
            'success': False,
            'message': 'Consultation not found.'
        }), 404

    return jsonify({
        'success': True,
        'consultation': consultation.to_dict()
    }), 200
