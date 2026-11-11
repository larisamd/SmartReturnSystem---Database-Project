from functools import wraps

from flask import flash, redirect, session, url_for


def login_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to continue.', 'warning')
            return redirect(url_for('login'))
        return view_func(*args, **kwargs)

    return wrapped


def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(*args, **kwargs):
            if 'user_role' not in session:
                flash('Your session is invalid. Please log in again.', 'warning')
                return redirect(url_for('login'))
            if session['user_role'] not in roles:
                flash('You do not have permission to access this section.', 'danger')
                return redirect(url_for('dashboard'))
            return view_func(*args, **kwargs)

        return wrapped

    return decorator
