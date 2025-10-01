"""
Dependency Injection Container following SOLID principles.
Manages dependencies and provides instances of services.
"""

from typing import Dict, Any, Type, TypeVar, Callable
from abc import ABC, abstractmethod

T = TypeVar('T')


class DIContainer:
    """
    Simple dependency injection container.
    Manages service registration and resolution.
    """
    
    def __init__(self):
        """Initialize the container."""
        self._services: Dict[Type, Any] = {}
        self._factories: Dict[Type, Callable] = {}
        self._singletons: Dict[Type, Any] = {}
    
    def register_singleton(self, interface: Type[T], implementation: Type[T]) -> None:
        """
        Register a singleton service.
        
        Args:
            interface: Interface or abstract class
            implementation: Concrete implementation class
        """
        self._services[interface] = implementation
        self._singletons[interface] = None
    
    def register_transient(self, interface: Type[T], implementation: Type[T]) -> None:
        """
        Register a transient service (new instance each time).
        
        Args:
            interface: Interface or abstract class
            implementation: Concrete implementation class
        """
        self._services[interface] = implementation
    
    def register_factory(self, interface: Type[T], factory: Callable[[], T]) -> None:
        """
        Register a factory function for service creation.
        
        Args:
            interface: Interface or abstract class
            factory: Factory function that creates the service
        """
        self._factories[interface] = factory
    
    def register_instance(self, interface: Type[T], instance: T) -> None:
        """
        Register a specific instance.
        
        Args:
            interface: Interface or abstract class
            instance: Specific instance to use
        """
        self._services[interface] = instance
        self._singletons[interface] = instance
    
    def resolve(self, interface: Type[T]) -> T:
        """
        Resolve a service instance.
        
        Args:
            interface: Interface or abstract class to resolve
            
        Returns:
            Service instance
            
        Raises:
            ValueError: If service is not registered
        """
        # Check if we have a factory
        if interface in self._factories:
            return self._factories[interface]()
        
        # Check if we have a singleton instance
        if interface in self._singletons and self._singletons[interface] is not None:
            return self._singletons[interface]
        
        # Check if we have a registered service
        if interface not in self._services:
            raise ValueError(f"Service {interface.__name__} is not registered")
        
        service = self._services[interface]
        
        # If it's already an instance, return it
        if not isinstance(service, type):
            return service
        
        # Create new instance
        try:
            # Try to get constructor parameters
            import inspect
            sig = inspect.signature(service.__init__)
            params = {}
            
            for param_name, param in sig.parameters.items():
                if param_name == 'self':
                    continue
                
                if param.annotation != inspect.Parameter.empty:
                    params[param_name] = self.resolve(param.annotation)
            
            instance = service(**params)
            
            # Store singleton if needed
            if interface in self._singletons:
                self._singletons[interface] = instance
            
            return instance
            
        except Exception as e:
            raise ValueError(f"Failed to create instance of {service.__name__}: {str(e)}")
    
    def is_registered(self, interface: Type[T]) -> bool:
        """
        Check if a service is registered.
        
        Args:
            interface: Interface or abstract class
            
        Returns:
            True if registered, False otherwise
        """
        return interface in self._services or interface in self._factories


# Global container instance
container = DIContainer()


def configure_services() -> None:
    """
    Configure all services in the dependency injection container.
    This function should be called during application startup.
    """
    # Import here to avoid circular imports
    from ...domain.interfaces.repositories.user_repository import UserRepository
    from ...domain.interfaces.services.user_service import UserService
    from ..database.repositories.user_repository import UserRepositoryImpl
    from ...application.services.user_service import UserServiceImpl
    
    # Import Lesson domain
    from ...domain.interfaces.repositories.lesson_repository import LessonRepository
    from ...domain.interfaces.services.lesson_service import LessonService
    from ..database.repositories.lesson_repository import LessonRepositoryImpl
    from ...application.services.lesson_service import LessonServiceImpl
    
    # Import Note domain
    from ...domain.interfaces.repositories.note_repository import NoteRepository
    from ...domain.interfaces.services.note_service import NoteService
    from ..database.repositories.note_repository import NoteRepositoryImpl
    from ...application.services.note_service import NoteServiceImpl
    
    # Import Task domain
    from ...domain.interfaces.repositories.task_repository import TaskRepository
    from ...domain.interfaces.services.task_service import TaskService
    from ..database.repositories.task_repository import TaskRepositoryImpl
    from ...application.services.task_service import TaskServiceImpl
    
    # Register repositories
    container.register_singleton(UserRepository, UserRepositoryImpl)
    container.register_singleton(LessonRepository, LessonRepositoryImpl)
    container.register_singleton(NoteRepository, NoteRepositoryImpl)
    container.register_singleton(TaskRepository, TaskRepositoryImpl)
    
    # Register services
    container.register_singleton(UserService, UserServiceImpl)
    container.register_singleton(LessonService, LessonServiceImpl)
    container.register_singleton(NoteService, NoteServiceImpl)
    container.register_singleton(TaskService, TaskServiceImpl)
    
    # Register other services as needed
    # container.register_singleton(TaskRepository, TaskRepositoryImpl)
    # container.register_singleton(TaskService, TaskServiceImpl)
    # container.register_singleton(AuthService, AuthServiceImpl)


def get_service(interface: Type[T]) -> T:
    """
    Get a service instance from the container.
    
    Args:
        interface: Interface or abstract class
        
    Returns:
        Service instance
    """
    return container.resolve(interface)
