from controllers.v1_Controller import V1BaseController
from models.error.v1_Error import DefaultError
from models.transaction.v1_Transaction import Transactions
from models.v1_Model import V1Model
import unittest


class TestV1BaseController(unittest.TestCase):
    """
    Unit tests for the V1BaseController class to validate its CRUD operations.
    """

    def setUp(self) -> None:
        """
        Sets up the test environment by initializing the model, transaction, and controller objects.
        """
        self.model = V1Model()
        self.transaction = Transactions(self.model)
        self.controller = V1BaseController(self.transaction)

    def test_create_succesful(self) -> None:
        """
        Test case to validate successful creation of data.
        """
        data = {"siblings": 5, "blood_group": "AB"}
        result = self.controller.create(data)
        self.assertTrue(result)

    def test_create_empty_data(self) -> None:
        """
        Test case to verify that attempting to create with empty data raises a ValueError.
        """
        with self.assertRaises(ValueError):
            self.controller.create({})

    def test_create_unsuccessful(self) -> None:
        """
        Test case to ensure DefaultError is raised for creating data that already exists.
        """
        data = {"siblings": 5, "blood_group": "AB"}
        with self.assertRaises(DefaultError):
            self.controller.create(data)

    def test_create_invalid_data_type_as_arg(self) -> None:
        """
        Test case to validate that TypeError is raised for invalid data types.
        """
        with self.assertRaises(TypeError):
            self.controller.create("invalid_data_type")

    def test_read_success(self) -> None:
        """
        Test case to validate successful retrieval of data using valid filters.
        """
        filters = ["siblings"]
        result = self.controller.read(filters)
        self.assertEqual(result, {'university': 'African Leadership University', "siblings": 5})

    def test_read_failure_unknown_data(self) -> None:
        """
        Test case to ensure all Exception (default, key) Error is raised raised for reading unknown data.
        """
        filters = ["parent_status"]
        with self.assertRaises(Exception):
            self.controller.read(filters)

    def test_read_empty_filters(self) -> None:
        """
        Test case to verify that attempting to read with empty filters raises a ValueError.
        """
        with self.assertRaises(ValueError):
            self.controller.read([])

    def test_read_invalid_data_type_in_filters(self) -> None:
        """
        Test case to validate that ValueError is raised when filters contain invalid data types.
        """
        with self.assertRaises(ValueError):
            self.controller.read(["siblings", 240, {}])

    def test_read_invalid_filters_data_type_as_arg(self) -> None:
        """
        Test case to validate that TypeError is raised for invalid filter arguments.
        """
        with self.assertRaises(TypeError):
            self.controller.read("invalid_filter")

    def test_update_success(self) -> None:
        """
        Test case to validate successful update of existing data.
        """
        data = {"siblings": 25}
        result = self.controller.update(data)
        self.assertTrue(result)

    def test_update_empty_data(self) -> None:
        """
        Test case to verify that attempting to update with empty data raises a ValueError.
        """
        with self.assertRaises(ValueError):
            self.controller.update({})

    def test_update_invalid_data_as_arg(self) -> None:
        """
        Test case to validate that TypeError is raised for invalid data types during update.
        """
        with self.assertRaises(TypeError):
            self.controller.update("invalid_data_type")

    def test_delete_success(self) -> None:
        """
        Test case to validate successful deletion of data using valid filters.
        """
        filters = ["blood_group"]
        result = self.controller.delete(filters)
        self.assertTrue(result)

    def test_delete_unsuccessful(self) -> None:
        """
        Test case to ensure Exception (default, key) is raised for attempting to delete unknown data.
        """
        filters = ["parent_status"]
        with self.assertRaises(Exception):
            self.controller.delete(filters)

    def test_delete_empty_filters(self) -> None:
        """
        Test case to verify that attempting to delete with empty filters raises a ValueError.
        """
        with self.assertRaises(ValueError):
            self.controller.delete([])

    def test_delete_invalid_filters_as_arg(self) -> None:
        """
        Test case to validate that TypeError is raised for invalid filter arguments during deletion.
        """
        with self.assertRaises(TypeError):
            self.controller.delete("invalid_filter_data_type")


if __name__ == '__main__':
    unittest.main()
