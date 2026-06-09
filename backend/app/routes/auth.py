import re
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from ..extensions import db
from ..models.user import User

auth_bp = Blueprint('auth', __name__)


# --------------- Page Routes ---------------

@auth_bp.route('/login')
def login_page():
    """Render login page."""
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.dashboard_page'))
        return redirect(url_for('dashboard.dashboard_page'))
    return render_template('auth/login.html')


@auth_bp.route('/signup')
def signup_page():
    """Render signup page."""
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.dashboard_page'))
        return redirect(url_for('dashboard.dashboard_page'))
    return render_template('auth/signup.html')


# --------------- API Routes ---------------

@auth_bp.route('/api/auth/signup', methods=['POST'])
def signup():
    """Register a new user."""
    data = request.get_json()

    # Validate required fields
    if not data or not data.get('name') or not data.get('email') or not data.get('password'):
        return jsonify({
            'success': False,
            'message': 'Name, email, and password are required.'
        }), 400

    name = data['name'].strip()
    email = data['email'].strip().lower()
    password = data['password']

    # Validate email format
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        return jsonify({
            'success': False,
            'message': 'Invalid email format.'
        }), 400

    # Validate password length
    if len(password) < 6:
        return jsonify({
            'success': False,
            'message': 'Password must be at least 6 characters long.'
        }), 400

    # Check if email already exists
    if User.query.filter_by(email=email).first():
        return jsonify({
            'success': False,
            'message': 'An account with this email already exists.'
        }), 409

    # Create new user
    try:
        new_user = User(name=name, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        # Auto-login after signup
        login_user(new_user)

        return jsonify({
            'success': True,
            'message': 'Account created successfully!',
            'user': new_user.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'An error occurred during registration. Please try again.'
        }), 500


@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    """Authenticate user and create session."""
    data = request.get_json()

    if not data or not data.get('email') or not data.get('password'):
        return jsonify({
            'success': False,
            'message': 'Email and password are required.'
        }), 400

    email = data['email'].strip().lower()
    password = data['password']

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return jsonify({
            'success': False,
            'message': 'Invalid email or password.'
        }), 401

    # Reject deactivated accounts
    if not user.is_active:
        return jsonify({
            'success': False,
            'message': 'Your account has been deactivated. Please contact the administrator.'
        }), 403

    login_user(user)

    return jsonify({
        'success': True,
        'message': 'Login successful!',
        'user': user.to_dict()
    }), 200


@auth_bp.route('/api/auth/logout', methods=['GET', 'POST'])
@login_required
def logout():
    """Logout the current user."""
    logout_user()
    if request.method == 'GET':
        return redirect(url_for('index'))
    return jsonify({
        'success': True,
        'message': 'Logged out successfully.'
    }), 200


@auth_bp.route('/api/auth/status', methods=['GET'])
def auth_status():
    """Check authentication status."""
    if current_user.is_authenticated:
        return jsonify({
            'authenticated': True,
            'user': current_user.to_dict()
        }), 200
    return jsonify({
        'authenticated': False
    }), 200
