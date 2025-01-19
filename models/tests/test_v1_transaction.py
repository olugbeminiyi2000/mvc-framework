from models.error.v1_Error import TransactionQueueError, DefaultError
from models.transaction.v1_Transaction import Transactions
from models.v1_Model import V1Model
import unittest


class TestTransactions(unittest.TestCase):
    def setUp(self):
        # Setup a mock V1Model instance
        self.model = V1Model()
        self.transaction = Transactions(self.model)

    def test_initialize_transaction_with_invalid_model(self):
        # Test if Transactions throws error when initialized with a non-V1Model instance
        with self.assertRaises(TypeError):
            Transactions("Exception")

    def test_generate_transaction_id(self):
        # Test if the transaction ID generation is correct
        transaction_id = Transactions.generate_transaction_id()
        self.assertTrue(transaction_id.startswith("TX-"))
        self.assertTrue(len(transaction_id.split('-')[1]) > 0)  # Ensure timestamp exists
        self.assertTrue(len(transaction_id.split('-')[-1]) == 8)  # Ensure hash part

    def test_begin_transaction_when_active(self):
        # Test if beginning a transaction raises an error when one is already active
        self.transaction.begin_transaction()
        with self.assertRaises(TransactionQueueError):
            self.transaction.begin_transaction()
        with self.assertRaises(TransactionQueueError):
            self.transaction.end_transaction()

    def test_begin_transaction(self):
        # Test if beginning a transaction works
        self.transaction.begin_transaction()
        self.assertTrue(self.transaction.transaction_id is not None)
        self.assertTrue(self.transaction.transaction_state is not None)
        self.assertTrue(Transactions.active)
        with self.assertRaises(TransactionQueueError):
            self.transaction.end_transaction()
        

    def test_commit_transaction(self):
        # Test committing a transaction after a successful operation
        self.transaction.begin_transaction()
        self.transaction.add("email", "mvcframework.python@gmail.com")
        result = self.transaction.commit_transaction()
        self.assertTrue(result)
        self.assertEqual(self.transaction.transaction_status, "committed")
        self.transaction.end_transaction()

    def test_commit_transaction_with_failure(self):
        # Test committing a transaction when an operation has failed
        self.transaction.begin_transaction()
        with self.assertRaises(DefaultError):
            self.transaction.add("last_name", None)  # Invalid value
        result = self.transaction.commit_transaction()
        self.assertFalse(result)
        self.assertEqual(self.transaction.transaction_status, "rolled_back")
        self.transaction.end_transaction()

    def test_rollback_transaction(self):
        # Test rolling back a transaction after failure
        self.transaction.begin_transaction()
        with self.assertRaises(DefaultError):
            self.transaction.add("Guardian", None)  # Invalid value
        self.transaction.rollback_transaction()
        self.assertEqual(self.transaction.transaction_status, "rolled_back")
        self.transaction.end_transaction()

    def test_end_transaction_when_committed(self):
        # Test ending a committed transaction
        self.transaction.begin_transaction()
        self.transaction.add("username", "theDarkVoid")
        self.transaction.commit_transaction()
        self.transaction.end_transaction()
        self.assertFalse(Transactions.active)

    def test_end_transaction_when_rolled_back(self):
        # Test ending a rolled-back transaction
        self.transaction.begin_transaction()
        with self.assertRaises(DefaultError):
            self.transaction.add("next_of_kin", None)  # Invalid value
        self.transaction.rollback_transaction()
        self.transaction.end_transaction()
        self.assertFalse(Transactions.active)

    def test_end_transaction_when_incomplete(self):
        # Test ending an incomplete transaction raises an error
        self.transaction.begin_transaction()
        with self.assertRaises(TransactionQueueError):
            self.transaction.end_transaction()

    def test_add_valid_key_value(self):
        # Test adding a valid key-value pair
        self.transaction.begin_transaction()
        self.transaction.add("country", "Nigeria")
        self.transaction.commit_transaction()
        self.assertEqual(self.transaction.transaction_state["country"], "Nigeria")
        self.transaction.end_transaction()

    def test_add_invalid_key(self):
        # Test adding an invalid key
        self.transaction.begin_transaction()
        with self.assertRaises(DefaultError):
            self.transaction.add("a3$£&%234@", "encrypted")
        with self.assertRaises(DefaultError):
            self.transaction.add("123", "numerical")
        with self.assertRaises(DefaultError):
            self.transaction.add(None, "numerical")
        with self.assertRaises(TransactionQueueError):
            self.transaction.end_transaction()

    def test_add_invalid_value(self):
        # Test adding an invalid value
        self.transaction.begin_transaction()
        with self.assertRaises(DefaultError):
            self.transaction.add("Gender", None)
        with self.assertRaises(TransactionQueueError):
            self.transaction.end_transaction()

    def test_update_valid_key_value(self):
        # Test updating an existing key-value pair
        self.transaction.begin_transaction()
        self.transaction.add("Sex", "Male")
        self.transaction.add("Sex", None, allowNone=True)
        self.transaction.update("Sex", "Female")
        self.transaction.commit_transaction()
        self.assertEqual(self.transaction.transaction_state["Sex"], "Female")
        self.transaction.end_transaction()

    def test_update_nonexistent_key(self):
        # Test updating a non-existent key should create it.
        self.transaction.begin_transaction()
        self.transaction.update("bone_mass", "500kg")
        self.transaction.commit_transaction()
        self.transaction.end_transaction()

    def test_delete_key(self):
        # Test deleting an existing key
        self.transaction.begin_transaction()
        self.transaction.add("animal", "kangaroo")
        self.transaction.commit_transaction()
        self.transaction.delete("animal")
        self.transaction.commit_transaction()
        self.assertNotIn("animal", self.transaction.transaction_state)
        self.transaction.end_transaction()

    def test_delete_nonexistent_key(self):
        # Test deleting a non-existent key
        self.transaction.begin_transaction()
        with self.assertRaises(DefaultError):
            self.transaction.delete("dog_species")
        with self.assertRaises(TransactionQueueError):
            self.transaction.end_transaction()

    def test_read_key(self):
        # Test reading an existing key
        self.transaction.begin_transaction()
        self.transaction.add("university", "African Leadership University")
        self.transaction.commit_transaction()
        self.transaction.read("university")
        self.assertEqual(self.transaction.transaction_queue[-1]["outcome"], "success")
        self.transaction.commit_transaction()
        self.transaction.end_transaction()

    def test_read_nonexistent_key(self):
        # Test reading a non-existent key
        self.transaction.begin_transaction()
        with self.assertRaises(DefaultError):
            self.transaction.read("highschool")

    def test_preview_transactions(self):
        # Test previewing the transaction queue
        self.transaction.begin_transaction()
        self.transaction.add("MiddleSchool", 5)
        preview = self.transaction.preview_transactions(formatted=True)
        self.assertIn("MiddleSchool", preview)
        with self.assertRaises(TransactionQueueError):
            self.transaction.end_transaction()


    def test_process_batch_valid_operations(self):
        # Test processing a valid batch of operations
        self.transaction.begin_transaction()
        batch = [
            {"action": "add", "key": "age", "value": 23},
            {"action": "update", "key": "height", "value": 6.4},
            {"action": "delete", "key": "age"}
        ]
        self.transaction.process_batch(batch)
        self.assertNotIn("sex", self.transaction.transaction_state)
        with self.assertRaises(TransactionQueueError):
            self.transaction.end_transaction()

    def test_process_batch_invalid_operations(self):
        # Test processing a batch with invalid operations
        self.transaction.begin_transaction()
        batch = [
            {"action": "submit", "key": "key1", "value": "value1"},
            {"action": "annotate", "key": "key2", "value": None}
        ]
        self.transaction.process_batch(batch)
        # No exceptions should be raised, and invalid operations should be skipped
        self.assertNotIn("key1", self.transaction.transaction_state)
        self.assertNotIn("key2", self.transaction.transaction_state)
        with self.assertRaises(TransactionQueueError):
            self.transaction.end_transaction()

if __name__ == "__main__":
    unittest.main()
