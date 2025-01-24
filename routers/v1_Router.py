from controllers.v1_Controller import V1AbstractController
import inspect
import os
import pickle
from typing import Any, Dict, Optional, Tuple, Type
from views.v1_View import V1BaseView

class V1Router:
    DEFAULT_FILE_PATH = "router_state.pkl"

    def __init__(self, file_path: Optional[str] = None):
        self.file_path = file_path or self.DEFAULT_FILE_PATH
        self.routes: Dict[str, Tuple[Any, str, Type[V1BaseView]]] = self._load_or_initialize_routes()

    def _atomic_save(self):
        """Saves the Router object state atomically to the file."""
        temp_file = self.file_path + ".tmp"
        try:
            with open(temp_file, "wb") as f:
                pickle.dump(self.routes, f)
            os.replace(temp_file, self.file_path)
        except Exception as e:
            if os.path.exists(temp_file):
                os.remove(temp_file)
            raise RuntimeError(f"Failed to save Router state: {e}")

    def _load_or_initialize_routes(self):
        """Loads the Router state from file or initializes a new one if the file does not exist."""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "rb") as f:
                    return pickle.load(f)
            except Exception as e:
                raise RuntimeError(f"Failed to load Router state from {self.file_path}: {e}")
        return {}

    def validate_controller_action(self, controller_class: Any, action_name: str):
        """
        Validates that the controller and action conform to the required structure.

        Args:
            controller_class (Any): The controller class to validate.
            action_name (str): The name of the action to validate.

        Raises:
            TypeError: If the controller does not inherit from V1AbstractController.
            ValueError: If the action does not meet the required argument structure.
        """
        if not issubclass(controller_class, V1AbstractController):
            raise TypeError(
                f"The controller '{controller_class.__name__}' must inherit from 'V1AbstractController'."
            )

        action_method = getattr(controller_class, action_name, None)
        if action_method is None:
            raise ValueError(f"Action '{action_name}' not found in controller '{controller_class.__name__}'.")

        # Get the signature of the action method
        signature = inspect.signature(action_method)
        parameters = signature.parameters

        # Exclude 'self' from the parameter list
        filtered_params = [
            (name, param) for name, param in parameters.items() if name != "self"
        ]

        # Ensure that all arguments after 'self' are **kwargs (no required arguments)
        for name, param in filtered_params:
            if param.kind != inspect.Parameter.VAR_KEYWORD:
                raise ValueError(
                    f"Controller action '{action_name}' must only accept 'self' and **kwargs for additional arguments. "
                    f"Invalid parameter: '{name}'."
                )

    def add_route(self, route: str, controller_class: Any, action_name: str, view_class: V1BaseView):
        """
        Adds a route to the router.

        Args:
            route (str): The route URL.
            controller_class (Any): The controller class.
            action_name (str): The name of the action method.
            view_class (V1BaseView): The view class to render the result.

        Raises:
            RuntimeError: If the route cannot be added due to validation errors.
        """
        self.validate_controller_action(controller_class, action_name)

        # Ensure the view is a subclass of V1BaseView
        if not issubclass(view_class, V1BaseView):
            raise TypeError(f"View class '{view_class.__name__}' must inherit from 'V1BaseView'.")

        # Store the route, controller, action, and view
        self.routes[route] = (controller_class, action_name, view_class)
        self._atomic_save()

    def route(self, url: str, method: str = "GET", **kwargs: Any):
        """
        Routes a request to the appropriate controller action and renders the result with the associated view.

        Args:
            url (str): The URL of the route.
            method (str): The HTTP method (default: "GET").
            **kwargs (Any): Data to pass to the action as **kwargs.

        Returns:
            str: The final result rendered by the view.

        Raises:
            ValueError: If the route is not found.
        """
        if url in self.routes:
            controller_class, action_name, view_class = self.routes[url]
            controller_instance = controller_class()
            action_method = getattr(controller_instance, action_name)

            if method.upper() in {"GET", "POST", "PUT", "DELETE", "PATCH"}:
                controller_response = action_method(**kwargs)
            else:
                raise ValueError(f"HTTP method '{method.upper()}' not supported.")

            # Render the controller response using the associated view
            view_instance = view_class()
            return view_instance.render(controller_response=controller_response)
        else:
            raise ValueError(f"Route '{url}' not found.")

    def clear_routes(self):
        """Clears all routes and saves the empty state."""
        self.routes = {}
        self._atomic_save()