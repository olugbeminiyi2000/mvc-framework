import json
from json.decoder import JSONDecodeError
import logging
from models.error.v1_Error import InvalidKeyValueError
from models.validation.v1_Validation import CheckAllValidation, V1Validation
import os
import pickle
from typing import Callable, Dict, Any

# Set up basic logging configuration
logging.basicConfig(filename='error.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')


class V1Model:
    """
    A model class that handles reading, writing, and validating data stored in a JSON file.
    Supports registering and validating rules for key-value pairs.
    """
    DEFAULT_FILE_PATH = "model_state.pkl"

    def __init__(self, file_path="v1_model.json"):
        """
        Initializes the model by reading existing data from the file and initializing validation rules.
        """
        self.file_path = self.DEFAULT_FILE_PATH
        self.json_file_path = file_path
        self.read_data_from_file()
        self._validation_rules: Dict[str, Dict[str, Any]] = self._load_or_initialize_custom_validation_rules()

    def _atomic_save(self) -> None:
        """
        Saves the Model object state atomically to the file to ensure data integrity.
        This involves writing to a temporary file first and then replacing the original file.
        
        Raises:
            RuntimeError: If the save operation fails.
        """
        temp_file = self.file_path + ".tmp"
        try:
            with open(temp_file, "wb") as f:
                pickle.dump(self._validation_rules, f)
            os.replace(temp_file, self.file_path)
        except Exception as e:
            if os.path.exists(temp_file):
                os.remove(temp_file)
            raise RuntimeError(f"Failed to save Model state: {e}")

    def _load_or_initialize_custom_validation_rules(self) -> Dict[str, Any]:
        """
        Loads the custom validation rules from the file if it exists.
        If the file does not exist, initializes an empty dictionary.

        Returns:
            Dict[str, Any]: The loaded or initialized validation rules.

        Raises:
            RuntimeError: If the load operation fails.
        """
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "rb") as f:
                    return pickle.load(f)
            except Exception as e:
                raise RuntimeError(f"Failed to load Model state from {self.file_path}: {e}")
        return {}
    
    def register_rule(self, field: str, rule: Callable[[Any], bool], message: str, example_value: Any) -> None:
        """
        Registers a validation rule for a specific field.
        
        Parameters:
            field (str): The field name to validate.
            rule (Callable[[Any], bool]): The validation function.
            message (str): The error message if validation fails.
            example_value (Any): A sample value to validate.
            
        Raises:
            ValueError: If any validation parameters are invalid.
        """
        if not isinstance(field, str):
            raise ValueError(f"{field} must be of type string.")
        if not isinstance(message, str):
            raise ValueError(f"Message for rule {rule} must be a string.")
        if not callable(rule):
            raise ValueError(f"{rule} should be a callable i.e. a function.")
        if rule.__code__.co_argcount != 1:
            raise ValueError(f"Function {rule} should have exactly one argument (the value to validate).")

        field_value = self._generate_example_value(example_value)

        result = rule(field_value)
        if not isinstance(result, bool):
            raise ValueError(f"Rule function {rule} must return a boolean value, but returned {type(result)}.")

        if field not in self._validation_rules:
            self._validation_rules[field] = {"messages": [], "rules": []}

        self._validation_rules[field]["messages"].append(message)
        self._validation_rules[field]["rules"].append(rule)
        self._atomic_save()

    def _generate_example_value(self, example_value: Any) -> Any:
        """
        Generates a default value based on the class of the example value.
        
        Parameters:
            example_value (Any): The sample value to determine the type for default generation.
        
        Returns:
            Any: A default example value of the same type as example_value.
            
        Raises:
            ValueError: If the argument type is unsupported.
        """
        if isinstance(example_value, int):
            return 42
        elif isinstance(example_value, str):
            return "example"
        elif isinstance(example_value, float):
            return 3.14
        elif isinstance(example_value, bool):
            return True
        elif isinstance(example_value, list):
            return [1, 2, 3]
        elif isinstance(example_value, dict):
            return {"key": "value"}
        elif isinstance(example_value, set):
            return {1, 2, 3}
        elif isinstance(example_value, tuple):
            return (1, 2, 3)
        elif hasattr(example_value, "__class__"):
            if callable(example_value):
                try:
                    return example_value()
                except TypeError:
                    raise ValueError(f"Class {example_value} cannot be instantiated without arguments.")
            return example_value
        else:
            raise ValueError(f"Unsupported argument type: {example_value}")

    def delete_rule(self, field: str) -> None:
        """
        Deletes a validation rule for a specific field.
        
        Parameters:
            field (str): The field name to remove validation rules for.
        
        Raises:
            ValueError: If the field does not exist in the validation rules.
        """
        if field not in self._validation_rules:
            raise ValueError(f"Field '{field}' does not exist in the validation rules to delete.")
        del self._validation_rules[field]
        self._atomic_save()

    def validate(self, field: str, value: Any) -> None:
        """
        Validates a value for a specific field against registered rules.
        
        Parameters:
            field (str): The field name to validate.
            value (Any): The value to validate.
        
        Raises:
            ValueError: If any validation rule fails.
        """
        if field in self._validation_rules:
            for rule, message in zip(self._validation_rules[field]["rules"], self._validation_rules[field]["messages"]):
                if not rule(value):
                    raise ValueError(f"Validation failed for '{field}': {value}, message: {message}")

    def read_data_from_file(self) -> None:
        """
        Reads data from a JSON file and stores it in memory.
        If the file does not exist or is invalid, an empty dictionary is used.
        """
        try:
            with open(self.json_file_path, mode='r', encoding="utf-8") as fp:
                self._data = json.load(fp)
        except FileNotFoundError:
            self._data = {}
        except JSONDecodeError:
            self._data = {}

    def write_data_to_file(self) -> None:
        """
        Writes the current in-memory data to a JSON file.
        A temporary file is used to avoid data corruption during the writing process.
        """
        try:
            temp_file = "v1_model.tmp"
            with open(temp_file, mode='w', encoding="utf-8") as fp:
                json.dump(self._data, fp)
            os.replace(temp_file, self.json_file_path)
        except Exception as e:
            logging.error("Failed to write data: %s", e)

    def get_data(self) -> Dict[str, Any]:
        """
        Returns a copy of the current in-memory data.
        
        Returns:
            Dict[str, Any]: The data stored in memory.
        """
        return self._data.copy()

    def overwrite_data(self, allowNone: bool = False, confirm: bool = False, **overwrite_data: Dict[str, Any]) -> bool:
        """
        Overwrites the current data with new data after validation.
        
        Parameters:
            allowNone (bool): If False, None values are not allowed in the overwrite data.
            confirm (bool): If True, user confirmation is required before overwriting.
            overwrite_data (Dict[str, Any]): The new data to overwrite with.
        
        Returns:
            bool: True if the data was successfully overwritten, False if not.
        """
        for field in overwrite_data.keys():
            CheckAllValidation.check_all_key_validation(field, self._data)

        for value in overwrite_data.values():
            CheckAllValidation.check_all_value_validation(value, allowNone)
            data_type = V1Validation.identify_data_type(value)
            if data_type == "email":
                CheckAllValidation.check_valid_email(value)
            elif data_type == "phone":
                CheckAllValidation.check_valid_phone_number(value)
            elif data_type == "url":
                CheckAllValidation.check_valid_url(value)

        for field, value in overwrite_data.items():
            self.validate(field, value)

        if confirm:
            confirmation = input("Do you want to overwrite your existing data yes/no? ")
            if confirmation.lower() != "yes":
                return False
        self._data = overwrite_data or {}
        self.write_data_to_file()
        return True

    def add_key_value(self, key_data: str, value_data: Any, allowNone: bool = False, persists: bool = True) -> bool:
        """
        Adds a new key-value pair to the data after validation.
        
        Parameters:
            key_data (str): The key to add.
            value_data (Any): The value associated with the key.
            allowNone (bool): If False, None values are not allowed.
            persists (bool): If True, the data is written to the file.
        
        Returns:
            bool: True if the key-value pair was added successfully, False if not.
        """
        CheckAllValidation.check_all_key_validation(key_data, self._data)
        CheckAllValidation.check_all_value_validation(value_data, allowNone)

        data_type = V1Validation.identify_data_type(value_data)
        if data_type == "email":
            CheckAllValidation.check_valid_email(value_data)
        elif data_type == "phone":
            CheckAllValidation.check_valid_phone_number(value_data)
        elif data_type == "url":
            CheckAllValidation.check_valid_url(value_data)

        self.validate(key_data, value_data)

        try:
            if persists:
                self._data[key_data] = value_data
                self.write_data_to_file()
            return True
        except Exception as e:
            logging.error("Failed to add key '%s' with value '%s': %s", key_data, value_data, e)
            return False

    def update_key_value(self, allowNone: bool = False, persists: bool = True, **update_dict: Dict[str, Any]) -> None:
        """
        Updates existing key-value pairs with new data after validation.
        
        Parameters:
            allowNone (bool): If False, None values are not allowed.
            persists (bool): If True, the data is written to the file.
            update_dict (Dict[str, Any]): The data to update with.
        
        Raises:
            InvalidKeyValueError: If the update dictionary is empty.
        """
        if not update_dict:
            raise InvalidKeyValueError("No key-value data to update.")

        for key_data, value_data in update_dict.items():
            CheckAllValidation.check_all_key_validation(key_data, self._data, update=True)
            CheckAllValidation.check_all_value_validation(value_data, allowNone)

            data_type = V1Validation.identify_data_type(value_data)
            if data_type == "email":
                CheckAllValidation.check_valid_email(value_data)
            elif data_type == "phone":
                CheckAllValidation.check_valid_phone_number(value_data)
            elif data_type == "url":
                CheckAllValidation.check_valid_url(value_data)

            self.validate(key_data, value_data)

            if persists:
                self._data[key_data] = value_data

        self.write_data_to_file()

    def get_key_value(self, key_data: str) -> Any:
            """
            Retrieves the value associated with the given key from the stored data.
            
            Parameters:
                key_data (str): The key to retrieve the value for.
            
            Returns:
                Optional[Any]: The value associated with the key, or None if the key doesn't exist.
            
            Raises:
                InvalidKeyValueError: If the key is invalid (empty, None, or not a valid identifier).
            """
            if not key_data:
                raise InvalidKeyValueError("Key or value cannot be None or empty")
            if not isinstance(key_data, str) or not key_data.isidentifier():
                raise InvalidKeyValueError("Keys must be valid identifiers. Also, spaces should be replaced with underscores.")
            return self._data.get(key_data)

    def delete_key_value(self, key_data: str, persists: bool = True) -> bool:
        """
        Deletes a key-value pair from the stored data based on the provided key.
        
        Parameters:
            key_data (str): The key to delete.
            persists (bool): Whether to write the changes to the file after deletion. Default is True.
        
        Returns:
            bool: True if the key-value pair was deleted successfully, False if not.
        
        Raises:
            InvalidKeyValueError: If the key is invalid (empty, None, or not a valid identifier).
            InvalidKeyValueError: If the key doesn't exist in the data.
        """
        if not key_data:
            raise InvalidKeyValueError("Key or value cannot be None or empty")
        if not isinstance(key_data, str) or not key_data.isidentifier():
            raise InvalidKeyValueError("Keys must be valid identifiers. Also, spaces should be replaced with underscores.")
        try:
            if persists:
                del self._data[key_data]
                self.write_data_to_file()
            return True
        except KeyError as e:
            logging.error("Key '%s' not found for deletion: %s", key_data, e)
            raise InvalidKeyValueError(f"Key '{key_data}' does not exist.") from e