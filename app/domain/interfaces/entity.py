"""
Base entity interface following Domain-Driven Design principles.
"""

from abc import ABC, abstractmethod
from typing import Any


class Entity(ABC):
    """
    Base class for domain entities.
    Entities have identity and lifecycle.
    """
    
    @property
    @abstractmethod
    def id(self) -> str:
        """Get entity ID."""
        pass
    
    def __eq__(self, other: Any) -> bool:
        """Check equality with another entity."""
        if not isinstance(other, self.__class__):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        """Get hash value for the entity."""
        return hash(self.id)
    
    def __ne__(self, other: Any) -> bool:
        """Check inequality with another entity."""
        return not self.__eq__(other)
