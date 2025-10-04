"""
Pomodoro Dependency Injection Container
Dependency injection configuration for Pomodoro services
"""
from dependency_injector import containers, providers
from app.infrastructure.database.pomodoro_repository import PomodoroRepositoryImpl
from app.application.services.pomodoro_service import PomodoroService
from app.presentation.controllers.pomodoro_controller import PomodoroController

class PomodoroContainer(containers.DeclarativeContainer):
    """Pomodoro dependency injection container"""
    
    # Database
    database = providers.Dependency()
    
    # Repository
    pomodoro_repository = providers.Singleton(
        PomodoroRepositoryImpl,
        database=database
    )
    
    # Service
    pomodoro_service = providers.Singleton(
        PomodoroService,
        pomodoro_repository=pomodoro_repository
    )
    
    # Controller
    pomodoro_controller = providers.Singleton(
        PomodoroController,
        pomodoro_service=pomodoro_service
    )
