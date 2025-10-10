from flask import Blueprint, render_template

pomodoro_bp = Blueprint('pomodoro', __name__)

@pomodoro_bp.route('/pomodoro')
def pomodoro():
    """Render the Pomodoro page (fragment or full page)."""
    return render_template('pomodoro_fragment.html')
