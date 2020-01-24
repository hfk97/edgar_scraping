# import the packages needed for getpack() function
import subprocess
import sys
import importlib


# function that imports a library if it is installed, else installs it and then imports it
def getpack(package):
    try:
        return (importlib.import_module(package))
        # import package
    except ImportError:
        subprocess.call([sys.executable, "-m", "pip", "install", package])
        return (importlib.import_module(package))
        # import package


# urllib enables us to work with urls
urllib = getpack("urllib")
request = getpack("urllib.request")
from urllib.request import Request

# beautiful soup 4 is a powerful package that allows us to easily process html code
bs4 = getpack("bs4")
from bs4 import BeautifulSoup

# pickle allows us to store python objects, in this case dictionnairies, we will use it to store important
# information across sessions
import pickle


# This function takes a web-adress as input and returns the parsed html elements
def make_soup(url):
    headers = {
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'}
    req = Request(url, headers=headers)
    try:
        page = urllib.request.urlopen(req)  # conntect to website
    except:
        print("An error occured.")
    try:
        soup = BeautifulSoup(page, 'html.parser')
    except UnboundLocalError:
        print("The data could not be requested, please check your internet connection and try again.\n")
        sys.exit()

    return soup


# this function saves a python object (obj) under a specified name
def save_obj(obj, name):
    with open(name+".pkl", 'wb') as pickle_file:
        pickle.dump(obj, pickle_file, pickle.HIGHEST_PROTOCOL)


# this function loads a pickled object
def load_obj(name):
    with open(name+".pkl", 'rb') as pickle_file:
        return pickle.load(pickle_file)


# this function takes a start and endyear, as well as a list of tickers and returns a list containing the urls
# under which the respective 10ks can be found
def main(startyear, endyear, tickers):

    global queue
    queue = []

    # load and else initialize the processed_links log
    try:
        processed_links = load_obj("processed_links")
    except FileNotFoundError:
        processed_links = {}

    for i in tickers:
        if i[0] not in processed_links:
            processed_links[i[0]] = []

    # for each selected ticker
    for t in tickers:
        # explaing the exact steps that follow would require me telling you more about the EDGAR website structure
        # all you need to know is that it find the links to all Form 10-Ks within the selected time period
        # and appends them to the queue, if they have not been processed before
        CIK = t[2]

        url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={CIK}&type=10-K&dateb=&owner=exclude&count=40"

        print(f"Searching for: {t}.\n")

        soup = make_soup(url)

        for table in soup.findAll('table'):
            allrows = []
            for row in table.findAll('tr'):
                rowdata = []
                for column in row.findAll('td'):
                    if len(column.findAll('a', href=True)) != 0:
                        rowdata.append("https://www.sec.gov/" + column.findAll('a', href=True)[0]['href'])
                    else:
                        rowdata.append(column.text)
                allrows.append(rowdata)

            for i in allrows:
                try:
                    if i[0] == '10-K':
                        year = int(i[3][0:4])
                        if startyear <= year <= endyear:

                            minisoup = make_soup(i[1])

                            for table in minisoup.findAll('table'):
                                allrows = []
                                for row in table.findAll('tr'):
                                    if "10-K" in row.text:
                                        newlink = "https://www.sec.gov/" + row.findAll('a', href=True)[0]["href"]

                                        if newlink not in processed_links[t[0]]:
                                            queue.append((t, newlink, int(i[3][0:4]) - 1))
                                            processed_links[t[0]].append(newlink)

                except IndexError:
                    continue

    if len(queue) > 0:
        save_obj(processed_links, "processed_links")
        return queue

    else:
        print("Something went wrong no new data was found or data already initialized")
        return None

