import inspect
import os
import pickle


class V1Router:
    DEFAULT_FILE_PATH = "router_state.pkl"

    def __init__(self):
        self.file_path = self.DEFAULT_FILE_PATH
        self.routes = self._load_or_initialize_routes()

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
        # TODO create a default controller method that returns a information of choice.
        return {}

    def validate_controller_action(self, controller_class, action_name):
        action_method = getattr(controller_class(), action_name)
        signature = inspect.signature(action_method)
        parameters = signature.parameters

        if "data" not in parameters:
            raise ValueError(f"Controller action '{action_name}' must accept 'data' argument.")

        required_params = [
            param for param, param_info in parameters.items()
            if param_info.default == inspect.Parameter.empty
        ]
        if len(required_params) > 1:
            raise ValueError(
                f"Controller action '{action_name}' must only require 'data' as a non-optional argument, "
                f"found: {', '.join(required_params)}."
            )

        for param, param_info in parameters.items():
            if param != "data" and param_info.default == inspect.Parameter.empty:
                raise ValueError(
                    f"Controller action '{action_name}' cannot require arguments other than 'data'. "
                    f"Please pass additional parameters as **kwargs."
                )

    def add_route(self, route, controller_class, action_name):
        self.validate_controller_action(controller_class, action_name)
        self.routes[route] = getattr(controller_class(), action_name)
        self._atomic_save()

    def route(self, url: str, method: str = "GET", data=None, **kwargs):
        if url in self.routes:
            controller_action = self.routes[url]
            if method.upper() in {"GET", "POST", "PUT", "DELETE"}:
                return controller_action(data, **kwargs)
        else:
            raise ValueError(f"Route '{url}' not found.")

    def clear_routes(self):
        """Clears all routes and saves the empty state."""
        self.routes = {}
        self._atomic_save()
