import hashlib
import json
import logging
from models.validation.v1_Validation import CheckAllValidation, V1Validation
from models.v1_Model import V1Model
from models.error.v1_Error import InvalidKeyValueError, DefaultError, TransactionQueueError
import random
import string
import time
from typing import List, Dict, Optional, Any


# Set up error logging to error.log
error_logger = logging.getLogger('error')
error_handler = logging.FileHandler('error.log')
error_handler.setLevel(logging.ERROR)
error_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
error_handler.setFormatter(error_formatter)
error_logger.addHandler(error_handler)

# Set up info logging to info.log
info_logger = logging.getLogger('info')
info_handler = logging.FileHandler('info.log')
info_handler.setLevel(logging.INFO)
info_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
info_handler.setFormatter(info_formatter)
info_logger.addHandler(info_handler)


class Transactions(V1Model):
    active: bool = False  # Tracks the status of an ongoing transaction

    def __init__(self, v1_model: V1Model):
        """
        Initializes the Transactions class.

        :param v1_model: An instance of V1Model to work with.
        :raises TypeError: If v1_model is not an instance of V1Model.
        """
        if not isinstance(v1_model, V1Model):
            raise TypeError(f"Expected an instance of V1Model, got {type(v1_model).__name__} instead.")
        super().__init__()
        self._object = v1_model
        self._transaction_data = v1_model.get_data()
        self.transaction_state: Optional[Dict] = None
        self.transaction_id: Optional[str] = None
        self.transaction_queue: List[Dict] = []  # Queue for storing transaction operations
        self.transaction_status: Optional[str] = None

    @staticmethod
    def generate_transaction_id(prefix: str = "TX", suffix: str = "", length: int = 12) -> str:
        """
        Generates a unique transaction ID based on a timestamp and random string.

        :param prefix: Prefix for the transaction ID (default is "TX").
        :param suffix: Suffix for the transaction ID (default is empty).
        :param length: Length of the random string (default is 12).
        :return: A unique transaction ID.
        """
        timestamp = int(time.time() * 1000)  # Get current timestamp in milliseconds
        random_str = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
        transaction_id = f"{prefix}-{timestamp}-{random_str}{suffix}"
        transaction_id_hash = hashlib.md5(transaction_id.encode()).hexdigest()[:8]
        return f"{transaction_id}-{transaction_id_hash}"

    def begin_transaction(self) -> None:
        """
        Begins a new transaction by generating a transaction ID and storing the initial state.
        If a transaction is already active, raises a TransactionQueueError.
        """
        if Transactions.active:
            raise TransactionQueueError(f"Transaction {self.transaction_id} ongoing cannot proceed.")
        self.transaction_id = Transactions.generate_transaction_id()
        self.transaction_state = self._transaction_data.copy()
        Transactions.active = True
        info_logger.info(f"Transaction {self.transaction_id} started.")

    def read(self, key_data: str) -> None:
        """
        Reads data from the transaction state by the provided key.

        :param key_data: The key to read from the transaction state.
        :raises DefaultError: If the key does not exist in the state.
        """
        try:
            if self.transaction_state is None:
                raise TransactionQueueError("No active transaction. Begin a transaction first.")
            _ = self.transaction_state[key_data]  # Try to access the key
            self.transaction_queue.append({"transaction_id": self.transaction_id, "action": self.read.__name__, "data": (key_data, None), "outcome": "success", "timestamp": time.time(), "operation_id": hashlib.md5(f"{self.read.__name__}-{key_data}-{time.time()}".encode()).hexdigest()})
        except Exception as e:
            self.transaction_queue.append({"transaction_id": self.transaction_id, "action": self.read.__name__, "data": (key_data, None), "outcome": "failure", "timestamp": time.time(), "operation_id": hashlib.md5(f"{self.read.__name__}-{key_data}-{time.time()}".encode()).hexdigest()})
            Transactions.active = False
            logging.error("Key '%s' not found for deletion: %s", key_data, e)
            raise DefaultError(f"Key '{key_data}' does not exist.") from e

    def add(self, key_data: str, value_data: str, allowNone: bool = False) -> None:
        """
        Adds a new key-value pair to the transaction state.

        :param key_data: The key to add.
        :param value_data: The value to associate with the key.
        :param allowNone: Whether or not None values are allowed (default is False).
        :raises DefaultError: If there is an error in the validation or operation.
        """
        try:
            if self.transaction_state is None:
                raise TransactionQueueError("No active transaction. Begin a transaction first.")

            # Validate key and value
            CheckAllValidation.check_all_key_validation(key_data, self.transaction_state)
            CheckAllValidation.check_all_value_validation(value_data, allowNone)

            data_type = V1Validation.identify_data_type(value_data)
            if data_type == "email":
                CheckAllValidation.check_valid_email(value_data)
            elif data_type == "phone":
                CheckAllValidation.check_valid_phone_number(value_data)
            elif data_type == "url":
                CheckAllValidation.check_valid_url(value_data)
            else:
                pass

            # Custom validation
            self.validate(key_data, value_data)
        except Exception as e:
            self.transaction_queue.append({"transaction_id": self.transaction_id, "action": self.add.__name__, "data": (key_data, value_data), "outcome": "failure", "timestamp": time.time(), "operation_id": hashlib.md5(f"{self.add.__name__}-{key_data}-{time.time()}".encode()).hexdigest()})
            raise DefaultError(e)
        else:
            self.transaction_queue.append({"transaction_id": self.transaction_id, "action": self.add.__name__, "data": (key_data, value_data), "outcome": "success", "timestamp": time.time(), "operation_id": hashlib.md5(f"{self.add.__name__}-{key_data}-{time.time()}".encode()).hexdigest()})

    def update(self, key_data: str, value_data: str, allowNone: bool = False) -> None:
        """
        Updates an existing key-value pair in the transaction state.

        :param key_data: The key to update.
        :param value_data: The new value to associate with the key.
        :param allowNone: Whether or not None values are allowed (default is False).
        :raises DefaultError: If there is an error in the validation or operation.
        """
        try:
            if self.transaction_state is None:
                raise TransactionQueueError("No active transaction. Begin a transaction first.")
            
            # Validate key and value
            CheckAllValidation.check_all_key_validation(key_data, self.transaction_state, update=True)
            CheckAllValidation.check_all_value_validation(value_data, allowNone)

            data_type = V1Validation.identify_data_type(value_data)
            if data_type == "email":
                CheckAllValidation.check_valid_email(value_data)
            elif data_type == "phone":
                CheckAllValidation.check_valid_phone_number(value_data)
            elif data_type == "url":
                CheckAllValidation.check_valid_url(value_data)
            else:
                pass

            # Custom validation
            self.validate(key_data, value_data)
        except Exception as e:
            self.transaction_queue.append({"transaction_id": self.transaction_id, "action": self.update.__name__, "data": (key_data, value_data), "outcome": "failure", "timestamp": time.time(), "operation_id": hashlib.md5(f"{self.update.__name__}-{key_data}-{time.time()}".encode()).hexdigest()})
            raise DefaultError(e)
        else:
            self.transaction_queue.append({"transaction_id": self.transaction_id, "action": self.update.__name__, "data": (key_data, value_data), "outcome": "success", "timestamp": time.time(), "operation_id": hashlib.md5(f"{self.update.__name__}-{key_data}-{time.time()}".encode()).hexdigest()})

    def delete(self, key_data: str) -> bool:
        """
        Deletes a key from the transaction state.

        :param key_data: The key to delete.
        :return: True if the deletion is successful.
        :raises DefaultError: If the key does not exist in the state.
        """
        try:
            if self.transaction_state is None:
                raise TransactionQueueError("No active transaction. Begin a transaction first.")
            if not key_data:
                raise InvalidKeyValueError("Key or value cannot be None or empty")
            if not isinstance(key_data, str) or not key_data.isidentifier():
                raise InvalidKeyValueError("Keys must be valid identifiers. Also spaces should be replaced with underscore")
            # Try to get the data instead of deleting it to test for key error
            _ = self.transaction_state[key_data]
        except Exception as e:
            self.transaction_queue.append({"transaction_id": self.transaction_id, "action": self.delete.__name__, "data": (key_data, None), "outcome": "failure", "timestamp": time.time(), "operation_id": hashlib.md5(f"{self.delete.__name__}-{key_data}-{time.time()}".encode()).hexdigest()})
            error_logger.error("Key '%s' not found for deletion: %s", key_data, e)
            raise DefaultError(f"Key '{key_data}' could not be deleted.") from e
        else:
            self.transaction_queue.append({"transaction_id": self.transaction_id, "action": self.delete.__name__, "data": (key_data, None), "outcome": "success", "timestamp": time.time(), "operation_id": hashlib.md5(f"{self.delete.__name__}-{key_data}-{time.time()}".encode()).hexdigest()})
            return True

    def preview_transactions(self, formatted: bool = False) -> Any:
            """
            Previews the transactions in the current queue.
            
            Args:
                formatted (bool): Whether to return the transactions in a formatted JSON string (default is False).
            
            Returns:
                A list of transaction objects or a JSON-formatted string.
            
            Raises:
                TransactionQueueError: If no active transaction exists.
            """
            if not Transactions.active:
                raise TransactionQueueError("No active transaction to preview.")
            
            if formatted:
                return json.dumps(self.transaction_queue, indent=4)
            return self.transaction_queue
        
    def commit_transaction(self) -> bool:
        """
        Commits the transaction, updating the state if all operations are successful.
        
        Returns:
            bool: True if the transaction was successfully committed, False otherwise.
        
        Raises:
            TransactionQueueError: If no operations are in the transaction queue to commit.
        """
        if not self.transaction_queue:
            raise TransactionQueueError("No operations in the transaction queue to commit.")
        
        all_success = True
        for operation in self.transaction_queue:
            if operation["outcome"] == "failure":
                all_success = False
                break
        
        if not all_success:
            error_logger.error("Some operations have failed, rolling back the transaction.")
            self.rollback_transaction()
            return False
        
        for operation in self.transaction_queue:
            if operation["outcome"] == "success":
                action = operation["action"]
                key_data, value_data = operation["data"]
                if action == "add":
                    self.transaction_state[key_data] = value_data
                elif action == "update":
                    self.transaction_state[key_data] = value_data
                elif action == "delete":
                    del self.transaction_state[key_data]
                else:
                    print(self.transaction_state[key_data])

        self._data = self.transaction_state.copy()
        self.write_data_to_file()
        info_logger.info(f"Data written to file successfully.")     
        
        self.transaction_status = "committed"
        self.transaction_queue.clear()
        info_logger.info(f"Transaction {self.transaction_id} successfully committed.")
        return True
    
    def rollback_transaction(self) -> None:
        """
        Rolls back the current transaction, clearing the transaction queue.
        
        Raises:
            TransactionQueueError: If no active transaction exists to rollback.
        """
        if not Transactions.active:
            raise TransactionQueueError("No active transaction to rollback.")
        self.transaction_status = "rolled_back"
        self.transaction_queue.clear()
        info_logger.info("Transaction rolled back.")

    def end_transaction(self) -> None:
        """
        Ends the current transaction, either committing or rolling it back.
        
        Raises:
            TransactionQueueError: If no active transaction exists to end.
        """
        if not Transactions.active:
            raise TransactionQueueError("No active transaction to end.")
            
        if self.transaction_status == "committed":
            self.transaction_queue.clear()
            info_logger.info("Transaction committed and ended.")
        elif self.transaction_status == "rolled_back":
            self.transaction_queue.clear()
            info_logger.info("Transaction rolled back and ended.")
        else:
            Transactions.active = False
            raise TransactionQueueError("Transaction incomplete: No commit or rollback was performed.")

        Transactions.active = False
        self.transaction_status = None
        self.transaction_state = None

    def process_batch(self, batch: List[Dict]) -> None:
        """
        Processes a batch of operations for the current transaction.
        
        Args:
            batch (List[Dict]): A list of operations (add, update, delete, read).
        
        Raises:
            TransactionQueueError: If no active transaction exists or the batch format is invalid.
        """
        if not Transactions.active:
            raise TransactionQueueError("No active transaction to process batch.")
        
        if not isinstance(batch, list):
            raise TransactionQueueError("Batch must be a list of operations.")
        
        # First loop: Check for invalid keys before processing operations
        for operation in batch:
            # Ensure only the valid keys exist in the operation
            valid_keys = {"action", "key", "value"}
            invalid_keys = set(operation.keys()) - valid_keys
            
            if invalid_keys:
                raise TransactionQueueError(f"Invalid keys in operation: {invalid_keys}. Only 'action', 'key', and optionally 'value' are allowed.")
        
        # Second loop: Process the batch operations
        for operation in batch:
            action = operation.get("action")
            key_data = operation.get("key")
            value_data = operation.get("value", None)
            
            if not action or not key_data:
                error_logger.error(f"Invalid operation in batch: {operation}")
                continue  # Skip invalid operations
            
            try:
                if action == "add":
                    self.add(key_data, value_data)
                elif action == "update":
                    self.update(key_data, value_data)
                elif action == "delete":
                    self.delete(key_data)
                elif action == "read":
                    self.read(key_data)
                else:
                    error_logger.error(f"Unsupported action: {action} in batch operation.")
                    continue  # Skip unsupported actions
            except Exception as e:
                # Log the error and move on to the next operation
                error_logger.error(f"Failed to execute {action} on {key_data}: {e}")
                continue  # Skip to the next operation in the batch