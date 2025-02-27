import requests
from bs4 import BeautifulSoup
import json

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
necessary = []
groups = []
electives = []

def parse_block(block):
    table = block.find("tbody")
    list = table.find_all("tr")
    required = False
    for c in list[0].get("class"):
        if "header" in c:
            required = "Required" in list[0].find("td").find("span").get_text(strip=True)
    print(required)
    constraint = "none"
    for i in range(0,len(list)):

   
        bo = False
        for sub in list[i].get("class"):
            if ("header" in sub):
                bo = True
        if(bo): #header
            con = list[i].find("td").find("span").get_text(strip=True)
            if "Choose" in con: #header is a constraint
                constraint = con
                
                groups.append([con,[]])
            else:
                constraint = "none"
                

        else: #class 
            if(required):
                #check constraint
                if(constraint == "none"):
                    #ADD TO NECESSARY
                    if(list[i].get("class")[0] == "orclass"):
                        cl = list[i].find("td").get_text(strip=True)
                        cl = cl[2:6] + cl[7:]
                        necessary[len(necessary)-1].append(cl)
                    else:#or class
                        cl = list[i].find("td").get_text(strip=True)
                        cl = cl[:4] + cl[5:]
                        necessary.append([cl])
                else:
                    #add to current group
                    cl = list[i].find("td").get_text(strip=True)
                    cl = cl[:4] + cl[5:]
                    groups[len(groups)-1][1].append(cl)
                    
                    pass
                pass
            else:
                #add tp electives
                if(constraint == "none"):
                    #ADD TO NECESSARY
                    cl = list[i].find("td").get_text(strip=True)
                    cl = cl[:4] + cl[5:]
                    electives.append(cl)
                else:
                    #add to current group
                    cl = list[i].find("td").get_text(strip=True)
                    cl = cl[:4] + cl[5:]
                    groups[len(groups)-1][1].append(cl)
                pass
            
                
        
    
for block in blocks:
    parse_block(block)
print("groups")
print(groups)
print("hard")
print(necessary)
print("electives")
print(electives)

data = {
    "necessary": necessary,
    "groups": groups,
    "electives": electives
}

with open("exCS_BS.json", "w") as json_file:
    json.dump(data, json_file, indent=4)

    
