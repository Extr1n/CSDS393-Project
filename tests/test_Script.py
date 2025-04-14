# tests/test_scrapeall.py
import unittest
from unittest.mock import patch, MagicMock, mock_open
import json
import sys
import pandas as pd
import os


scrape_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scrape'))
sys.path.append(scrape_path)

# imported files to test (scrapeall and scrapereq)
from scrape import parse, script_sub



titles = []
desc = []

href = ["https://bulletin.case.edu/course-descriptions/anee/","https://bulletin.case.edu/course-descriptions/dsci/","https://bulletin.case.edu/course-descriptions/arab/","https://bulletin.case.edu/course-descriptions/bafi/"]

class TestClassScript(unittest.TestCase):

    def test_script(self):
        for i in range(len(href)):
            script_sub.collect_courses(href[i],titles,desc)

        d = {"title": titles, "desc": desc}
        df = pd.DataFrame(data=d)

        df.to_json('testcourse.json',orient='records',indent=4)

        with open('testcourse.json') as f1, open('unittestcourse.json') as f2:
                    json1 = json.load(f1)
                    json2 = json.load(f2) # hand created json file of requirements in astornomy minor to compare to the scrapeall.py output

        # Assert equality
        assert json1 == json2


if __name__ == '__main__':
    unittest.main()
