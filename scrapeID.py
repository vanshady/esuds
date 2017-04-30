from string import ascii_letters
import requests
import sys
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import time
import re
import json

domain = "http://asi.esuds.net/RoomStatus/showRoomStatus.do"

def getUrl():
    soup = queryEsuds()
    data = parseEsuds(soup)

    with open('asi.json', 'w') as fp:
        json.dump(data, fp, sort_keys=True, indent=4)

def parseEsuds(soup):
    table = soup.find("ul", {"class": "treeLevel5"})

    tableHead = 0
    data = {}
    for schoolLi in table.find_all("li", recursive=False):
        school = schoolLi.find(text=True, recursive=False).strip()
        data[school] = {}
        for campusLi in schoolLi.find("ul", {"class": "treeLevel4"}).find_all("li", recursive=False):
            campus = campusLi.find(text=True, recursive=False).strip()
            data[school][campus] = {}
            for hallLi in campusLi.find("ul", {"class": "treeLevel3"}).find_all("li", recursive=False):
                hall = hallLi.find("a").text.strip()
                href = "http://asi.esuds.net/RoomStatus/" + hallLi.find("a")['href']
                data[school][campus][hall] = getHallIdList(href)

    print(data)
    return data

def getHallIdList(url):
    soup = getWebpageSource(url)
    script = soup.find("body").find("script").get_text()
    idList = []
    hallId = int(re.findall('bottomLocationId=(.*?)\"', script)[0])
    idList.append(hallId)
    return idList


def queryEsuds():
    queryUrl = domain
    soup = getWebpageSource(queryUrl)
    return soup

# gets a BeautifulSoup object of the given url's source
def getWebpageSource(url):
    ua = UserAgent()
    headers = { "Connection": "close", "User-Agent": ua.random }
    r = requests.get(url, headers = headers, timeout = 20)
    return BeautifulSoup(r.text, "html.parser")

getUrl()
