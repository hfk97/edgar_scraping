# import the necessary packages
import subprocess
import sys
import importlib
import os


# function that imports a library if it is installed, else installs it and then imports it
def getpack(package):
    try:
        return importlib.import_module(package)
    except ImportError:
        subprocess.call([sys.executable, "-m", "pip", "install", package])
        return importlib.import_module(package)


bs4 = getpack("bs4")
from bs4 import BeautifulSoup
urllib = getpack("urllib")
request = getpack("urllib.request")
from urllib.request import Request
import pickle
# pandas allows us to create dataframes
import pandas as pd

# re is the regex package we will use to search specific (sub-)strings
re = getpack("re")
# datetime helps us handel date formatting
datetime = getpack("datetime")


def load_obj(name):
    with open(name+".pkl", 'rb') as pickle_file:
        return pickle.load(pickle_file)


# function that takes a ticker, url and date, adds a soup object for the respective url and hands the data to parse10k
def make_soup(ticker, url, date):

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'}
    req = Request(url, headers=headers)

    try:
        page = urllib.request.urlopen(req)  # connect to website

    except:
        print("An error occured with the data request to SEC databank, check your internet connection.")

    soup = BeautifulSoup(page, 'html.parser')

    return parse10k(ticker, soup, date, url)


# this function extracts and returns all tables from the soup handed to it
def gettables(soup):

    tables = []

    for table in soup.findAll('table'):
        newtable = {}
        for row in table.findAll('tr'):
            rowdata = []
            for column in row.findAll('td'):
                rowdata.append(column.text.strip(" "))

            for n, i in enumerate(rowdata):
                rowdata[n] = " ".join(i.split())
                pattern = re.compile(r'^\(\d+[.,]?\d*$')

                if pattern.match(rowdata[n]) is not None:
                    rowdata[n] = rowdata[n].replace('(', '-')

            dropitems = ['', '$', ')']

            for i in dropitems:
                while i in rowdata:
                    rowdata.remove(i)

            if len(rowdata) > 4:
                ok = re.compile("\(?-?\d+(,\d+)?\)?")
                for n, i in enumerate(rowdata):
                    if n > 0 and ok.match(i) is None:
                        rowdata.remove(rowdata[n])
                        break

            if len(rowdata) > 2:
                newtable[rowdata[0]] = rowdata[1:]

        if len(newtable) > 0:
            tables.append(newtable)
        del newtable

    del table

    return tables


