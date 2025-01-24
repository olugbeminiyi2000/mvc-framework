from abc import ABC, abstractmethod

class V1View(ABC):
    @abstractmethod
    def __init__(self):
        """
        Initializes the view
        """
        pass