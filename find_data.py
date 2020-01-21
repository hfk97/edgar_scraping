import subprocess
import sys
import importlib
from urllib.request import Request

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



def make_soup(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'}
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


import pickle


def save_obj(obj, name ):
    with open(name+".pkl", 'wb') as pickle_file:
        pickle.dump(obj, pickle_file,pickle.HIGHEST_PROTOCOL)


def load_obj(name ):
    with open(name+".pkl", 'rb') as pickle_file:
        return pickle.load(pickle_file)



def main(startyear=2015,endyear=2018,tickers=None):

    print("companies.pkl is missing. The program now need to initialize all SP500 companies. This might take some time.")
    try:
        companies
    except NameError:
        try:
            companies=load_obj("companies")

        except FileNotFoundError:
            import init_companies
            companies=load_obj("companies")

    global queue
    queue=[]

    try:
        processed_links
    except NameError:
        try:
            processed_links=load_obj("processed_links")
        except FileNotFoundError:
            processed_links={}
            for i in companies:
                processed_links[i]=[]


    newlinks=0

    for t in tickers:

        if t in companies.keys():

            CIK = companies[t][2]

            url = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=" + str(
                CIK) + "&type=10-K&dateb=&owner=exclude&count=40"

            print("Handling: " + t + ". \n")

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
                            if year >= startyear and year <=endyear:

                                minisoup = make_soup(i[1])

                                for table in minisoup.findAll('table'):
                                    allrows = []
                                    for row in table.findAll('tr'):
                                        if "10-K" in row.text:
                                            newlink="https://www.sec.gov/" + row.findAll('a', href=True)[0]["href"]

                                            if newlink not in processed_links[t]:
                                                queue.append((t, newlink,int(i[3][0:4]) - 1))
                                                processed_links[t].append(newlink)
                                                if newlinks == 0:
                                                    newlinks = 1


                    except IndexError:
                        continue


    if newlinks==1:
        save_obj(processed_links, "processed_links")
        return queue

    else:
        print("Something went wrong no new data was found or data already initialized")
        return None

if __name__ == "__main__":
    main(2008,2014,["INTC","AMD","AMAT"])