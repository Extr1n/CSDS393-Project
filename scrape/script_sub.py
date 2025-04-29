"""
    This script scrapes the course titles and descriptions from the CWRU course catelog for a specific subject area.
"""

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd
import re


def collect_courses(link, titles, desc):
    """
    Collects course titles and descriptions from a given link using Selenium and BeautifulSoup.
    This function navigates to the provided link, extracts course information, and appends it to the provided lists.

    Args:
        link (str): URL to the course catalog page for a specific subject area.
        titles (list): A list to store the extracted course titles
        desc (list): A list to store the extracted course descriptions
    """
    driver =  webdriver.Chrome()
    driver.get(link)
    time.sleep(2)
    source = driver.page_source
    driver.quit()
    soup = BeautifulSoup(source, "html.parser")
    

    course_blocks = soup.find_all("div", class_="courseblock")

    # Iterate through every course in subject
    for block in course_blocks:
        title = block.find("p", class_="courseblocktitle").get_text(strip=True) if block.find("p", class_="courseblocktitle") else "N/A"
        titles.append(title)

        description = block.find("p", class_="courseblockdesc").get_text(strip=True) if block.find("p", class_="courseblockdesc") else "N/A"
        desc.append(description)