"""
Google Sign-In (OAuth2) routes for Flask app.

Provides a simple "Sign in with Google" flow that:
- Redirects user to Google for auth
- Handles callback, fetches userinfo
- Creates or reuses a local user record and sets session['user_id']

Security notes:
- This example stores minimal user info. Do NOT store OAuth tokens in plaintext in production.
"""
from flask import (
    Blueprint,
    current_app,
    session,
    redirect,
    url_for,
    request,
    flash,
)
from google_auth_oauthlib.flow import Flow
import requests
import uuid
from app import db
from app.models.user import UserModel


google_auth_bp = Blueprint('google_auth', __name__, url_prefix='/auth/google')

# Basic scopes for authentication (openid + profile + email)
SCOPES = [
    'openid',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
]


@google_auth_bp.route('/login')
def login():
    """Start OAuth2 flow by redirecting to Google's authorization endpoint."""
    client_id = current_app.config.get('GOOGLE_CLIENT_ID')
    client_secret = current_app.config.get('GOOGLE_CLIENT_SECRET')
    if not client_id or not client_secret:
        flash('Google OAuth credentials are not configured.', 'danger')
        return redirect(url_for('main.index'))

    port = current_app.config.get('PORT', 5003)
    redirect_uri = f"http://localhost:{port}/auth/google/callback"

    flow = Flow.from_client_config(
        client_config={
            'web': {
                'client_id': client_id,
                'client_secret': client_secret,
                'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
                'token_uri': 'https://oauth2.googleapis.com/token',
                'redirect_uris': [redirect_uri],
            }
        },
        scopes=SCOPES,
    )
    flow.redirect_uri = redirect_uri

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='select_account',
    )

    session['oauth_state'] = state
    return redirect(authorization_url)


@google_auth_bp.route('/callback')
def callback():
    """Handle OAuth2 callback, fetch userinfo and login/create local user."""
    state = session.pop('oauth_state', None)
    client_id = current_app.config.get('GOOGLE_CLIENT_ID')
    client_secret = current_app.config.get('GOOGLE_CLIENT_SECRET')
    if not client_id or not client_secret:
        flash('Google OAuth credentials are not configured.', 'danger')
        return redirect(url_for('main.index'))

    port = current_app.config.get('PORT', 5003)
    redirect_uri = f"http://localhost:{port}/auth/google/callback"

    flow = Flow.from_client_config(
        client_config={
            'web': {
                'client_id': client_id,
                'client_secret': client_secret,
                'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
                'token_uri': 'https://oauth2.googleapis.com/token',
                'redirect_uris': [redirect_uri],
            }
        },
        scopes=SCOPES,
        state=state,
    )
    flow.redirect_uri = redirect_uri

    try:
        authorization_response = request.url
        flow.fetch_token(authorization_response=authorization_response)
    except Exception as e:
        current_app.logger.exception('Failed to fetch token from Google')
        flash('Authentication with Google failed.', 'danger')
        return redirect(url_for('main.index'))

    credentials = flow.credentials

    # Use token to fetch userinfo
    resp = requests.get(
        'https://www.googleapis.com/oauth2/v2/userinfo',
        headers={'Authorization': f'Bearer {credentials.token}'},
        timeout=10,
    )

    if resp.status_code != 200:
        current_app.logger.error('Failed to fetch userinfo: %s', resp.text)
        flash('Failed to fetch user profile from Google.', 'danger')
        return redirect(url_for('main.index'))

    userinfo = resp.json()
    email = userinfo.get('email')
    name = userinfo.get('name') or ''
    picture = userinfo.get('picture')

    if not email:
        flash('Google account did not provide an email address.', 'danger')
        return redirect(url_for('main.index'))

    # Find existing user by email or create a new one
    user = UserModel.query.filter_by(email=email).first()
    if not user:
        new_user = UserModel(
            id=str(uuid.uuid4()),
            username=email.split('@')[0],
            email=email,
            password_hash='oauth',  # marker for oauth-only user; replace in production
            first_name=name,
            profile_image=picture,
            email_verified=True,
        )
        db.session.add(new_user)
        try:
            db.session.commit()
            user = new_user
        except Exception:
            db.session.rollback()
            current_app.logger.exception('Failed to create user')
            flash('Failed to create user account.', 'danger')
            return redirect(url_for('main.index'))

    else:
        # Update profile image / name if missing
        updated = False
        if picture and user.profile_image != picture:
            user.profile_image = picture
            updated = True
        if name and (not user.first_name):
            user.first_name = name
            updated = True
        if updated:
            try:
                db.session.commit()
            except Exception:
                db.session.rollback()

    # Log the user in by setting session
    session['user_id'] = user.id
    flash('Logged in with Google.', 'success')

    # Note: if you need to persist credentials for API calls (Classroom/Drive)
    # store credentials.refresh_token and other values securely (encrypted)

    return redirect(url_for('main.index'))
