import unittest
from models.validation.v1_Validation import V1Validation, CheckAllValidation

class TestV1Validation(unittest.TestCase):
    def setUp(self):
        self.sample_data = {"first_name": "Emmanuel"}

    # Test for is_key_truthy_value
    def test_is_key_truthy_value(self):
        self.assertTrue(V1Validation.is_key_truthy_value("Abiodun"))
        self.assertTrue(V1Validation.is_key_truthy_value(2))
        self.assertFalse(V1Validation.is_key_truthy_value(""))
        self.assertFalse(V1Validation.is_key_truthy_value(None))        

    # Test for is_valid_identifier
    def test_is_valid_identifier(self):
        self.assertTrue(V1Validation.is_valid_identifier("Address"))
        self.assertFalse(V1Validation.is_valid_identifier("a@biscuit"))
        self.assertFalse(V1Validation.is_valid_identifier(123))

    # Test for is_not_reserved_word
    def test_is_not_reserved_word(self):
        self.assertTrue(V1Validation.is_not_reserved_word("custom"))
        self.assertTrue(V1Validation.is_not_reserved_word("python"))
        self.assertFalse(V1Validation.is_not_reserved_word("class"))
        self.assertFalse(V1Validation.is_not_reserved_word("lambda"))

    # Test for is_key_within_length_limit
    def test_is_key_within_length_limit(self):
        self.assertTrue(V1Validation.is_key_within_length_limit("Information Communication Technology"))
        self.assertFalse(V1Validation.is_key_within_length_limit("height" * 100))

    # Test for is_value_acceptable_type
    def test_is_value_acceptable_type(self):
        self.assertTrue(V1Validation.is_value_acceptable_type(True))
        self.assertTrue(V1Validation.is_value_acceptable_type(False))
        self.assertTrue(V1Validation.is_value_acceptable_type(None, allowNone=True))
        self.assertTrue(V1Validation.is_value_acceptable_type("", allowNone=True))
        self.assertFalse(V1Validation.is_value_acceptable_type(None))
        self.assertFalse(V1Validation.is_value_acceptable_type(""))
        self.assertFalse(V1Validation.is_value_acceptable_type([]))
        self.assertFalse(V1Validation.is_value_acceptable_type({}))

    # Test for is_key_unique
    def test_is_key_unique(self):
        self.assertTrue(V1Validation.is_key_unique("last_name", self.sample_data))
        self.assertFalse(V1Validation.is_key_unique("first_name", self.sample_data))

    # Test for identify_data_type
    def test_identify_data_type(self):
        self.assertEqual(V1Validation.identify_data_type("test@example.com"), "email")
        self.assertEqual(V1Validation.identify_data_type("http://example.com"), "url")
        self.assertEqual(V1Validation.identify_data_type("1234567890"), "unknown")
        self.assertEqual(V1Validation.identify_data_type("+923001234567"), "phone")

    # Test for is_valid_phone_number
    def test_is_valid_phone_number(self):
        self.assertTrue(V1Validation.is_valid_phone_number("923001234567"))
        self.assertFalse(V1Validation.is_valid_phone_number("123456"))

    # Test for is_valid_email
    def test_is_valid_email(self):
        self.assertTrue(V1Validation.is_valid_email("test@example.com"))
        self.assertTrue(V1Validation.is_valid_email("test@gmail.com"))
        self.assertFalse(V1Validation.is_valid_email("testgmail.com"))
        self.assertFalse(V1Validation.is_valid_email("test@gmail"))

    # Test for is_valid_url
    def test_is_valid_url(self):
        self.assertTrue(V1Validation.is_valid_url("http://example.com"))
        self.assertTrue(V1Validation.is_valid_url("https://example.com"))
        self.assertFalse(V1Validation.is_valid_url("htp:/example"))

class TestCheckAllValidation(unittest.TestCase):
    def setUp(self):
        self.sample_data = {"first_name": "Renoir"}

    # Test for check_all_key_validation
    def test_check_all_key_validation(self):
        with self.assertRaises(ValueError):
            # for checking truthy value of key
            CheckAllValidation.check_all_key_validation("", self.sample_data)

        with self.assertRaises(ValueError):
            # for checking reserved keyword of key
            CheckAllValidation.check_all_key_validation("class", self.sample_data)

        with self.assertRaises(ValueError):
            # for checking uniqueness of key
            CheckAllValidation.check_all_key_validation("first_name", self.sample_data)

        with self.assertRaises(ValueError):
            # for checking valid indentifier
            CheckAllValidation.check_all_key_validation("123", self.sample_data)

        # new key with no issues
        CheckAllValidation.check_all_key_validation("last_name", self.sample_data)  # Should not raise
        # existing key but an update
        CheckAllValidation.check_all_key_validation("first_name", self.sample_data, update=True)  # Should not raise

    # Test for check_all_value_validation
    def test_check_all_value_validation(self):
        with self.assertRaises(ValueError):
            CheckAllValidation.check_all_value_validation(None)

        CheckAllValidation.check_all_value_validation("African Leadership University")  # Should not raise

    # Test for check_valid_phone_number
    def test_check_valid_phone_number(self):
        with self.assertRaises(ValueError):
            CheckAllValidation.check_valid_phone_number("123456")

        CheckAllValidation.check_valid_phone_number("923001234567")  # Should not raise

    # Test for check_valid_email
    def test_check_valid_email(self):
        with self.assertRaises(ValueError):
            CheckAllValidation.check_valid_email("testgmail.com")

        CheckAllValidation.check_valid_email("test@example.com")  # Should not raise

    # Test for check_valid_url
    def test_check_valid_url(self):
        with self.assertRaises(ValueError):
            CheckAllValidation.check_valid_url("htp:/example")

        CheckAllValidation.check_valid_url("http://example.com")  # Should not raise

if __name__ == "__main__":
    unittest.main()
