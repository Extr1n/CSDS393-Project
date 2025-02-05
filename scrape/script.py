from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd

driver = webdriver.Chrome()
driver.get("https://bulletin.case.edu/course-descriptions/")  #holds all subjects


time.sleep(2)  

links = driver.find_elements(By.XPATH, "//div/ul/li/a")
href = []
for link in links:
    href.append(link.get_attribute("href"))


driver.quit()


titles = []
desc = []

def collect_courses(link, titles, desc):
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
        

for i in range(30,len(href)):
    collect_courses(href[i],titles,desc)

d = {"title": titles, "desc": desc}
df = pd.DataFrame(data=d)

df.to_json('allcourse.json',orient='records',indent=4)