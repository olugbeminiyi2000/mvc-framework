from models.validation.dialing_code.dialing_code import DailingCodes
from keyword import iskeyword
import re


class V1Validation:
    """Provides static methods for key and value validation."""

    @staticmethod
    def is_key_truthy_value(user_key: str) -> bool:
        """
        Checks if the given key is truthy.
        
        :param user_key: The key to validate.
        :return: True if the key is truthy, False otherwise.
        """
        return bool(user_key)

    @staticmethod
    def is_valid_identifier(user_key: str) -> bool:
        """
        Checks if the given key is a valid Python identifier.
        
        :param user_key: The key to validate.
        :return: True if the key is a valid identifier, False otherwise.
        """
        try:
            return user_key.isidentifier()
        except AttributeError:
            return False

    @staticmethod
    def is_not_reserved_word(user_key: str) -> bool:
        """
        Checks if the given key is not a reserved Python keyword.
        
        :param user_key: The key to validate.
        :return: True if the key is not a reserved keyword, False otherwise.
        """
        return not iskeyword(user_key)

    @staticmethod
    def is_key_within_length_limit(user_key: str, limit: int = 300) -> bool:
        """
        Checks if the key's length is within the specified limit.
        
        :param user_key: The key to validate.
        :param limit: The maximum allowed length.
        :return: True if the key length is within the limit, False otherwise.
        """
        return len(user_key) <= limit

    @staticmethod
    def is_value_acceptable_type(user_value: object, allowNone: bool = False) -> bool:
        """
        Validates the value's acceptability based on its type.
        
        :param user_value: The value to validate.
        :param allowNone: Whether None is allowed as a value.
        :return: True if the value is acceptable, False otherwise.
        """
        if allowNone or isinstance(user_value, bool):
            return True
        return bool(user_value)

    @staticmethod
    def is_key_unique(user_key: str, data: dict) -> bool:
        """
        Checks if the key is unique in the given dataset.
        
        :param user_key: The key to validate.
        :param data: The dataset to check against.
        :return: True if the key is unique, False otherwise.
        """
        return user_key not in data

    @staticmethod
    def identify_data_type(value: object) -> str:
        """
        Identifies the type of data based on its format.
        
        :param value: The data to identify.
        :return: The identified data type ('email', 'phone', 'url', or 'unknown').
        """
        if V1Validation.is_valid_email(value):
            return "email"
        elif V1Validation.is_valid_phone_number(value):
            return "phone"
        elif V1Validation.is_valid_url(value):
            return "url"
        else:
            return "unknown"

    @staticmethod
    def is_valid_phone_number(phone_number: object) -> bool:
        """
        Validates the given phone number against known patterns.
        
        :param phone_number: The phone number to validate.
        :return: True if the phone number is valid, False otherwise.
        """
        phone_number = re.sub(r'\D', '', str(phone_number))
        for phone_pattern in DailingCodes.phone_number_patterns:
            if re.fullmatch(phone_pattern, phone_number):
                return True
        return False

    @staticmethod
    def is_valid_email(email: object) -> bool:
        """
        Validates the given email using a regex pattern.
        
        :param email: The email to validate.
        :return: True if the email is valid, False otherwise.
        """
        EMAIL_PATTERN = r"(^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$)"
        prog = re.compile(EMAIL_PATTERN)
        return bool(prog.fullmatch(str(email)))

    @staticmethod
    def is_valid_url(url: object) -> bool:
        """
        Validates the given URL using a regex pattern.
        
        :param url: The URL to validate.
        :return: True if the URL is valid, False otherwise.
        """
        URL_PATTERN = r"^(https?|ftp|file|ws|wss):\/\/[^\s/$.?#].[^\s]*$"
        prog = re.compile(URL_PATTERN)
        return bool(prog.fullmatch(str(url)))


class CheckAllValidation:
    """Provides methods to validate keys and values comprehensively."""

    @staticmethod
    def check_all_key_validation(user_key: str, data: dict, update: bool = False) -> None:
        """
        Performs all key validations sequentially.

        :param user_key: The key to validate.
        :param data: The dataset to check for uniqueness.
        :param update: Skip uniqueness validation if updating.
        :raises ValueError: If any validation fails.
        """
        validation_methods = [
            (V1Validation.is_key_truthy_value, "Key must be a truthy value."),
            (V1Validation.is_valid_identifier, "Key must be a valid identifier. Also spaces should be replaced with underscore"),
            (V1Validation.is_not_reserved_word, "Key must not be a reserved keyword."),
            (lambda key: V1Validation.is_key_unique(key, data), "Key must be unique, or use update method instead to make changes."),
            (lambda key: V1Validation.is_key_within_length_limit(key, 300), "Key must not exceed 300 characters."),
        ]
        for validate, error_message in validation_methods:
            if update and "unique" in error_message.lower():
                continue
            if not validate(user_key):
                raise ValueError(f"'{user_key}' failed validation: {error_message}")

    @staticmethod
    def check_all_value_validation(user_value: object, allowNone: bool = False) -> None:
        """
        Validates all value-related rules.

        :param user_value: The value to validate.
        :param allowNone: Whether None is allowed as a value.
        :raises ValueError: If validation fails.
        """
        if not V1Validation.is_value_acceptable_type(user_value, allowNone):
            raise ValueError(f"'{user_value}' failed validation: Value cannot be empty or None.")

    @staticmethod
    def check_valid_phone_number(phone_number: object) -> None:
        """
        Validates if the phone number is valid.

        :param phone_number: The phone number to validate.
        :raises ValueError: If the phone number is invalid.
        """
        if not V1Validation.is_valid_phone_number(phone_number):
            raise ValueError(f"'{phone_number}' failed validation: Please enter a valid phone number with the correct country code (with or without the '+' sign). Example: '923001234567' for Pakistan.")

    @staticmethod
    def check_valid_email(email: object) -> None:
        """
        Validates if the email is valid.

        :param email: The email to validate.
        :raises ValueError: If the email is invalid.
        """
        if not V1Validation.is_valid_email(email):
            raise ValueError(f"'{email}' failed validation: Please enter a valid email. E.g example@domain.com")

    @staticmethod
    def check_valid_url(url: object) -> None:
        """
        Validates if the URL is valid.

        :param url: The URL to validate.
        :raises ValueError: If the URL is invalid.
        """
        if not V1Validation.is_valid_url(url):
            raise ValueError(f"'{url}' failed validation: Please enter a valid URL")
