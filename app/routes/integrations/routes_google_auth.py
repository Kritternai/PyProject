# app/routes/google_auth.py
from flask import Blueprint, current_app, session, redirect, url_for, request, flash
from google_auth_oauthlib.flow import Flow
import requests
import uuid
from app import db
from app.models.user import UserModel
import os
from pathlib import Path
import json

google_auth_bp = Blueprint('google_auth', __name__, url_prefix='/auth/google')

# ขอบเขตการขอข้อมูลจาก Google
SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile"
]

def get_google_flow(state=None, base_url=None):
    """
    ฟังก์ชันช่วยสร้างอ็อบเจกต์ Flow ของ Google OAuth
    เพื่อให้แน่ใจว่าใช้การตั้งค่าเดียวกันทั้งใน /login และ /callback
    """
    # --- START: โค้ดที่ปรับปรุง ---
    # สร้าง Path ไปยังไฟล์ client_secrets.json โดยอ้างอิงจากตำแหน่งของแอป (app/)
    # แล้วถอยกลับไปหนึ่งระดับ ซึ่งจะทำให้หาไฟล์เจอได้แน่นอนกว่า
    # ตราบใดที่ไฟล์ client_secrets.json อยู่ใน root ของโปรเจกต์
    try:
        # current_app.root_path จะชี้ไปที่โฟลเดอร์ 'app'
        project_root = Path(current_app.root_path).parent
        secrets_path = project_root / 'client_secrets.json'

        if not secrets_path.exists():
            # Try environment variables as a fallback (useful in CI or when client_secrets.json
            # has not been placed into the project root). This will construct a minimal
            # client_config for the Flow. If env vars are missing, preserve previous behavior.
            current_app.logger.warning(f"Client secrets file not found at {secrets_path}; trying environment variables as fallback.")
            client_id = current_app.config.get('GOOGLE_CLIENT_ID') or os.environ.get('GOOGLE_CLIENT_ID')
            client_secret = current_app.config.get('GOOGLE_CLIENT_SECRET') or os.environ.get('GOOGLE_CLIENT_SECRET')
            # Determine port: prefer configured PORT, then environment, else default 5004
            try:
                port = int(current_app.config.get('PORT', os.environ.get('PORT', 5004)))
            except Exception:
                port = 5004

            redirect_uri = f"http://localhost:{port}/auth/google/callback"

            if not client_id or not client_secret:
                current_app.logger.error(f"CRITICAL: Client secrets file not found. Checked at: {secrets_path}")
                return None

            try:
                # If base_url provided, prefer that as redirect_uri
                if base_url:
                    redirect_uri = base_url.rstrip('/') + '/auth/google/callback'

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
                return flow
            except Exception as e:
                current_app.logger.exception('CRITICAL: Failed to initialize Google Flow from env. Error: %s', e)
                return None

        # สร้าง Flow จากไฟล์ client_secrets.json โดยตรง
        flow = Flow.from_client_secrets_file(
            str(secrets_path),
            scopes=SCOPES,
            state=state
        )

        # สำคัญ: กำหนด redirect_uri ให้ตรงกับอันแรกที่อยู่ในไฟล์ secrets
        # เพื่อความแน่นอน 100%
        # เพิ่มการตรวจสอบ 'web' key เพื่อป้องกัน error หากไฟล์มี format อื่น
        client_config = json.loads(secrets_path.read_text())
        if 'web' in client_config and 'redirect_uris' in client_config['web']:
            uris = client_config['web']['redirect_uris']
            # If base_url provided, try to find matching redirect URI (same host:port)
            if base_url:
                # extract host:port from base_url
                host_port = base_url.rstrip('/').split('://')[-1].split('/')[0]
                preferred = base_url.rstrip('/') + '/auth/google/callback'
                if preferred in uris:
                    flow.redirect_uri = preferred
                else:
                    matched = None
                    for u in uris:
                        if host_port in u:
                            matched = u
                            break
                    flow.redirect_uri = matched or uris[0]
            else:
                flow.redirect_uri = client_config['web']['redirect_uris'][0]
        else:
            current_app.logger.error("CRITICAL: 'redirect_uris' not found in client_secrets.json under 'web' key.")
            return None

        return flow
    except Exception as e:
        current_app.logger.exception('CRITICAL: Failed to initialize Google Flow. Error: %s', e)
        return None
    # --- END: โค้ดที่ปรับปรุง ---


@google_auth_bp.route('/login')
def login():
    flow = get_google_flow(base_url=request.url_root)
    if not flow:
        flash('Google OAuth configuration error. Please check server logs for "CRITICAL" messages.', 'danger')
        return redirect(url_for('main_routes.index'))

    # สร้าง URL สำหรับให้ผู้ใช้กดเพื่อล็อกอิน
    authorization_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="select_account"
    )

    # เก็บ state ไว้ใน session เพื่อใช้ตรวจสอบใน callback
    session['oauth_state'] = state
    return redirect(authorization_url)


@google_auth_bp.route('/callback')
def callback():
    state = session.pop('oauth_state', None)
    # เพิ่มการตรวจสอบ state กับที่ได้จาก request.args
    if not state or state != request.args.get('state'):
        flash("Invalid state or session expired. Please try logging in again.", "warning")
        return redirect(url_for("main.index"))

    # สร้าง Flow อีกครั้งโดยใช้ state ที่ได้รับกลับมา
    flow = get_google_flow(state=state, base_url=request.url_root)
    if not flow:
        flash('Google OAuth configuration error. Please check server logs for "CRITICAL" messages.', 'danger')
        return redirect(url_for('main_routes.index'))

    try:
        # นำ authorization code ที่ได้จาก URL มาแลกเป็น token
        flow.fetch_token(authorization_response=request.url)
    except Exception as e:
        current_app.logger.exception("OAuth token fetch failed: %s", e)
        flash("Authentication failed with Google. Please try again.", "danger")
        return redirect(url_for("main.index"))

    # ดึงข้อมูลผู้ใช้จาก Google
    credentials = flow.credentials
    userinfo_response = requests.get(
        "https://www.googleapis.com/oauth2/v2/userinfo",
        headers={"Authorization": f"Bearer {credentials.token}"},
        timeout=10
    )
    
    if not userinfo_response.ok:
        flash("Failed to retrieve user information from Google.", "danger")
        return redirect(url_for("main.index"))
        
    userinfo = userinfo_response.json()
    email = userinfo.get("email")
    name = userinfo.get("name")
    picture = userinfo.get("picture")

    if not email:
        flash("Could not get email from Google account.", "danger")
        return redirect(url_for("main.index"))

    # ค้นหาหรือสร้างผู้ใช้ใหม่ในฐานข้อมูล
    user = UserModel.query.filter_by(email=email).first()
    if not user:
        user = UserModel(
            id=str(uuid.uuid4()),
            username=name or email.split("@")[0],
            email=email,
            password_hash="oauth_google", # ระบุว่าเป็นผู้ใช้จาก Google
            first_name=name or "",
            profile_image=picture,
            email_verified=True
        )
        db.session.add(user)
        db.session.commit()

    session["user_id"] = user.id
    flash("Logged in successfully with Google!", "success")
    return redirect(url_for("main.index"))

