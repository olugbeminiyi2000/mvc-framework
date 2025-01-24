import os
import pickle
import unittest
from routers.v1_Router import V1Router
from controllers.v1_Controller import V1AbstractController
from views.v1_View import V1BaseView


class StudentController(V1AbstractController):
    def __init__(self):
        super().__init__()

    def search_student(self, **kwargs):
        return {"message": "Searched student", "kwargs": kwargs}

    def add_student(self, **kwargs):
        return {"message": "Added student", "kwargs": kwargs}


class StudentView(V1BaseView):
    def __init__(self, **kwargs):
        self.data = kwargs

    def render(self, **kwargs):
        return f"Rendered: {kwargs}"


class BadController(V1AbstractController):
    pass


class CartController:
    def list_items(self, **kwargs):
        return "Invalid action"


class TestV1Router(unittest.TestCase):
    def setUp(self):
        """Set up the router and clean up any previous state."""
        self.router = V1Router()
        self.router.file_path = "test_router_state.pkl"
        if os.path.exists(self.router.file_path):
            os.remove(self.router.file_path)

    def tearDown(self):
        """Clean up the state file after tests."""
        if os.path.exists(self.router.file_path):
            os.remove(self.router.file_path)

    def test_abstract_methods_not_implemented(self):
        """Test user-defined controller without abstract methods not implemented."""
        with self.assertRaises(TypeError):
            BadController()

    def test_initialization_with_no_state(self):
        """Test router initializes with an empty routes dictionary when no state file exists."""
        self.assertEqual(self.router.routes, {})

    def test_initialization_with_saved_state(self):
        """Test router loads the saved state correctly."""
        routes = {"/create/design/": "create_design"}
        with open(self.router.file_path, "wb") as f:
            pickle.dump(routes, f)

        router = V1Router(file_path=self.router.file_path)
        self.assertEqual(router.routes, routes)

    def test_add_route_with_valid_controller_and_view(self):
        """Test adding a valid route with a valid controller and view."""
        self.router.add_route("/search", StudentController, "search_student", StudentView)
        self.assertIn("/search", self.router.routes)

    def test_add_route_with_invalid_controller(self):
        """Test adding a route with a controller not inheriting V1AbstractController."""
        with self.assertRaises(TypeError):
            self.router.add_route("/all_item", CartController, "list_items", StudentView)

    def test_add_route_with_invalid_view(self):
        """Test adding a route with a view not inheriting V1BaseView."""
        class InvalidView:
            pass

        with self.assertRaises(TypeError):
            self.router.add_route("/search", StudentController, "search_student", InvalidView)

    def test_route_execution_with_valid_url_and_view(self):
        """Test route execution with a valid URL and rendering via the view."""
        self.router.add_route("/add", StudentController, "add_student", StudentView)
        response = self.router.route("/add", name="Obolo Emmanuel Oluwapelumi")
        self.assertEqual(response, "Rendered: {'controller_response': {'message': 'Added student', 'kwargs': {'name': 'Obolo Emmanuel Oluwapelumi'}}}")

    def test_route_execution_with_invalid_url(self):
        """Test route execution with an invalid URL."""
        with self.assertRaises(ValueError):
            self.router.route("/invalid_url", name="Unknown", message="404 not found")

    def test_clear_routes(self):
        """Test clearing all routes."""
        self.router.add_route("/add_student", StudentController, "add_student", StudentView)
        self.router.clear_routes()
        self.assertEqual(self.router.routes, {})

    def test_persistence_of_routes(self):
        """Test that routes are persisted between router instances."""
        self.router.add_route("/search_student", StudentController, "search_student", StudentView)
        self.assertIn("/search_student", self.router.routes)

        # Create a new router instance and check persistence
        new_router = V1Router(file_path=self.router.file_path)
        self.assertIn("/search_student", new_router.routes)


if __name__ == "__main__":
    unittest.main()
