from functools import wraps
from flask import jsonify, redirect, url_for, flash
from flask_login import current_user, login_required


def login_required_api(f):
    """Decorator that returns JSON 401 for API routes instead of redirecting."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'success': False, 'message': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Decorator that restricts access to admin users only.
    For API routes (paths starting with /api), returns JSON 403.
    For page routes, flashes an error and redirects to dashboard.
    """
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            # API routes return JSON 403
            if f.__module__.startswith('app.routes.admin') or \
               any('api' in str(r) for r in getattr(f, '__name__', '')):
                pass
            # Check if request is for API
            from flask import request
            if request.path.startswith('/api/'):
                return jsonify({'success': False, 'message': 'Admin access required'}), 403
            flash('You do not have permission to access the admin panel.', 'danger')
            return redirect(url_for('dashboard.dashboard_page'))
        return f(*args, **kwargs)
    return decorated_function
