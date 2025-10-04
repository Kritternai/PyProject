"""
Pomodoro Controller
HTTP request handling for Pomodoro functionality
"""
from typing import Dict, Any
from flask import request, jsonify, session
from app.application.services.pomodoro_service import PomodoroService
from app.domain.entities.pomodoro_session import SessionType, SessionStatus

class PomodoroController:
    """Pomodoro HTTP request controller"""
    
    def __init__(self, pomodoro_service: PomodoroService):
        self.pomodoro_service = pomodoro_service
    
    def start_session(self) -> Dict[str, Any]:
        """Start a new pomodoro session"""
        try:
            data = request.get_json()
            user_id = session.get('user_id')
            
            if not user_id:
                return jsonify({'success': False, 'message': 'User not authenticated'}), 401
            
            session_type = SessionType(data.get('session_type', 'focus'))
            duration = data.get('duration', 25)  # Default 25 minutes
            
            pomodoro_session = self.pomodoro_service.start_session(
                user_id=user_id,
                session_type=session_type,
                duration=duration,
                lesson_id=data.get('lesson_id'),
                section_id=data.get('section_id'),
                task_id=data.get('task_id'),
                notes=data.get('notes'),
                mood_before=data.get('mood_before')
            )
            
            return jsonify({
                'success': True,
                'message': 'Session started successfully',
                'session': pomodoro_session.to_dict()
            }), 201
            
        except ValueError as e:
            return jsonify({'success': False, 'message': str(e)}), 400
        except Exception as e:
            return jsonify({'success': False, 'message': f'Error starting session: {str(e)}'}), 500
    
    def pause_session(self) -> Dict[str, Any]:
        """Pause an active session"""
        try:
            data = request.get_json()
            user_id = session.get('user_id')
            session_id = data.get('session_id')
            
            if not user_id:
                return jsonify({'success': False, 'message': 'User not authenticated'}), 401
            
            if not session_id:
                return jsonify({'success': False, 'message': 'Session ID required'}), 400
            
            session = self.pomodoro_service.pause_session(user_id, session_id)
            
            return jsonify({
                'success': True,
                'message': 'Session paused successfully',
                'session': session.to_dict()
            })
            
        except ValueError as e:
            return jsonify({'success': False, 'message': str(e)}), 400
        except Exception as e:
            return jsonify({'success': False, 'message': f'Error pausing session: {str(e)}'}), 500
    
    def resume_session(self) -> Dict[str, Any]:
        """Resume a paused session"""
        try:
            data = request.get_json()
            user_id = session.get('user_id')
            session_id = data.get('session_id')
            
            if not user_id:
                return jsonify({'success': False, 'message': 'User not authenticated'}), 401
            
            if not session_id:
                return jsonify({'success': False, 'message': 'Session ID required'}), 400
            
            session = self.pomodoro_service.resume_session(user_id, session_id)
            
            return jsonify({
                'success': True,
                'message': 'Session resumed successfully',
                'session': session.to_dict()
            })
            
        except ValueError as e:
            return jsonify({'success': False, 'message': str(e)}), 400
        except Exception as e:
            return jsonify({'success': False, 'message': f'Error resuming session: {str(e)}'}), 500
    
    def complete_session(self) -> Dict[str, Any]:
        """Complete a session"""
        try:
            data = request.get_json()
            user_id = session.get('user_id')
            session_id = data.get('session_id')
            
            if not user_id:
                return jsonify({'success': False, 'message': 'User not authenticated'}), 401
            
            if not session_id:
                return jsonify({'success': False, 'message': 'Session ID required'}), 400
            
            session = self.pomodoro_service.complete_session(
                user_id=user_id,
                session_id=session_id,
                productivity_score=data.get('productivity_score'),
                mood_after=data.get('mood_after'),
                focus_score=data.get('focus_score'),
                energy_level=data.get('energy_level'),
                difficulty_level=data.get('difficulty_level'),
                notes=data.get('notes')
            )
            
            return jsonify({
                'success': True,
                'message': 'Session completed successfully',
                'session': session.to_dict()
            })
            
        except ValueError as e:
            return jsonify({'success': False, 'message': str(e)}), 400
        except Exception as e:
            return jsonify({'success': False, 'message': f'Error completing session: {str(e)}'}), 500
    
    def interrupt_session(self) -> Dict[str, Any]:
        """Interrupt a session"""
        try:
            data = request.get_json()
            user_id = session.get('user_id')
            session_id = data.get('session_id')
            reason = data.get('reason')
            
            if not user_id:
                return jsonify({'success': False, 'message': 'User not authenticated'}), 401
            
            if not session_id:
                return jsonify({'success': False, 'message': 'Session ID required'}), 400
            
            session = self.pomodoro_service.interrupt_session(user_id, session_id, reason)
            
            return jsonify({
                'success': True,
                'message': 'Session interrupted successfully',
                'session': session.to_dict()
            })
            
        except ValueError as e:
            return jsonify({'success': False, 'message': str(e)}), 400
        except Exception as e:
            return jsonify({'success': False, 'message': f'Error interrupting session: {str(e)}'}), 500
    
    def cancel_session(self) -> Dict[str, Any]:
        """Cancel a session"""
        try:
            data = request.get_json()
            user_id = session.get('user_id')
            session_id = data.get('session_id')
            
            if not user_id:
                return jsonify({'success': False, 'message': 'User not authenticated'}), 401
            
            if not session_id:
                return jsonify({'success': False, 'message': 'Session ID required'}), 400
            
            session = self.pomodoro_service.cancel_session(user_id, session_id)
            
            return jsonify({
                'success': True,
                'message': 'Session cancelled successfully',
                'session': session.to_dict()
            })
            
        except ValueError as e:
            return jsonify({'success': False, 'message': str(e)}), 400
        except Exception as e:
            return jsonify({'success': False, 'message': f'Error cancelling session: {str(e)}'}), 500
    
    def get_active_session(self) -> Dict[str, Any]:
        """Get user's active session"""
        try:
            user_id = session.get('user_id')
            
            if not user_id:
                return jsonify({'success': False, 'message': 'User not authenticated'}), 401
            
            active_session = self.pomodoro_service.get_active_session(user_id)
            
            if active_session:
                return jsonify({
                    'success': True,
                    'session': active_session.to_dict()
                })
            else:
                return jsonify({
                    'success': True,
                    'session': None,
                    'message': 'No active session'
                })
            
        except Exception as e:
            return jsonify({'success': False, 'message': f'Error getting active session: {str(e)}'}), 500
    
    def get_user_sessions(self) -> Dict[str, Any]:
        """Get user's sessions"""
        try:
            user_id = session.get('user_id')
            limit = request.args.get('limit', 50, type=int)
            
            if not user_id:
                return jsonify({'success': False, 'message': 'User not authenticated'}), 401
            
            sessions = self.pomodoro_service.get_user_sessions(user_id, limit)
            
            return jsonify({
                'success': True,
                'sessions': [session.to_dict() for session in sessions]
            })
            
        except Exception as e:
            return jsonify({'success': False, 'message': f'Error getting sessions: {str(e)}'}), 500
    
    def get_lesson_sessions(self, lesson_id: str) -> Dict[str, Any]:
        """Get sessions for a lesson"""
        try:
            user_id = session.get('user_id')
            
            if not user_id:
                return jsonify({'success': False, 'message': 'User not authenticated'}), 401
            
            sessions = self.pomodoro_service.get_lesson_sessions(user_id, lesson_id)
            
            return jsonify({
                'success': True,
                'sessions': [session.to_dict() for session in sessions]
            })
            
        except Exception as e:
            return jsonify({'success': False, 'message': f'Error getting lesson sessions: {str(e)}'}), 500
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get session statistics"""
        try:
            user_id = session.get('user_id')
            period = request.args.get('period', 'month')  # day, week, month
            
            if not user_id:
                return jsonify({'success': False, 'message': 'User not authenticated'}), 401
            
            from datetime import datetime, timedelta
            
            if period == 'day':
                stats = self.pomodoro_service.get_daily_statistics(user_id)
            elif period == 'week':
                stats = self.pomodoro_service.get_weekly_statistics(user_id)
            else:  # month
                stats = self.pomodoro_service.get_monthly_statistics(user_id)
            
            return jsonify({
                'success': True,
                'statistics': stats
            })
            
        except Exception as e:
            return jsonify({'success': False, 'message': f'Error getting statistics: {str(e)}'}), 500
    
    def get_productivity_insights(self) -> Dict[str, Any]:
        """Get productivity insights"""
        try:
            user_id = session.get('user_id')
            days = request.args.get('days', 30, type=int)
            
            if not user_id:
                return jsonify({'success': False, 'message': 'User not authenticated'}), 401
            
            insights = self.pomodoro_service.get_productivity_insights(user_id, days)
            
            return jsonify({
                'success': True,
                'insights': insights
            })
            
        except Exception as e:
            return jsonify({'success': False, 'message': f'Error getting insights: {str(e)}'}), 500
