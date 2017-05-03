from string import ascii_letters
import requests
import sys
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import time

domain = ".esuds.net/RoomStatus/machineStatus.i?bottomLocationId="

def scrape(root, hall_id):
    return getMachines("http://" + root + domain + str(hall_id))

def getMachines(queryUrl):
    soup = getWebpageSource(queryUrl)
    machines = parseEsuds(soup)
    if (machines == None):
        return None
    return machines

def parseEsuds(soup):
    result = []

    table = soup.find("table", {"class": "room_status"})
    tableHead = 0
    if table:
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
                if len(machine) >= 2:
                    result.append(machine)

    return result

# gets a BeautifulSoup object of the given url's source
def getWebpageSource(url):
    ua = UserAgent()
    headers = { "Connection": "close", "User-Agent": ua.random }
    r = ''
    while r == '':
        try:
            r = requests.get(url, headers = headers, timeout = 5)
        except:
            print("Connection refused by the server..")
            print(url)
            time.sleep(5)
            continue

    return BeautifulSoup(r.text, "html.parser")
