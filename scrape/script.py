"""
Main script to scrape course descriptions from Case Western Reserve University Bulletin.
This script uses Selenium to navigate the bulletin website, extract course titles and descriptions.

Visits main CWRU bulletin and passes each page to script_sub.py

"""

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd
import re
import script_sub

driver = webdriver.Chrome()
driver.get("https://bulletin.case.edu/course-descriptions/")  #holds all subjects


time.sleep(2)  

links = driver.find_elements(By.XPATH, "//div/ul/li/a")
href = []
# Extract the href attributes from the links to each subject
for link in links:
    href.append(link.get_attribute("href"))


driver.quit()


titles = []
desc = []

#iterate through all subjects, calling subroutine to scrape all courses for each subject
for i in range(30,len(href)):
    script_sub.collect_courses(href[i],titles,desc)

d = {"title": titles, "desc": desc}
df = pd.DataFrame(data=d)

#store raw cours data as json
df.to_json('allcourse.json',orient='records',indent=4)