import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import logging
import unittest
from AI import Embeddings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestEmbeddings(unittest.TestCase):

    def test_embedding_output_type_single(self):
        text = "Test sentence for embedding."
        result = Embeddings.get_embedding(text)
        self.assertIsInstance(result, list)
        self.assertIsInstance(result[0], float)

    def test_embedding_output_type_list(self):
        texts = ["First sentence", "Second one"]
        result = Embeddings.get_embedding(texts)
        self.assertIsInstance(result, list)
        self.assertTrue(all(isinstance(vec, list) for vec in result))
        self.assertTrue(all(isinstance(x, float) for vec in result for x in vec))

    @classmethod
    def tearDownClass(cls):
        # This will run after all tests in this class have run.
        logger.info("All tests in TestEmbeddings have passed.")

if __name__ == '__main__':
    unittest.main()
