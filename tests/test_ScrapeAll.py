# tests/test_scrapeall.py
import unittest
from unittest.mock import patch, MagicMock, mock_open
import json
import sys
import os


scrape_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scrape/req'))
sys.path.append(scrape_path)

# imported files to test (scrapeall and scrapereq)
import scrapeall, scrapereq



# test scrapereq.py on example url (astronomy minor)

testurl = "https://bulletin.case.edu/arts-sciences/astronomy/astronomy-minor/#programrequirementstext"

class TestScrapeAll(unittest.TestCase):

    def test_scrapeall(self):
      
        # simulate scrapeall.py iteration over urls
        reqs = [testurl]
        all = []
        for i in range(len(reqs)):
            url = reqs[i]
            # simulate call to scrapereq.py in scrapeall.py
            data = scrapereq.get_req(url)
            if data is not None:
                all.append(data)

        # store data from call
        with open("test.json", "w") as f:
            json.dump(all[0], f, indent=4)

        with open('test.json') as f1, open('unittest.json') as f2:
            json1 = json.load(f1)
            json2 = json.load(f2) # hand created json file of requirements in astornomy minor to compare to the scrapeall.py output

        # Assert equality
        assert json1 == json2

    

if __name__ == '__main__':
    unittest.main()
