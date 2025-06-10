from abc import ABC, abstractmethod
from views.v1_Render import render_json, render_template


class V1BaseView(ABC):
    # Centralized Content-Type definitions
    CONTENT_TYPES = {
        "HTML": "text/html",
        "JSON": "application/json",
        "PLAIN": "text/plain",
        "XML": "application/xml",
        "PDF": "application/pdf",
        # Add more as needed
    }
    
    content_type: str =  "text/html"

    @abstractmethod
    def __init__(self):
        pass # Subclasses must implement this, but no specific content_type assignment here.

    @abstractmethod
    def render(self, **kwargs) -> str:
        """Abstract method to render the data returned by the controller."""
        pass

    @staticmethod
    def render_template(template_name: str, data: dict) -> str:
        """Utility function to render templates."""
        return render_template(template_name, data)

    @staticmethod
    def render_json(data: dict) -> str:
        """Utility function to render data as JSON."""
        return render_json(data)
