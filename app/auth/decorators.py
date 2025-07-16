from flask import abort
from flask_login import current_user, login_required
from functools import wraps

def role_required(allowed_roles):
    """Decorator to restrict access based on user role."""
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            if current_user.role not in allowed_roles:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator
