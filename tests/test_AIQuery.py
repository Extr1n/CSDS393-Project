import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import logging
import unittest
from unittest.mock import MagicMock, patch
from AI import AIQuery

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Test_AIQuery(unittest.TestCase):

    @patch('AI.AIQuery.client.chat.completions.create')
    def test_get_response_returns_expected_message(self, mock_create):
        mock_chat_response = MagicMock()
        mock_chat_response.choices = [MagicMock(message=MagicMock(content="Test AI response"))]
        mock_create.return_value = mock_chat_response

        prompt = "What are the required courses for CS?"
        document = "CS major requires CSDS 132, 233, 234, and MATH 122."

        response = AIQuery.get_response(prompt, document)
        self.assertEqual(response, "Test AI response")
        mock_create.assert_called_once()

    def test_get_relevant_document(self):
        # This function currently just returns the prompt.
        prompt = "Some prompt"
        result = AIQuery.get_relevant_document(prompt)
        self.assertEqual(result, prompt)

    @classmethod
    def tearDownClass(cls):
        # This will run after all tests in this class have run.
        logger.info("All tests in TestCourseParse have passed.")

if __name__ == '__main__':
    unittest.main()