from abc import ABC, abstractmethod

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