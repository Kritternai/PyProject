"""
Services Package
Contains all business logic services for the application
"""

# Import services from dedicated service files
from .pomodoro_statistics_service import PomodoroStatisticsService

# For backwards compatibility, provide access to main services
# This is a temporary solution to avoid circular import issues
def _lazy_import_main_services():
    """Lazy import to get services from main services.py file"""
    try:
        import importlib.util
        import os
        
        # Get path to main services.py
        services_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'services.py')
        
        # Load the module
        spec = importlib.util.spec_from_file_location("main_services", services_path)
        main_services = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(main_services)
        
        return main_services
    except Exception as e:
        print(f"Warning: Could not load main services: {e}")
        return None

# Create proxy classes that delegate to the main services
class UserService:
    def __new__(cls):
        main_services = _lazy_import_main_services()
        if main_services and hasattr(main_services, 'UserService'):
            return main_services.UserService()
        else:
            raise ImportError("Could not load UserService from main services")

class LessonService:
    def __new__(cls):
        main_services = _lazy_import_main_services()
        if main_services and hasattr(main_services, 'LessonService'):
            return main_services.LessonService()
        else:
            raise ImportError("Could not load LessonService from main services")

class NoteService:
    def __new__(cls):
        main_services = _lazy_import_main_services()
        if main_services and hasattr(main_services, 'NoteService'):
            return main_services.NoteService()
        else:
            raise ImportError("Could not load NoteService from main services")

class TaskService:
    def __new__(cls):
        main_services = _lazy_import_main_services()
        if main_services and hasattr(main_services, 'TaskService'):
            return main_services.TaskService()
        else:
            raise ImportError("Could not load TaskService from main services")

class PomodoroSessionService:
    def __new__(cls):
        main_services = _lazy_import_main_services()
        if main_services and hasattr(main_services, 'PomodoroSessionService'):
            return main_services.PomodoroSessionService()
        else:
            raise ImportError("Could not load PomodoroSessionService from main services")

class PomodoroService:
    def __new__(cls):
        main_services = _lazy_import_main_services()
        if main_services and hasattr(main_services, 'PomodoroService'):
            return main_services.PomodoroService()
        else:
            raise ImportError("Could not load PomodoroService from main services")

class PomodoroStatisticsServiceWrapper:
    def __new__(cls):
        main_services = _lazy_import_main_services()
        if main_services and hasattr(main_services, 'PomodoroStatisticsServiceWrapper'):
            return main_services.PomodoroStatisticsServiceWrapper()
        else:
            raise ImportError("Could not load PomodoroStatisticsServiceWrapper from main services")

__all__ = [
    'PomodoroStatisticsService',
    'UserService',
    'LessonService', 
    'NoteService',
    'TaskService',
    'PomodoroSessionService',
    'PomodoroService',
    'PomodoroStatisticsServiceWrapper'
]