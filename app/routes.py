from app import app, db
from flask import render_template, request, flash, redirect, url_for, session
from app.core.user_manager import UserManager
from app.core.authenticator import Authenticator

# Initialize UserManager and Authenticator
user_manager = UserManager()
authenticator = Authenticator(user_manager)

@app.route('/')
@app.route('/index')
def index():
    if 'user_id' in session:
        user = user_manager.get_user_by_id(session['user_id'])
        if user:
            return render_template('dashboard.html', title='Dashboard', user=user)
    return render_template('index.html', title='Home')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        if not username or not email or not password:
            flash('Please fill out all fields.', 'danger')
            return redirect(url_for('register'))

        user = authenticator.register(username, email, password)
        if user:
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Username or email already exists.', 'danger')

    return render_template('register.html', title='Register')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = authenticator.login(username, password)
        if user:
            session['user_id'] = user.id
            flash('Logged in successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.', 'danger')

    return render_template('login.html', title='Login')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))