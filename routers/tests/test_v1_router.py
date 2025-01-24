import os
import pickle
import unittest
from routers.v1_Router import V1Router
from controllers.v1_Controller import V1AbstractController


class StudentController(V1AbstractController):
    def __init__(self):
        super().__init__()

    def search_student(self, **kwargs):
        return {"message": "Searched student", "kwargs": kwargs}

    def add_student(self, **kwargs):
        return {"message": "Added student", "kwargs": kwargs}


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

    def test_add_route_with_valid_controller(self):
        """Test adding a valid route with a valid controller."""
        self.router.add_route("/search", StudentController, "search_student")
        self.assertIn("/search", self.router.routes)

    def test_add_route_with_invalid_controller(self):
        """Test adding a route with a controller not inheriting V1AbstractController."""
        with self.assertRaises(TypeError):
            self.router.add_route("/all_item", CartController, "list_items")

    def test_add_route_with_invalid_action_signature(self):
        """Test adding a route with an invalid action signature."""
        class InvalidSignatureController(V1AbstractController):
            def __init__(self):
                super().__init__()

            def get_location(self, street, state):
                pass

        with self.assertRaises(ValueError):
            self.router.add_route("/find_loc", InvalidSignatureController, "get_location")


    def test_route_execution_with_valid_url(self):
        """Test route execution with a valid URL."""
        self.router.add_route("/add", StudentController, "add_student")
        response = self.router.route("/add", name="Obolo Emmanuel Oluwapelumi")
        self.assertEqual(response["message"], "Added student")
        self.assertEqual(response["kwargs"], {"name": "Obolo Emmanuel Oluwapelumi"})

    def test_route_execution_with_kwargs(self):
        """Test route execution with additional kwargs."""
        self.router.add_route("/search", StudentController, "search_student")
        response = self.router.route("/search", name="Obolo Emmanuel Oluwapelumi", intake="January")
        self.assertEqual(response["kwargs"], {"name": "Obolo Emmanuel Oluwapelumi", "intake": "January"})

    def test_route_execution_with_invalid_url(self):
        """Test route execution with an invalid URL."""
        with self.assertRaises(ValueError):
            self.router.route("/invalid_url", name="Unknown", message="404 not found")

    def test_clear_routes(self):
        """Test clearing all routes."""
        self.router.add_route("/add_student", StudentController, "add_student")
        self.router.clear_routes()
        self.assertEqual(self.router.routes, {})

    def test_persistence_of_routes(self):
        """Test that routes are persisted between router instances."""
        self.router.add_route("/search_student", StudentController, "search_student")
        self.assertIn("/search_student", self.router.routes)

        # Create a new router instance and check persistence
        new_router = V1Router(file_path=self.router.file_path)
        self.assertIn("/search_student", new_router.routes)


if __name__ == "__main__":
    unittest.main()
