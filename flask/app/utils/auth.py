import jwt  # handles creating and verifying JWT tokens
from functools import wraps  # needed to preserve the original function's name when wrapping it
from flask import request, jsonify, current_app  # request = incoming HTTP request, current_app = access to app.config


def require_auth(f):
    """
    A decorator that protects any route it's placed on.
    It checks the request for a valid JWT token before
    allowing the route function to run.
    """
    @wraps(f)  # preserves the original function name 
    def decorated(*args, **kwargs):
        token = None  

        # JWT tokens are sent in the Authorization header 
        auth_header = request.headers.get('Authorization', '')  # get the header, default to empty string if missing

        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]  # extract just the token part after "Bearer "

        if not token:
            # if no token was provided the request is rejected
            return jsonify({'error': 'Authentication token missing'}), 401

        try:
            # verify token using the app's secret key
            # if the token was tampered with or expired, this will raise an exception
            payload = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],  # the secret key from app.py 
                algorithms=['HS256']  # HS256 is the signing algorithm we used when creating the token
            )

            # attach the decoded token data to the request object
            # allowing any route using this decorator can access request.user
            request.user = payload

        except jwt.ExpiredSignatureError:
            # token was valid but has passed its 24-hour expiry time
            return jsonify({'error': 'Token has expired, please log in again'}), 401

        except jwt.InvalidTokenError:
            # token exists but has been tampered with or is malformed
            return jsonify({'error': 'Invalid token'}), 401

        return f(*args, **kwargs)  # token is valid — allow the route to run normally

    return decorated


def require_role(role):
    """
    A decorator that checks the user's role from the decoded token.
    Must always be used AFTER @require_auth, because it depends on
    request.user being set by require_auth first.

    Usage:
        @require_auth
        @require_role('lecturer')
        def my_route():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            # request.user was set by require_auth above
            if request.user.get('role') != role:
                # user is logged in but doesn't have the right role
                return jsonify({'error': f'Only {role}s can perform this action'}), 403
            return f(*args, **kwargs)  # role matches — allow through
        return decorated
    return decorator
