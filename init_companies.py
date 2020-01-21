import subprocess
import sys
import importlib

from urllib.request import Request
import pickle

# function that imports a library if it is installed, else installs it and then imports it
def getpack(package):
    try:
        return (importlib.import_module(package))
        # import package
    except ImportError:
        subprocess.call([sys.executable, "-m", "pip", "install", package])
        return (importlib.import_module(package))
        # import package

bs4=getpack("bs4")
from bs4 import BeautifulSoup
urllib=getpack("urllib")
request=getpack("urllib.request")
re=getpack("re")


def save_obj(obj, name ):
    with open(name+".pkl", 'wb') as pickle_file:
        pickle.dump(obj, pickle_file,pickle.HIGHEST_PROTOCOL)


def load_obj(name ):
    with open(name+".pkl", 'rb') as pickle_file:
        return pickle.load(pickle_file)

# get the tickers of all stocks in the SP500
def sp500_tickers():
    resp = requests.get('http://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    soup = bs.BeautifulSoup(resp.text, 'lxml')
    table = soup.find('table', {'class': 'wikitable sortable'})
    tickers = []
    for row in table.findAll('tr')[1:]:
        ticker = row.findAll('td')[0].text
        ticker = ticker.replace("\n","")
        tickers.append(ticker)

    return tickers


def initialize_companies():
    # do this dynamically
    SP500 = sp500_tickers()

    Companies={}

    n=0
    #for i in sample:
    for i in SP500:
        print(f"Initializing companies. ({n}/{len(SP500)})", end='\r')
        if "." in i:
            i=i.replace(".","")

        base_request = "https://sec.report/Ticker/"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'}
        req = Request(url=base_request + i, headers=headers)

        try:
            page = urllib.request.urlopen(req)  # conntect to website
        except:
            print("An error occured with: " + i)
            continue

        navigate = BeautifulSoup(page, 'html.parser')

        name = navigate.h1.text.split(":", 1)[1].strip()

        CIK = navigate.h2.text.split("CIK", 1)[1].strip()

        Companies[i] = [i, name, CIK]
        n+=1

    save_obj(Companies, "companies")

    return

initialize_companies()




