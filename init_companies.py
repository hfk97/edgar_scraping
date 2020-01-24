# import all necessary packages
import subprocess
import sys
import importlib


# function that imports a library if it is installed, else installs it and then imports it
def getpack(package):
    try:
        return importlib.import_module(package)
        # import package
    except ImportError:
        subprocess.call([sys.executable, "-m", "pip", "install", package])
        return importlib.import_module(package)
        # import package

bs4 = getpack("bs4")
from bs4 import BeautifulSoup
urllib = getpack("urllib")
#request = getpack("urllib.request")
from urllib.request import Request
import pickle


def save_obj(obj, name):
    with open(name+".pkl", 'wb') as pickle_file:
        pickle.dump(obj, pickle_file, pickle.HIGHEST_PROTOCOL)


def load_obj(name):
    with open(name+".pkl", 'rb') as pickle_file:
        return pickle.load(pickle_file)


# initialize the companies dictionary
def initialize_companies(tickers):
    # create the empty dictionary
    Companies = {}

    n = 0
    # for every ticker in the list of tickers extract name and CIK from EDGAR and store them in the dictionary
    for i in tickers:
        print(f"Initializing companies. ({n}/{len(tickers)})", end='\r')
        if "." in i:
            i = i.replace(".", "")

        base_request = "https://sec.report/Ticker/"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'}
        req = Request(url=base_request + i, headers=headers)

        try:
            page = urllib.request.urlopen(req)  # connect to website
        except:
            print("An error occured with: " + i)
            continue

        navigate = BeautifulSoup(page, 'html.parser')

        name = navigate.h1.text.split(":", 1)[1].strip()

        CIK = navigate.h2.text.split("CIK", 1)[1].strip()

        Companies[i] = [i, name, CIK]
        n += 1

    # save the newly collected identifiers
    save_obj(Companies, "companies")

    return
