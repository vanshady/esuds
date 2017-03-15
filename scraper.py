from string import ascii_letters
import requests
import sys
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

domain = "http://jhu.esuds.net/RoomStatus/machineStatus.i?bottomLocationId="

def getUrl(buttomLocationId):
    soup = queryEsuds(buttomLocationId)
    machines = parseEsuds(soup)
    if (machines == None):
        return None
    return machines

def parseEsuds(soup):
    table = soup.findAll("table", {"class": "room_status"})[0]
    tableHead = 0
    result = []
    for tr in table.find_all("tr"):
        if tableHead == 0:
            tableHead = 1
        else:
            machine = {}
            index = 0
            types = ["id", "type", "status", "time"]
            for td in tr.find_all("td"):
                if len(td.get_text().strip()) > 0:
                    machine[types[index]] = td.get_text().strip()
                    index += 1
            if len(machine) > 0:
                result.append(machine)

    return result

def queryEsuds(buttomLocationId):
    queryUrl = domain + str(buttomLocationId)
    soup = getWebpageSource(queryUrl)
    return soup

# gets a BeautifulSoup object of the given url's source
def getWebpageSource(url):
    ua = UserAgent()
    headers = { "Connection": "close", "User-Agent": ua.random }
    r = requests.get(url, headers = headers, timeout = 20)
    return BeautifulSoup(r.text, "html.parser")

# getUrl(2829)
