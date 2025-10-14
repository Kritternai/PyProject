"""
Pomodoro Timer Routes
Contains routes for Pomodoro Timer functionality.
"""

from flask import Blueprint, jsonify, request

pomodoro_bp = Blueprint('pomodoro', __name__)

@pomodoro_bp.route('/pomodoro/start', methods=['POST'])
def start_pomodoro():
    """Start a new Pomodoro session"""
    return jsonify({'message': 'Pomodoro started'}), 200

@pomodoro_bp.route('/pomodoro/stop', methods=['POST'])
def stop_pomodoro():
    """Stop current Pomodoro session"""
    return jsonify({'message': 'Pomodoro stopped'}), 200

@pomodoro_bp.route('/pomodoro/status', methods=['GET'])
def get_pomodoro_status():
    """Get status of current Pomodoro session"""
    return jsonify({'status': 'no active session'}), 200