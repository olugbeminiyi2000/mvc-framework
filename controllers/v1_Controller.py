from abc import ABC, abstractmethod

class V1AbstractController(ABC):
    """
    Abstract base class for controllers to enforce their initialization.
    while still giving user's the flexiblity to create their own crud operations
    """

    @abstractmethod
    def __init__(self):
        """
        Initializes the controller
        """
        pass