from abc import ABC, abstractmethod
from typing import Any, Dict

class V1AbstractController(ABC):
    """
    Abstract base class for controllers to enforce CRUD operations.
    All methods must accept a dictionary as the first argument and support **kwargs.
    """

    @abstractmethod
    def __init__(self):
        """
        Initializes the controller
        """
        pass

    @abstractmethod
    def create(self, data: Dict[str, Any], **kwargs: Any) -> Any:
        """
        Create a new record.
        """
        pass

    @abstractmethod
    def read(self, data: Dict[str, Any], **kwargs: Any) -> Any:
        """
        Read records based on provided filters.
        """
        pass

    @abstractmethod
    def update(self, data: Dict[str, Any], **kwargs: Any) -> Any:
        """
        Update records based on provided data.
        """
        pass

    @abstractmethod
    def delete(self, data: Dict[str, Any], **kwargs: Any) -> Any:
        """
        Delete records based on provided filters.
        """
        pass