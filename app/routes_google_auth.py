# app/routes/google_auth.py
from flask import Blueprint, current_app, session, redirect, url_for, request, flash
from google_auth_oauthlib.flow import Flow
import requests
import uuid
from app import db
from app.models.user import UserModel
import os

google_auth_bp = Blueprint('google_auth', __name__, url_prefix='/auth/google')

SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile"
]

@google_auth_bp.route('/login')
def login():
    client_id = current_app.config.get('GOOGLE_CLIENT_ID')
    client_secret = current_app.config.get('GOOGLE_CLIENT_SECRET')
    if not client_id or not client_secret:
        flash("Google OAuth credentials not configured", "danger")
        return redirect(url_for("main.index"))

    port = current_app.config.get('PORT', 5003)
    redirect_uri = f"http://localhost:{port}/auth/google/callback"

    flow = Flow.from_client_config(
        client_config={
            "web": {
                "client_id": client_id,
                "client_secret": client_secret,
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
    if not state:
        flash("Session expired. Please try again.", "warning")
        return redirect(url_for("main.index"))

    client_id = current_app.config.get('GOOGLE_CLIENT_ID')
    client_secret = current_app.config.get('GOOGLE_CLIENT_SECRET')
    port = current_app.config.get('PORT', 5003)
    redirect_uri = f"http://localhost:{port}/auth/google/callback"

    flow = Flow.from_client_config(
        client_config={
            "web": {
                "client_id": client_id,
                "client_secret": client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [redirect_uri]
            }
        },
        scopes=SCOPES,
        state=state
    )
    flow.redirect_uri = redirect_uri

    try:
        flow.fetch_token(authorization_response=request.url)
    except Exception as e:
        current_app.logger.exception("OAuth token fetch failed: %s", e)
        flash("Authentication failed.", "danger")
        return redirect(url_for("main.index"))

    credentials = flow.credentials
    userinfo = requests.get(
        "https://www.googleapis.com/oauth2/v2/userinfo",
        headers={"Authorization": f"Bearer {credentials.token}"},
        timeout=10
    ).json()

    email = userinfo.get("email")
    name = userinfo.get("name")
    picture = userinfo.get("picture")

    if not email:
        flash("Google account did not return an email.", "danger")
        return redirect(url_for("main.index"))

    # Find or create user
    user = UserModel.query.filter_by(email=email).first()
    if not user:
        user = UserModel(
            id=str(uuid.uuid4()),
            username=email.split("@")[0],
            email=email,
            password_hash="oauth",
            first_name=name or "",
            profile_image=picture,
            email_verified=True
        )
        db.session.add(user)
        db.session.commit()

    session["user_id"] = user.id
    flash("Logged in with Google!", "success")
    return redirect(url_for("main.index"))
