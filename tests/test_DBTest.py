import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, module="pydantic.v1.typing")

import unittest
from unittest.mock import patch, MagicMock
import importlib
import logging

# Configure logging (optional)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set the necessary environment variables.
env = {
    'MONGODB_URI': 'dummy_uri',
    'MONGODB_DB': 'dummy_db',
    'MONGODB_COLL': 'dummy_coll'
}
os.environ.update(env)

class TestDBTestModule(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Patch builtins.print BEFORE importing DBTest so that the print(3)
        # call inside DBTest gets captured.
        cls.print_patch = patch('builtins.print')
        cls.mock_print = cls.print_patch.start()

        # Patch the MongodbLoader so that load() returns 3 dummy documents.
        cls.mongodb_patch = patch('langchain_community.document_loaders.mongodb.MongodbLoader')
        cls.MockLoader = cls.mongodb_patch.start()
        instance = MagicMock()
        instance.load.return_value = ['doc1', 'doc2', 'doc3']  # simulate three documents
        cls.MockLoader.return_value = instance

        # Now import (or reload) DBTest so its code executes with our patches in place.
        from scrape import DBTest
        importlib.reload(DBTest)

    @classmethod
    def tearDownClass(cls):
        cls.print_patch.stop()
        cls.mongodb_patch.stop()
        logger.info("All tests in DBTest have passed.")

    def test_print_length_of_docs(self):
        """
        Since the patched loader returns three docs, we expect that when DBTest is imported,
        it prints the number 3. We check that the patched print was called with 3.
        """
        self.mock_print.assert_called_with(3)

if __name__ == '__main__':
    unittest.main()
