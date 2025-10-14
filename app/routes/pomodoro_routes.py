from flask import Blueprint, render_template

pomodoro_bp = Blueprint('pomodoro', __name__)

@pomodoro_bp.route('/pomodoro')
def pomodoro():
    return render_template('pomodoro_fragment.html')