# this function is the main function used to parse Form 10K filings. Arguments: ticker, soup object, date and url
def parse10k(ticker, soup, date, url):

    tables = gettables(soup)

    # the processing log established here is not displayed by default but can be used to troubleshoot if need be
    processing_log = ""
    processing_log += f"Log of {ticker}{date}\n"

    # to identify balance sheet, income and cashflow statements I have collected the following substring patterns
    tcas = re.compile("total\scurrent\sassets")
    tcls = re.compile("total\scurrent\sliabilities")
    tas = re.compile("total\sassets")

    rev = re.compile("\w*\s?revenue[s]?|| Net Sales")
    ninc = re.compile("net?\s?(\(loss\))?\s?((loss)|(income))\s?(\(loss\))?")
    inctax = re.compile("(\D*\s?(for)?income\stax{1}(es)?\s?\D*)||(Provision for\s(income\s)?taxes)")

    ncpoa = re.compile("(net\s)?cash\s\D+\soperating\sactivities$")
    ncpia = re.compile("(net\s)?cash\s\D+\sinvesting\sactivities$")
    ncpfa = re.compile("(net\s)?cash\s\D+\sfinancing\sactivities$")

    balance_patterns = [tcas, tcls, tas]
    income_patterns = [rev, ninc, inctax]
    cash_flow_patterns = [ninc, ncpoa, ncpia, ncpfa]

    # these will keep track of which tables have been found
    inc_found = False
    balance_found = False
    cash_found = False

    # the following for loop goes through all tables in a document, identifies whether they are on of the 3 we are
    # looking for and saves it if so.
    for i in tables:

        if not balance_found:
            if all(any(j.match(v.lower()) is not None for v in i)for j in balance_patterns):
                try:
                    balance_sheet_dict = i
                    balance_sheet = pd.DataFrame.from_dict(balance_sheet_dict, orient='index',
                                                           columns=[int(date), int(date) - 1])
                    balance_found = True
                except AssertionError as e:
                    processing_log += f"balance_sheet_ASSERTION_ERROR {e}\n"
                    pass

        if not inc_found:
            if all(any(j.match(v.lower()) is not None for v in i)for j in income_patterns):
                try:
                    operation_statement_dict = i
                    # break to avoid catching adjusted stuff
                    operation_statement = pd.DataFrame.from_dict(operation_statement_dict, orient='index',
                                                                 columns=[int(date), int(date) - 1, int(date) - 2])
                    operation_statement = operation_statement.iloc[1:]
                    inc_found = True
                except AssertionError as e:
                    processing_log += f"operation_statement_ASSERTION_ERROR {e}\n"
                    pass

        if not cash_found:
            if all(any(j.match(v.lower()) is not None for v in i)for j in cash_flow_patterns):
                try:
                    cash_flow_statement_dict = i
                    cash_flow_statement = pd.DataFrame.from_dict(cash_flow_statement_dict, orient='index',
                                                                 columns=[int(date), int(date) - 1, int(date) - 2])
                    cash_flow_statement = cash_flow_statement.iloc[1:]
                    cash_found = True

                    if "Fiscal Year" in cash_flow_statement.iloc[0].name:
                        cash_flow_statement.drop("Fiscal Year", inplace=True)

                except AssertionError as e:
                    processing_log += f"cash_flow_statement_ASSERTION_ERROR {e}\n"
                    pass
    # uncomment the line below for troubleshooting purposes
    # print(processing_log)
    del processing_log

    # upon completion of the for loop we export the data
    try:
        return export_to_csv(ticker, date, balance_sheet, operation_statement, cash_flow_statement, url)

    # if the export is not possible, due to the program not being able to extract the tables sought after, the full Form
    # 10-K is downloaded for manual inspection
    except UnboundLocalError as e:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'}
        req = Request(url, headers=headers)
        page = urllib.request.urlopen(req)
        filing = page.read()
        with open(f"./EdgarData/{ticker}/{date}/{ticker}{date}10k.html", 'w') as f:
            f.write(filing.decode('utf-8'))

        return f"There was an issue during data extraction (UnboundLocalError:{e}) for {ticker}{date} " \
            f"the respective 10k was downloaded and saved for manual inspection. For reasons please consider the " \
            f"limitations in this projects Readme file.\n"


def export_to_csv(ticker, year, balance, operation, cash, url):
    # if the following folder structure does not exist yet, create it
    if not os.path.exists("./EdgarData"):
        os.makedirs("EdgarData")
    if not os.path.exists(f"./EdgarData/{ticker}"):
        os.makedirs(f"./EdgarData/{ticker}")
    if not os.path.exists(f"./EdgarData/{ticker}/{year}"):
        os.makedirs(f"./EdgarData/{ticker}/{year}")

        # export the tables
        balance.to_csv(rf"./EdgarData/{ticker}/{year}/{ticker}{year}Balance_Sheet.csv")
        operation.to_csv(rf"./EdgarData/{ticker}/{year}/{ticker}{year}Operation_Statement.csv")
        cash.to_csv(rf"./EdgarData/{ticker}/{year}/{ticker}{year}Cashflow_statement.csv")

        headers = {
            'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'}
        req = Request(url, headers=headers)

        page = urllib.request.urlopen(req)

        filing = page.read()
        # add the full 10-K, in-case the user wants to see other details
        with open(f"./EdgarData/{ticker}/{year}/{ticker}{year}10k.html", 'w') as f:
            f.write(filing.decode('utf-8'))

        return f"Successful extraction - {ticker}{year}"

    else:
        return "This data already exists"
