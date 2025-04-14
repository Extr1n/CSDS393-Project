import requests
from bs4 import BeautifulSoup
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd
import scrapereq

main = "https://bulletin.case.edu/academic-programs/#filter=.filter_2"

driver = webdriver.Chrome()
driver.get(main) 
time.sleep(2)

ini = driver.find_elements(By.XPATH, "//div/div/ul/li/a")
href = []
for i in ini:
    a = i.get_attribute("href")
    if "academic" in a:
        a = None
    if a not in href and a != None:
        a += "#programrequirementstext"
        href.append(a)


driver.quit()
all_course_req = []
b  = True
for i in range(0,len(href)):
    url = href[i]
    print(url)
    a = scrapereq.get_req(url)
    if a != None :
        
        all_course_req.append(a)
        





with open("test.json", "w") as json_file:
    json.dump(all_course_req, json_file, indent=4)
