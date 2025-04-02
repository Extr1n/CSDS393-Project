import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from unittest.mock import MagicMock, patch
from AI import Embeddings

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

if __name__ == '__main__':
    unittest.main()
