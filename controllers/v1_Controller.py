from loggings.v1_Logging import error_logger, info_logger, warning_logger
from models.error.v1_Error import DefaultError
from models.transaction.v1_Transaction import Transactions


class V1BaseController:
    """
    Base controller class that handles CRUD operations with transaction management.

    Attributes:
        transaction_class (Transactions): Instance of the Transactions class
        used to manage database operations.
    """

    def __init__(self, v1_transactions: Transactions):
        """
        Initializes the controller with a Transactions instance.

        Args:
            v1_transactions (Transactions): An instance of the Transactions class.

        Raises:
            TypeError: If the provided `v1_transactions` is not an instance of Transactions.
        """
        if not isinstance(v1_transactions, Transactions):
            raise TypeError(f"Expected an instance of Transactions, got {type(v1_transactions).__name__} instead.")
        self.transaction_class = v1_transactions

    def create(self, data: dict) -> bool:
        """
        Creates a new record in the database using a dictionary of key-value pairs.

        Args:
            data (dict): A dictionary containing the key-value pairs to be added.

        Returns:
            bool: True if the transaction was successfully committed, False otherwise.

        Raises:
            TypeError: If the input data is not a dictionary.
            ValueError: If the input data dictionary is empty.
            DefaultError: If a custom error occurs during the transaction.
            Exception: For unexpected errors.
        """
        if not isinstance(data, dict):
            raise TypeError(f"Expected a dictionary of key-value pairs, got {type(data).__name__} instead.")
        if not data:
            raise ValueError("data dict cannot be empty.")
        try:
            info_logger.info("Starting Transaction")
            self.transaction_class.begin_transaction()
            for field, value in data.items():
                self.transaction_class.add(field, value)
            result = self.transaction_class.commit_transaction()
            if result:
                info_logger.info("Transaction successfully committed.")
            else:
                info_logger.info("Transaction failed, rolledback.")
        except TypeError as e:
            self.transaction_class.rollback_transaction()
            self.transaction_class.end_transaction()
            error_logger.error("TypeError: %s", e)
            raise TypeError(f"Invalid input data: {e}")    
        except DefaultError as e:
            self.transaction_class.rollback_transaction()
            self.transaction_class.end_transaction()
            error_logger.error("Error: %s", e)
            raise DefaultError(f"Error: {e}")
        except Exception as e:
            self.transaction_class.rollback_transaction()
            self.transaction_class.end_transaction()
            error_logger.error("Unexpected error: %s", e)
            raise Exception(f"Unexpected error: {e}")
        else:
            self.transaction_class.end_transaction()
            info_logger.info("Transaction ended.")
        
        return result

    def read(self, filters: list[str]) -> dict:
        """
        Reads data from the database based on a list of filters.

        Args:
            filters (list[str]): A list of keys or labels to fetch from the database.

        Returns:
            dict: A dictionary of the retrieved data.

        Raises:
            TypeError: If the filters argument is not a list of strings.
            ValueError: If the filters list is empty or contains non-string elements.
            DefaultError: If a custom error occurs during the transaction.
            Exception: For unexpected errors.
        """
        if not isinstance(filters, list):
            raise TypeError(f"Expected a list of keys or labels, got {type(filters).__name__} instead.")
        if not filters:
            raise ValueError("List of filters cannot be empty.")
        for field in filters:
            if not isinstance(field, str):
                raise ValueError(f"Each filter field must be a string, but got {type(field).__name__}.")
        try:
            info_logger.info("Starting Transaction")
            self.transaction_class.begin_transaction()
            for field in filters:
                self.transaction_class.read(field)
            result = self.transaction_class.commit_transaction()
            if result:
                info_logger.info("Transaction successfully committed.")
            else:
                info_logger.info("Transaction failed, rolledback.")
        except (TypeError, ValueError) as e:
            self.transaction_class.rollback_transaction()
            self.transaction_class.end_transaction()
            error_logger.error(f"Error during transaction: {e}")
            raise    
        except DefaultError as e:
            self.transaction_class.rollback_transaction()
            self.transaction_class.end_transaction()
            error_logger.error(f"Error: {e}")
            raise DefaultError(f"Error: {e}")      
        except Exception as e:
            self.transaction_class.rollback_transaction()
            self.transaction_class.end_transaction()
            error_logger.error(f"Unexpected error: {e}")
            raise Exception(f"Unexpected error: {e}")
        else:
            self.transaction_class.end_transaction()
            info_logger.info("Transaction ended.")

        if not self.transaction_class.read_data_store:
            warning_logger.warning("The data store is empty or invalid, returning an empty list as fallback.")
            return {}
        return self.transaction_class.read_data_store
    
    def update(self, data: dict) -> bool:
        """
        Updates existing records in the database using a dictionary of key-value pairs.

        Args:
            data (dict): A dictionary containing the key-value pairs to update.

        Returns:
            bool: True if the transaction was successfully committed, False otherwise.

        Raises:
            TypeError: If the input data is not a dictionary.
            ValueError: If the input data dictionary is empty.
            DefaultError: If a custom error occurs during the transaction.
            Exception: For unexpected errors.
        """
        if not isinstance(data, dict):
            raise TypeError(f"Expected a dictionary of key-value pairs, got {type(data).__name__} instead.")
        if not data:
            raise ValueError("data dict cannot be empty.")
        try:
            info_logger.info("Starting Transaction")
            self.transaction_class.begin_transaction()
            for field, value in data.items():
                self.transaction_class.update(field, value)
            result = self.transaction_class.commit_transaction()
            if result:
                info_logger.info("Transaction successfully committed.")
            else:
                info_logger.info("Transaction failed, rolledback.")
        except TypeError as e:
            self.transaction_class.rollback_transaction()
            self.transaction_class.end_transaction()
            error_logger.error("TypeError: %s", e)
            raise TypeError(f"Invalid input data: {e}")    
        except DefaultError as e:
            self.transaction_class.rollback_transaction()
            self.transaction_class.end_transaction()
            error_logger.error("Error: %s", e)
            raise DefaultError(f"Error: {e}")
        except Exception as e:
            self.transaction_class.rollback_transaction()
            self.transaction_class.end_transaction()
            error_logger.error("Unexpected error: %s", e)
            raise Exception(f"Unexpected error: {e}")
        else:
            self.transaction_class.end_transaction()
            info_logger.info("Transaction ended.")
        
        return result
    
    def delete(self, filters: list[str]) -> bool:
        """
        Deletes records from the database based on a list of filters.

        Args:
            filters (list[str]): A list of keys or labels to delete from the database.

        Returns:
            bool: True if the transaction was successfully committed, False otherwise.

        Raises:
            TypeError: If the filters argument is not a list of strings.
            ValueError: If the filters list is empty or contains non-string elements.
            DefaultError: If a custom error occurs during the transaction.
            Exception: For unexpected errors.
        """
        if not isinstance(filters, list):
            raise TypeError(f"Expected a list of keys or labels, got {type(filters).__name__} instead.")
        if not filters:
            raise ValueError("List of filters cannot be empty.")
        if any(not isinstance(field, str) for field in filters):
            raise ValueError("All filter fields must be strings.")
        try:
            info_logger.info("Starting Transaction")
            self.transaction_class.begin_transaction()
            for field in filters:
                self.transaction_class.delete(field)
            result = self.transaction_class.commit_transaction()
            if result:
                info_logger.info("Transaction successfully committed.")
            else:
                info_logger.info("Transaction failed, rolledback.")
        except (TypeError, ValueError) as e:
            self.transaction_class.rollback_transaction()
            self.transaction_class.end_transaction()
            error_logger.error(f"Error during transaction: {e}")
            raise
        except DefaultError as e:
            self.transaction_class.rollback_transaction()
            self.transaction_class.end_transaction()
            error_logger.error(f"Error: {e}")
            raise DefaultError(f"Error: {e}")      
        except Exception as e:
            self.transaction_class.rollback_transaction()
            self.transaction_class.end_transaction()
            error_logger.error(f"Unexpected error: {e}")
            raise Exception(f"Unexpected error: {e}")
        else:
            self.transaction_class.end_transaction()
            info_logger.info("Transaction ended.")

        return result
    