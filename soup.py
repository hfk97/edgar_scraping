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

bs4=getpack("bs4")
from bs4 import BeautifulSoup
urllib=getpack("urllib")
request=getpack("urllib.request")
re=getpack("re")

import pandas as pd
import pickle
from urllib.request import Request

def load_obj(name ):
    with open(name+".pkl", 'rb') as pickle_file:
        return pickle.load(pickle_file)


def make_soup(url):

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'}
    req = Request(url, headers=headers)

    try:
        page = urllib.request.urlopen(req)  # conntect to website

    except:
        print("An error occured.")

    soup = BeautifulSoup(page, 'html.parser')
    return soup


try:
    companies
except NameError:
    try:
        companies=load_obj("sample_companies")
        #companies=load_obj("companies")

    except FileNotFoundError:
        import init_companies
        companies=load_obj("sample_companies")
        #companies=load_obj("companies")




def identify(s):


    possible_tenk="10k","10K","10-k","10-K"
    possible_tenq="10q","10Q","10-q","10-Q"
    possible_quaters="q1","q2","q3","q4"

    for i in possible_tenk:
        if i in s:
            type="10k"
            type2="annual"

    for i in possible_tenq:
        if i in s:
            type="10q"
        for j in possible_quaters:
            if j in s:
                type2=j

    return(type,type2)


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




def parse10k(soup, date):
    tables = gettables(soup)

    tcas = re.compile("total\scurrent\sassets")
    tcls = re.compile("total\scurrent\sliabilities")
    tas = re.compile("total\sassets")

    rev = re.compile("\w*\s?revenue[s]?")
    ninc = re.compile("net?\s?(\(loss\))?\s?income\s?(\(loss\))?")
    #inctax = re.compile("\D*income\stax\s\D*")
    inctax = re.compile("(\D*\s?(for)?income\stax{1}(es)?\s?\D*)||(Provision for taxes)")

    ncpoa = re.compile("net\scash\s\D+\soperating\sactivities$")
    ncpia = re.compile("net\scash\s\D+\sinvesting\sactivities$")
    ncpfa = re.compile("net\scash\s\D+\sfinancing\sactivities$")


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
                    print("balance_sheet_ASSERTION_ERROR")
                    print(e)
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
                    print("operation_statement_ASSERTION_ERROR")
                    print(e)
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
                    print("cash_flow_statement_ASSERTION_ERROR")
                    print(e)
                    pass



    return balance_sheet, operation_statement, cash_flow_statement




def update_mode():
    import RSS_monitor

    queue=RSS_monitor.main()

    for q in queue:
        print(q)

        ticker = q[0]
        soup = make_soup(q[1])


        if "10-K" in soup.title.text:
            filing = "10k"

        else:
            raise Exception("A non 10-K form was handed to 10-K processing")

        year=q[2]

        try:
            balance_sheet, operation_statement, cash_flow_statement = parse10k(soup, year)

        except UnboundLocalError as e:
            print(e)
            print(q[1]+"\n")

        except AssertionError as e:
            print(e)
            print(q[1]+"\n")





def initialize_db10k():
    import init_data as ini
    queue=ini.main()
    issue_log=[]
    for q in queue:
        #print(q)

        ticker = q[0]
        soup = make_soup(q[1])

        year=q[2]

        #print(q[1])

        try:
            balance_sheet, operation_statement, cash_flow_statement = parse10k(soup, year)
            print("done \n")

        except UnboundLocalError as e:
            print(e)
            print(q[1]+"\n")
            issue_log.append(str(e)+q[1]+"\n")

        except AssertionError as e:
            print(e)
            print(q[1]+"\n")
            issue_log.append(str(e)+q[1]+"\n")

    print(issue_log)


initialize_db10k()



#ToDo: 10ks
#soup = make_soup("https://www.sec.gov/Archives/edgar/data/2488/000000248819000011/amd-12292018x10k.htm")
#soup=make_soup("https://www.sec.gov/Archives/edgar/data/1652044/000165204419000004/goog10-kq42018.htm#s60D13494C77354D8AED0E72D61E53B98")






sys.exit()

#ToDo Improve parsing


soup=make_soup("https://www.sec.gov//Archives/edgar/data/1045810/000104581011000015/fy2011form10k.htm")



filing,spec=identify(soup.filename.text.split("\n", 1)[0])

ticker='AMD'

if filing=='10k':
    s=soup.filename.text.split("\n", 1)[0]
    for i, n in enumerate(s):
        if n=="2" and s[i+1]=="0":
            year = s[i:i + 4]
            break

try:
    balance_sheet, operation_statement, cash_flow_statement = parse10k(soup, year)

except UnboundLocalError as e:
    print(e)
    print("here")



tables = gettables(soup)


#Todo fix issues from terminal

#Provision for taxes
inctax = re.compile("(\D*\s?(for)?income\stax{1}(es)?\s?\D*)||(Provision for taxes)")