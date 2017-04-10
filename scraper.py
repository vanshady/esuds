from string import ascii_letters
import requests
import sys
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import time

domain = "http://jhu.esuds.net/RoomStatus/machineStatus.i?bottomLocationId="

def getUrl(hall_id):
    soup = queryEsuds(hall_id)
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

def queryEsuds(hall_id):
    queryUrl = domain + str(hall_id)
    soup = getWebpageSource(queryUrl)
    return soup

# gets a BeautifulSoup object of the given url's source
def getWebpageSource(url):
    ua = UserAgent()
    headers = { "Connection": "close", "User-Agent": ua.random }
    r = requests.get(url, headers = headers, timeout = 20)
    return BeautifulSoup(r.text, "html.parser")

# starttime=time.time()
# idList = {
#     'AMR-A': [2829],
#     'AMR-B': [2831],
#     'AMR-I': [2824],
#     'AMR-II': [2826, 2827],
#     'bradford': [2835],
#     'commons': [2841],
#     'mccoy': [1015524, 1015507],
#     'wolman': [2839],
#     'rogers': [2074912],
# }
#
# hopkins = {}
# while True:
#     for hall, ids in idList.items():
#         machines = []
#         for hall_id in ids:
#             machines += getUrl(hall_id)
#         hopkins["hall"] = machines
#
#     time.sleep(30.0 - ((time.time() - starttime) % 30.0))
