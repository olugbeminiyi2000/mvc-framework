from models.error.v1_Error import InvalidKeyValueError
from models.v1_Model import V1Model
import unittest
from unittest.mock import patch, mock_open



"""Test that the rule function must return a boolean value"""
def positive(x):
    return x > 0

def invalid_rule(x):
    return x

"""Test that ValueError is raised for rules with more than one argument"""
def invalid_rule_2(x, y):
    return x > y

"""Test that the rule function must return a boolean value"""
class Height:
    def __init__(self, height: float):
        self.height = height

def check_object_height(height_object: Height) -> bool:
    return height_object.height > 6.0
        
height_1 = Height(7.2)

"""Test that validation works if rule passes"""
def positive_2(x):
    return x > 0

class TestV1Model(unittest.TestCase):

    def test_initialization(self):
        """Test initialization and data loading from file"""
        model = V1Model()
        self.assertEqual(model.get_data(), {'username': 'Honeybadger', 'Guardian': 'mother'})
        
    def test_register_rule_invalid_field_type(self):
        """Test that ValueError is raised for non-string field"""
        model = V1Model()
        with self.assertRaises(ValueError):
            model.register_rule(123, lambda x: x > 0, "must be greater than 0", 2)
    
    def test_register_rule_invalid_message_type(self):
        """Test that ValueError is raised for non-string message"""
        model = V1Model()
        with self.assertRaises(ValueError):
            model.register_rule("age", lambda x: x > 0, 123, 20)
    
    def test_register_rule_invalid_rule_type(self):
        """Test that ValueError is raised for non-callable rule"""
        model = V1Model()
        with self.assertRaises(ValueError):
            model.register_rule("age", 123, "must be greater than 0", 80)
    
    def test_register_rule_invalid_rule_argument_count(self):
        """Test that ValueError is raised for rules with more than one argument"""
        model = V1Model()
        with self.assertRaises(ValueError):
            model.register_rule("age", invalid_rule_2, "must be greater than 0", 43)

    def test_rule_return_type_is_bool(self):
        """Test that the rule function must return a boolean value"""
        model = V1Model()
        # Register a valid rule
        model.register_rule("age", positive, "must be greater than 0", 67)
        try:
            model.validate("age", 5)
        except ValueError:
            self.fail("Valid rule raised ValueError unexpectedly")

        with self.assertRaises(ValueError):
            # Register an invalid rule
            model.register_rule("age", invalid_rule, "must be greater than 0", "34")

    def test_rule_object_example_value(self):
        """Test that the rule function must return a boolean value"""
        model = V1Model()
        # Register a valid rule
        model.register_rule("height", check_object_height, "height must be greater than 6.0", height_1)

        # validate rule
        model.validate("height", height_1)
    
    def test_validate_success(self):
        """Test that validation works if rule passes"""
        model = V1Model()
        model.register_rule("age", positive_2, "must be greater than 0", 23)
        model.validate("age", 5)
    
    def test_validate_fail(self):
        """Test that validation raises ValueError if rule fails"""
        model = V1Model()
        model.register_rule("age", positive_2, "must be greater than 0", 21)
        with self.assertRaises(ValueError):
            model.validate("age", -1)
    
    def test_write_data_to_file(self):
        """Test writing data to file"""
        model = V1Model()
        result = model.add_key_value("first_name", "Emmanuel")
        self.assertTrue(result)

    def test_add_key_value_success(self):
        """Test adding key-value pair successfully"""
        model = V1Model()
        result = model.add_key_value("username", "Honeybadger")
        self.assertTrue(result)
        self.assertEqual(model.get_data(), {"username": "Honeybadger"})
    
    def test_add_key_value_invalid_key(self):
        """Test that InvalidKeyValueError is raised for invalid key"""
        model = V1Model()
        with self.assertRaises(ValueError):
            model.add_key_value("aek2345£@", "%63572")
        with self.assertRaises(ValueError):
            model.add_key_value(None, "aek2345£")
    
    def test_add_key_value_invalid_value(self):
        """Test that InvalidKeyValueError is raised for invalid value"""
        model = V1Model()
        with self.assertRaises(ValueError):
            model.add_key_value("last_name", "")
        with self.assertRaises(ValueError):
            model.add_key_value("last_name", None)
    
    def test_get_key_value_success(self):
        """Test retrieving a key-value pair"""
        model = V1Model()
        result = model.add_key_value("Guardian", "mother")
        self.assertTrue(result)
        value = model.get_key_value("Guardian")
        self.assertEqual(value, "mother")
    
    def test_get_key_value_not_found(self):
        """Test that None is returned if key is not found"""
        model = V1Model()
        value = model.get_key_value("next_of_kin")
        self.assertIsNone(value)
    
    def test_delete_key_value_success(self):
        """Test deleting a key-value pair"""
        model = V1Model()
        result = model.add_key_value("sex", "Female")
        self.assertTrue(result)
        result = model.delete_key_value("sex")
        self.assertTrue(result)
        self.assertNotIn("sex", model.get_data())
    
    def test_delete_key_value_not_found(self):
        """Test that InvalidKeyValueError is raised when key is not found"""
        model = V1Model()
        with self.assertRaises(InvalidKeyValueError):
            model.delete_key_value("gender")

    def test_update_key_value_success(self):
        """Test updating key-value pairs"""
        model = V1Model()
        result = model.add_key_value("gender", "female")
        self.assertTrue(result)
        model.update_key_value(gender="male")
        self.assertEqual(model.get_data(), {'username': 'Honeybadger', 'Guardian': 'mother', 'gender': 'male'})

    def test_update_key_value_invalid_key(self):
        """Test that InvalidKeyValueError is raised when updating no dictionary pair."""
        model = V1Model()
        with self.assertRaises(InvalidKeyValueError):
            model.update_key_value()


if __name__ == "__main__":
    unittest.main()
