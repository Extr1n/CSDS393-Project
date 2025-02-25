import requests
from bs4 import BeautifulSoup

# URL of the webpage
url = "https://bulletin.case.edu/engineering/computer-data-sciences/computer-science-bs/#programrequirementstext"

# Send a GET request
response = requests.get(url)

# Parse the HTML
soup = BeautifulSoup(response.text, "html.parser")

# Print formatted HTML

blocks = []

def collect_req(link, blocks):
    response = requests.get(link)
    soup = BeautifulSoup(response.text, "html.parser")
    
    course_blocks = soup.find_all("table", class_="sc_courselist")
    for block in course_blocks:
        blocks.append(block)
    
collect_req(url,blocks)



#necessary 
#groups 
#electives 
groups = []

def parse_block(block):
    table = block.find("tbody")
    list = table.find_all("tr")
    required = "Required" in list[0].find("td").find("span").get_text(strip=True)
    print(required)
    constraint = "none"
    for i in range(0,len(list)):
   
        bo = False
        for sub in list[i].get("class"):
            if ("header" in sub):
                bo = True
        if(bo):
            con = list[i].find("td").find("span").get_text(strip=True)
            if "Choose" in con:
                print(con)
                groups.append([con,[]])
                

        else:
            pass
        
    
    
parse_block(blocks[1])
print(groups)

    
