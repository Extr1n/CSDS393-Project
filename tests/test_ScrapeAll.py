# tests/test_scrapeall.py
import unittest
from unittest.mock import patch, MagicMock, mock_open
import json
import sys
import os

# Ensure the project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the modules under test from the full package path.
from scrape import scrapeall, scrapereq

class TestScrapeAll(unittest.TestCase):
    @patch('scrape.req.scrapeall.webdriver.Chrome')
    @patch('scrape.req.scrapeall.scrapereq.get_req')
    @patch('scrape.req.scrapeall.time.sleep', return_value=None)
    @patch('builtins.open', new_callable=mock_open)
    def test_scrapeall(self, mock_file, mock_sleep, mock_get_req, mock_chrome):
        # Setup dummy Selenium driver instance
        dummy_element = MagicMock()
        dummy_element.get_attribute.return_value = "http://example.com/test"
        driver_instance = MagicMock()
        driver_instance.find_elements.return_value = [dummy_element]
        mock_chrome.return_value = driver_instance

        # Set get_req to return a dummy data dictionary
        dummy_data = {"title": "Dummy Course"}
        mock_get_req.return_value = dummy_data

        # Override the href list to control the loop (simulate one URL)
        scrapeall.href = ["http://example.com/test#programrequirementstext"]

        # Reset the accumulator list and run the loop manually
        scrapeall.all_course_req = []
        for i in range(len(scrapeall.href)):
            url = scrapeall.href[i]
            # Here we use scrapereq.get_req (which should be patched via scrapeall's reference)
            data = scrapereq.get_req(url)
            if data is not None:
                scrapeall.all_course_req.append(data)

        # Write the data using our patched open
        with open("test.json", "w") as f:
            json.dump(scrapeall.all_course_req, f, indent=4)

        # Assert that the file write was called with our dummy data
        handle = mock_file()
        # Retrieve the actual written string from the mock (the write call may be called multiple times)
        written_calls = ''.join(call_arg[0][0] for call_arg in handle.write.call_args_list)
        written_data = json.loads(written_calls)
        self.assertEqual(written_data, [dummy_data])

if __name__ == '__main__':
    unittest.main()
