from abc import ABC, abstractmethod

class V1AbstractController(ABC):
    """
    Abstract base class for controllers to enforce CRUD operations.
    All methods can accept **kwargs as the second and only arguement
    after self.
    """

    @abstractmethod
    def __init__(self):
        """
        Initializes the controller
        """
        pass