# app/routes_google_auth.py
from flask import Blueprint, current_app, session, redirect, url_for, request, flash, g
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
import requests
from functools import wraps
from app.models.user import UserModel
from app import db

google_auth_bp = Blueprint('google_auth', __name__, url_prefix='/auth/google')

SCOPES = ["openid", "https://www.googleapis.com/auth/userinfo.email", "https://www.googleapis.com/auth/userinfo.profile"]

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return wrapper

@google_auth_bp.route('/login')
def login():
    if not current_app.config.get('GOOGLE_CLIENT_ID') or not current_app.config.get('GOOGLE_CLIENT_SECRET'):
        flash('Google client credentials not configured', 'danger')
        return redirect(url_for('main.index'))

    port = current_app.config.get('PORT', 5004)
    redirect_uri = f"http://localhost:{port}/auth/google/callback"

    flow = Flow.from_client_config(
        client_config={
            "web": {
                "client_id": current_app.config['GOOGLE_CLIENT_ID'],
                "client_secret": current_app.config['GOOGLE_CLIENT_SECRET'],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [redirect_uri]
            }
        },
        scopes=SCOPES,
    )
    flow.redirect_uri = redirect_uri

    authorization_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="select_account"
    )

    session['oauth_state'] = state
    return redirect(authorization_url)

@google_auth_bp.route('/callback')
def callback():
    state = session.pop('oauth_state', None)
    port = current_app.config.get('PORT', 5004)
    redirect_uri = f"http://localhost:{port}/auth/google/callback"

    flow = Flow.from_client_config(
        client_config={
            "web": {
                "client_id": current_app.config['GOOGLE_CLIENT_ID'],
                "client_secret": current_app.config['GOOGLE_CLIENT_SECRET'],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [redirect_uri]
            }
        },
        scopes=SCOPES,
        state=state
    )
    flow.redirect_uri = redirect_uri

    authorization_response = request.url
    try:
        flow.fetch_token(authorization_response=authorization_response)
    except Exception as e:
        current_app.logger.exception("Failed to fetch token")
        flash("Authentication failed", "danger")
        return redirect(url_for('main.index'))

    credentials = flow.credentials  # google.oauth2.credentials.Credentials

    # Fetch userinfo
    resp = requests.get(
        'https://www.googleapis.com/oauth2/v2/userinfo',
        headers={'Authorization': f'Bearer {credentials.token}'}
    )
    if resp.status_code != 200:
        flash("Failed to fetch user info from Google", "danger")
        return redirect(url_for('main.index'))

    userinfo = resp.json()
    email = userinfo.get('email')
    google_id = userinfo.get('id')
    name = userinfo.get('name') or ""
    picture = userinfo.get('picture')

    # Find or create user
    user = UserModel.query.filter_by(email=email).first()
    if not user:
        # Create a local user - you might want to set a random password or mark as oauth user
        import uuid
        new_user = UserModel(
            id=str(uuid.uuid4()),
            username=email.split('@')[0],
            email=email,
            password_hash='oauth',  # mark as oauth-only (or generate random)
            first_name=name,
            profile_image=picture,
            email_verified=True
        )
        db.session.add(new_user)
        db.session.commit()
        user = new_user

    # Optionally update user profile with Google data (picture, name)
    updated = False
    if picture and user.profile_image != picture:
        user.profile_image = picture
        updated = True
    if name and (not user.first_name):
        user.first_name = name
        updated = True
    if updated:
        db.session.commit()

    # Set session
    session['user_id'] = user.id

    # If you need the credentials later for Classroom/Drive, store credentials.refresh_token securely
    # WARNING: store tokens encrypted or in a secure store in production
    return redirect(url_for('main.index'))