import unittest
from detaillogger import DetailLogger

class TestDetailLogger(unittest.TestCase):
    def setUp(self):
        self.logger = DetailLogger()

    def test_log_message(self):
        # Just checks that logging doesn't raise an error
        try:
            self.logger.log("Test message")
        except Exception as e:
            self.fail(f"log() raised an exception: {e}")

    def test_log_exception(self):
        try:
            raise ValueError("Test error")
        except Exception as e:
            try:
                self.logger.log_exception(e, details="Testing exception")
            except Exception as log_err:
                self.fail(f"log_exception() failed: {log_err}")
    
if __name__ == "__main__":
    unittest.main()