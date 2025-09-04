"""
Value Object interface following Domain-Driven Design principles.
"""

from abc import ABC, abstractmethod
from typing import Any


class ValueObject(ABC):
    """
    Base class for value objects.
    Value objects are immutable and defined by their attributes.
    """
    
    @abstractmethod
    def __eq__(self, other: Any) -> bool:
        """Check equality with another value object."""
        pass
    
    @abstractmethod
    def __hash__(self) -> int:
        """Get hash value for the value object."""
        pass
    
    def __ne__(self, other: Any) -> bool:
        """Check inequality with another value object."""
        return not self.__eq__(other)
