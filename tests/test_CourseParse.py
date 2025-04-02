import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import logging
from scrape.courses_parse import parse_course_info

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestCourseParse(unittest.TestCase):
    
    def test_parse_course_info_succuss(self):
        # Input that should be correctly parsed.
        input_data = {
            "title": "AIQS 100. Academic Inquiry Seminar. 3 Units.",
            "desc": (
                "This course develops the habits of mind and writing/communication processes that "
                "characterize academic discourse. Students engage with questions and topics from "
                "multiple perspectives, and they establish effective writing processes (including "
                "planning, drafting, responding to feedback, revising, reflecting, and self-assessing)."
            )
        }
        # Expected output (parsed_course data)
        expected_output = {
            "department": "AIQS",
            "class_code": "AIQS 100",
            "class_title": "Academic Inquiry Seminar",
            "units": "3 Units",
            "description": (
                "This course develops the habits of mind and writing/communication processes that "
                "characterize academic discourse. Students engage with questions and topics from "
                "multiple perspectives, and they establish effective writing processes (including "
                "planning, drafting, responding to feedback, revising, reflecting, and self-assessing)."
            )
        }

        parsed = parse_course_info(input_data)
        self.assertEqual(parsed, expected_output)

    def test_parse_course_info_failure(self):
        course_data = {
            'title': 'Invalid Title Format',
            'desc': 'Some description'
        }
        with self.assertRaises(ValueError):
            parse_course_info(course_data)

    @classmethod
    def tearDownClass(cls):
        # This will run after all tests in this class have run.
        logger.info("All tests in TestCourseParse have passed.")


if __name__ == '__main__':
    unittest.main()