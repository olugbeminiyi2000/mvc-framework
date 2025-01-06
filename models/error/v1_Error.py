class InvalidKeyValueError(Exception):
    """
    Exception raised for invalid key-value operations in a transaction.

    This exception is used when an invalid key or value is encountered
    in a transaction operation, such as an unsupported or invalid key,
    or when the value doesn't match the expected type or format.

    Inherits from the built-in Exception class.
    """
    pass

class TransactionQueueError(Exception):
    """
    Exception raised for errors related to the transaction queue.

    This exception is raised when there is an issue with the transaction queue,
    such as when no active transaction exists, or when invalid operations are
    attempted within the queue (e.g., trying to commit an empty queue).

    Inherits from the built-in Exception class.
    """
    pass

class DefaultError(Exception):
    """
    A generic exception for unexpected or unspecified errors.

    This exception is used as a catch-all for errors that don't fall under more
    specific exceptions. It is meant for general error handling when no other
    error type applies.

    Inherits from the built-in Exception class.
    """
    pass
