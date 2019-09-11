import subprocess
import sys
import importlib
import os



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
datetime=getpack("datetime")

import pandas as pd
import pickle
from urllib.request import Request

def load_obj(name ):
    with open(name+".pkl", 'rb') as pickle_file:
        return pickle.load(pickle_file)


def make_soup(ticker,url,date):

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'}
    req = Request(url, headers=headers)

    try:
        page = urllib.request.urlopen(req)  # conntect to website

    except:
        print("An error occured with the data request to SEC databank, check your internet connection.")

    soup = BeautifulSoup(page, 'html.parser')
    parse10k(ticker,soup,date)


def gettables(soup):

    tables=[]

    for table in soup.findAll('table'):
        newtable={}
        #print(table)
        for row in table.findAll('tr'):
            rowdata=[]
            for column in row.findAll('td'):
                rowdata.append(column.text.strip(" "))
                #print(column.text)

            for n,i in enumerate(rowdata):
                rowdata[n]=" ".join(i.split())
                pattern=re.compile(r'^\(\d+[.,]?\d*$')

                if pattern.match(rowdata[n]) is not None:
                    rowdata[n]=rowdata[n].replace('(','-')

            #dropitems = ["\xa0", '','$',"\n"]
            dropitems = ['', '$',')']


            for i in dropitems:
                while i in rowdata:
                    rowdata.remove(i)

            if len(rowdata)>4:
                ok=re.compile("\(?-?\d+(,\d+)?\)?")
                for n,i in enumerate(rowdata):
                    if n>0 and ok.match(i) is None:
                        rowdata.remove(rowdata[n])
                        break

            if len(rowdata)>2:
                newtable[rowdata[0]]= rowdata[1:]


        if len(newtable)>0:
            tables.append(newtable)
        del newtable

    del table

    return(tables)




def parse10k(ticker,soup, date):
    tables = gettables(soup)

    processing_log=""
    processing_log+="Log of " + ticker + str(date) +"\n"

    tcas = re.compile("total\scurrent\sassets")
    tcls = re.compile("total\scurrent\sliabilities")
    tas = re.compile("total\sassets")

    rev = re.compile("\w*\s?revenue[s]?||Net Sales")
    ninc = re.compile("net?\s?(\(loss\))?\s?income\s?(\(loss\))?")
    #inctax = re.compile("\D*income\stax\s\D*")
    inctax = re.compile("(\D*\s?(for)?income\stax{1}(es)?\s?\D*)||(Provision for taxes)")

    ncpoa = re.compile("(net\s)?cash\s\D+\soperating\sactivities$")
    ncpia = re.compile("(net\s)?cash\s\D+\sinvesting\sactivities$")
    ncpfa = re.compile("(net\s)?cash\s\D+\sfinancing\sactivities$")


    balance_patterns = [tcas, tcls, tas]

    income_patterns = [rev, ninc, inctax]

    cash_flow_patterns = [ncpoa, ncpia, ncpfa]

    inc_found = False
    balance_found = False
    cash_found = False

    for i in tables:

        if not balance_found:
            if all(any(j.match(v.lower()) is not None for v in i)for j in balance_patterns):
                #print("Balance sheet: ", i)
                try:
                    balance_sheet_dict = i
                    balance_sheet = pd.DataFrame.from_dict(balance_sheet_dict, orient='index',
                                                           columns=[int(date), int(date) - 1])
                    balance_found = True
                except AssertionError as e:
                    processing_log+="balance_sheet_ASSERTION_ERROR" + str(e) + "\n"
                    pass

        if not inc_found:
            if all(any(j.match(v.lower()) is not None for v in i)for j in income_patterns):
                #print("Income statement: ", i)
                try:
                    operation_statement_dict = i
                    # break to avoid catching adjusted stuff
                    operation_statement = pd.DataFrame.from_dict(operation_statement_dict, orient='index',
                                                                 columns=[int(date), int(date) - 1, int(date) - 2])
                    operation_statement = operation_statement.iloc[1:]
                    inc_found = True
                except AssertionError as e:
                    processing_log+="operation_statement_ASSERTION_ERROR"+str(e)+"\n"
                    pass

        if not cash_found:
            if all(any(j.match(v.lower()) is not None for v in i)for j in cash_flow_patterns):
                #print("Cashflow statement: ", i)
                try:
                    cash_flow_statement_dict = i
                    cash_flow_statement = pd.DataFrame.from_dict(cash_flow_statement_dict, orient='index',
                                                                 columns=[int(date), int(date) - 1, int(date) - 2])
                    cash_flow_statement = cash_flow_statement.iloc[1:]
                    cash_found = True
                except AssertionError as e:
                    processing_log+="cash_flow_statement_ASSERTION_ERROR"+str(e)+"\n"
                    pass

    #print(processing_log)
    del processing_log
    export_to_csv(ticker, date, balance_sheet, operation_statement, cash_flow_statement)





def export_to_csv(ticker,year,balance,operation,cash):

    if not os.path.exists("./EdgarData"):
        os.makedirs("EdgarData")
    if not os.path.exists("./EdgarData/"+ticker):
        os.makedirs("./EdgarData/"+ticker)
    if not os.path.exists("./EdgarData/"+ticker+"/"+str(year)):
        os.makedirs("./EdgarData/" + ticker + "/" + str(year))

        balance.to_csv (r"./EdgarData/" + ticker + "/" + str(year) + "/" + ticker+str(year)+"Balance_Sheet.csv")
        operation.to_csv(r"./EdgarData/" + ticker + "/" + str(year) + "/" + ticker + str(year) + "Operation_Statement.csv")
        cash.to_csv(r"./EdgarData/" + ticker + "/" + str(year) + "/" + ticker + str(year) + "Cashflow_statement.csv")

        print("Successfull extraction - "+ticker+str(year))

    else:
        print("This data already exists")




#10ks
#https://www.sec.gov/Archives/edgar/data/2488/000000248819000011/amd-12292018x10k.htm
#https://www.sec.gov/Archives/edgar/data/1652044/000165204419000004/goog10-kq42018.htm#s60D13494C77354D8AED0E72D61E53B98
#https://www.sec.gov//Archives/edgar/data/1045810/000104581011000015/fy2011form10k.htm

make_soup("AMAT","https://www.sec.gov//Archives/edgar/data/6951/000000695116000068/amat10302016-10k.htm#sA39551AE2B055A83BF22C4A6C722F33F","2016")