import requests
import regex as re
from bs4 import BeautifulSoup as bs


def getURLfromNumber(number):
    try:
        m = re.search("H. [0-9]+", number)
        Heft = m.group(0).replace("H. ", "")
        URL = (
            "http://www.regesta-imperii.de/regesten/13-"
            + Heft
            + "-0-friedrich-iii.html"
        )
    except AttributeError:
        URL = "http://www.regesta-imperii.de/regesten/13-0-2-friedrich-iii.html"
    req = requests.get(URL)
    soup = bs(req.text, "html.parser")
    items = soup.find_all("p", {"class": "departement"})
    for item in items:
        for a in item.find_all("a"):
            if a.text == number:
                for button in item.find_all_next("p"):
                    URIs = button.find_all("a")
                    for u in URIs:
                        if u.text == "URI":
                            return u["href"]
    list = soup.find("ul", {"class": "pagination"})
    pages = list.find_all("a", {"class": "button"})
    URI = findURIinPages(pages, number)
    while URI != None:
        list = soup.find("ul", {"class": "pagination"})
        page = list.find("a", {"class": "button"})["href"]
        req = requests.get(page)
        soup = bs(req.text, "html.parser")
        list = soup.find("ul", {"class": "pagination"})
        pages = list.find_all("a", {"class": "button"})
        URI = findURIinPages(pages, number)
        return URI


def findURIinPages(pages, number):
    for page in pages:
        req = requests.get(page["href"])
        soup = bs(req.text, "html.parser")
        items = soup.find_all("p", {"class": "departement"})
        for item in items:
            for a in item.find_all("a"):
                if a.text == number:
                    for button in item.find_all_next("p"):
                        URIs = button.find_all("a")
                        for u in URIs:
                            if u.text == "URI":
                                return u["href"]
