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


#delete companies part here


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

    processing_log=[]
    processing_log.append("Log of" + str(soup.filename))

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
                    processing_log.append("balance_sheet_ASSERTION_ERROR" + str(e) + "\n")
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
                    processing_log.append("operation_statement_ASSERTION_ERROR"+str(e)+"\n")
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
                    processing_log.append("cash_flow_statement_ASSERTION_ERROR"+str(e)+"\n")
                    pass

    print(processing_log)
    return balance_sheet, operation_statement, cash_flow_statement




def update_mode():
    import RSS_monitor
    issue_log=[]
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
            issue_log.append("Log of" + str(q))
            balance_sheet, operation_statement, cash_flow_statement = parse10k(soup, year)
            issue_log.append("Tables found")

        except UnboundLocalError as e:
            print(e)
            print(q[1] + "\n")
            issue_log.append(str(e) + q[1] + "\n")
            print(issue_log)

        except AssertionError as e:
            print(e)
            print(q[1] + "\n")
            issue_log.append(str(e) + q[1] + "\n")
            print(issue_log)





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
            issue_log.append("Log of"+ str(q))
            balance_sheet, operation_statement, cash_flow_statement = parse10k(soup, year)
            issue_log.append("Tables found")

        except UnboundLocalError as e:
            print(e)
            print(q[1]+"\n")
            issue_log.append(str(e)+q[1]+"\n")
            print(issue_log)

        except AssertionError as e:
            print(e)
            print(q[1]+"\n")
            issue_log.append(str(e)+q[1]+"\n")
            print(issue_log)



def export_to_csv(ticker,year,balance,operation,cash):

    if not os.path.exists("./EdgarData"):
        os.makedirs("EdgarData")
    if not os.path.exists("./EdgarData/"+ticker):
        os.makedirs("./EdgarData/"+ticker)
    if not os.path.exists("./EdgarData/"+ticker+"/"+year):
        os.makedirs("./EdgarData/" + ticker + "/" + year)

        balance.to_csv (r"./EdgarData/" + ticker + "/" + year + "/" + ticker+year+"Balance_Sheet.csv")
        operation.to_csv(r"./EdgarData/" + ticker + "/" + year + "/" + ticker + year + "Operation_Statement.csv")
        cash.to_csv(r"./EdgarData/" + ticker + "/" + year + "/" + ticker + year + "Cashflow_statement.csv")

    else:
        print("This data already exists")





def main_menu():
    print("started")
    SP500 = ["MMM", "ABT", "ABBV", "ABMD", "ACN", "ATVI", "ADBE", "AMD", "AAP", "AES", "AMG", "AFL", "A", "APD", "AKAM",
             "ALK", "ALB", "ARE", "ALXN", "ALGN", "ALLE", "AGN", "ADS", "LNT", "ALL", "GOOGL", "GOOG", "MO", "AMZN",
             "AMCR", "AEE", "AAL", "AEP", "AXP", "AIG", "AMT", "AWK", "AMP", "ABC", "AME", "AMGN", "APH", "APC", "ADI",
             "ANSS", "ANTM", "AON", "AOS", "APA", "AIV", "AAPL", "AMAT", "APTV", "ADM", "ARNC", "ANET", "AJG", "AIZ",
             "ATO", "T", "ADSK", "ADP", "AZO", "AVB", "AVY", "BHGE", "BLL", "BAC", "BK", "BAX", "BBT", "BDX", "BRK.B",
             "BBY", "BIIB", "BLK", "HRB", "BA", "BKNG", "BWA", "BXP", "BSX", "BMY", "AVGO", "BR", "BF.B", "CHRW", "COG",
             "CDNS", "CPB", "COF", "CPRI", "CAH", "KMX", "CCL", "CAT", "CBOE", "CBRE", "CBS", "CE", "CELG", "CNC",
             "CNP", "CTL", "CERN", "CF", "SCHW", "CHTR", "CVX", "CMG", "CB", "CHD", "CI", "XEC", "CINF", "CTAS", "CSCO",
             "C", "CFG", "CTXS", "CLX", "CME", "CMS", "KO", "CTSH", "CL", "CMCSA", "CMA", "CAG", "CXO", "COP", "ED",
             "STZ", "COO", "CPRT", "GLW", "CTVA", "COST", "COTY", "CCI", "CSX", "CMI", "CVS", "DHI", "DHR", "DRI",
             "DVA", "DE", "DAL", "XRAY", "DVN", "FANG", "DLR", "DFS", "DISCA", "DISCK", "DISH", "DG", "DLTR", "D",
             "DOV", "DOW", "DTE", "DUK", "DRE", "DD", "DXC", "ETFC", "EMN", "ETN", "EBAY", "ECL", "EIX", "EW", "EA",
             "EMR", "ETR", "EOG", "EFX", "EQIX", "EQR", "ESS", "EL", "EVRG", "ES", "RE", "EXC", "EXPE", "EXPD", "EXR",
             "XOM", "FFIV", "FB", "FAST", "FRT", "FDX", "FIS", "FITB", "FE", "FRC", "FISV", "FLT", "FLIR", "FLS", "FMC",
             "FL", "F", "FTNT", "FTV", "FBHS", "FOXA", "FOX", "BEN", "FCX", "GPS", "GRMN", "IT", "GD", "GE", "GIS",
             "GM", "GPC", "GILD", "GPN", "GS", "GWW", "HAL", "HBI", "HOG", "HIG", "HAS", "HCA", "HCP", "HP", "HSIC",
             "HSY", "HES", "HPE", "HLT", "HFC", "HOLX", "HD", "HON", "HRL", "HST", "HPQ", "HUM", "HBAN", "HII", "IDXX",
             "INFO", "ITW", "ILMN", "IR", "INTC", "ICE", "IBM", "INCY", "IP", "IPG", "IFF", "INTU", "ISRG", "IVZ",
             "IPGP", "IQV", "IRM", "JKHY", "JEC", "JBHT", "JEF", "SJM", "JNJ", "JCI", "JPM", "JNPR", "KSU", "K", "KEY",
             "KEYS", "KMB", "KIM", "KMI", "KLAC", "KSS", "KHC", "KR", "LB", "LHX", "LH", "LRCX", "LW", "LEG", "LEN",
             "LLY", "LNC", "LIN", "LKQ", "LMT", "L", "LOW", "LYB", "MTB", "MAC", "M", "MRO", "MPC", "MKTX", "MAR",
             "MMC", "MLM", "MAS", "MA", "MKC", "MXIM", "MCD", "MCK", "MDT", "MRK", "MET", "MTD", "MGM", "MCHP", "MU",
             "MSFT", "MAA", "MHK", "TAP", "MDLZ", "MNST", "MCO", "MS", "MOS", "MSI", "MSCI", "MYL", "NDAQ", "NOV",
             "NKTR", "NTAP", "NFLX", "NWL", "NEM", "NWSA", "NWS", "NEE", "NLSN", "NKE", "NI", "NBL", "JWN", "NSC",
             "NTRS", "NOC", "NCLH", "NRG", "NUE", "NVDA", "ORLY", "OXY", "OMC", "OKE", "ORCL", "PCAR", "PKG", "PH",
             "PAYX", "PYPL", "PNR", "PBCT", "PEP", "PKI", "PRGO", "PFE", "PM", "PSX", "PNW", "PXD", "PNC", "PPG", "PPL",
             "PFG", "PG", "PGR", "PLD", "PRU", "PEG", "PSA", "PHM", "PVH", "QRVO", "PWR", "QCOM", "DGX", "RL", "RJF",
             "RTN", "O", "REG", "REGN", "RF", "RSG", "RMD", "RHI", "ROK", "ROL", "ROP", "ROST", "RCL", "CRM", "SBAC",
             "SLB", "STX", "SEE", "SRE", "SHW", "SPG", "SWKS", "SLG", "SNA", "SO", "LUV", "SPGI", "SWK", "SBUX", "STT",
             "SYK", "STI", "SIVB", "SYMC", "SYF", "SNPS", "SYY", "TMUS", "TROW", "TTWO", "TPR", "TGT", "TEL", "FTI",
             "TFX", "TXN", "TXT", "TMO", "TIF", "TWTR", "TJX", "TMK", "TSS", "TSCO", "TDG", "TRV", "TRIP", "TSN", "UDR",
             "ULTA", "USB", "UAA", "UA", "UNP", "UAL", "UNH", "UPS", "URI", "UTX", "UHS", "UNM", "VFC", "VLO", "VAR",
             "VTR", "VRSN", "VRSK", "VZ", "VRTX", "VIAB", "V", "VNO", "VMC", "WAB", "WMT", "WBA", "DIS", "WM", "WAT",
             "WEC", "WCG", "WFC", "WELL", "WDC", "WU", "WRK", "WY", "WHR", "WMB", "WLTW", "WYNN", "XEL", "XRX", "XLNX",
             "XYL", "YUM", "ZBH", "ZION", "ZTS"]

    choice = 0

    print(
        "\nThis is a scrapjng tool that allows you to extract SP500 companies's data (i.e. balance sheet, income sheet and cashflow statement) as a .csv from the respective 10k in the SEC's EDGAR databank.\n")

    while True:
        try:
            choice = int(input(
                "Please choose an option:\n(1) Initialize continous monitoring.  \n(2) One-time request. \n(3) Run program with a sample. \n(0) End \n"))
        except ValueError:
            print("Invalid selection.")
            continue

        if choice == 0:
            conf = input("Are you sure?(Y/N): ")
            if conf == "Y":
                print("\n\nThank you, goodbye.")
                break


        elif choice == 1:
            input_tickers = input("Please enter the ticker or tickers of the respective companies (seperate them with a comma): \n")

            for i in input_tickers:
                if i not in SP500:
                    print(str(i)+"Is not a SP500 company ticker, it will be skipped")
                    input_tickers.remove(i)

            print("Please select the startyear for datacollection. \n")
            input_startyear = input("Please insert the startyear: ")
            print("\n")

            input_endyear = datetime.datetime.now().year
            print("\n\n")




        elif choice == 2:
            input_tickers = input("Please enter the ticker or tickers of the respective companies (seperate them with a comma): \n")
            for i in input_tickers:
                if i not in SP500:
                    print(str(i)+"Is not a SP500 company ticker, it will be skipped")
                    input_tickers.remove(i)

            print("Please select the timeframe for which you would like to extract the data. \n")
            input_startyear = input("Please insert the startyear: ")
            print("\n")
            input_endyear = input("Please insert the endyear: ")
            print("\n\n")






        elif choice == 3:



        else:
            print("Invalid selection. \n")







if __name__ == "__main__":
    main_menu()










#Todo fix issues from terminal

#ToDo dynamic SP500 list


#ToDo: 10ks
#soup = make_soup("https://www.sec.gov/Archives/edgar/data/2488/000000248819000011/amd-12292018x10k.htm")
#soup=make_soup("https://www.sec.gov/Archives/edgar/data/1652044/000165204419000004/goog10-kq42018.htm#s60D13494C77354D8AED0E72D61E53B98")
#https://www.sec.gov//Archives/edgar/data/1045810/000104581011000015/fy2011form10k.htm


sys.exit()





soup=make_soup("https://www.sec.gov/Archives/edgar/data/1652044/000165204419000004/goog10-kq42018.htm#s60D13494C77354D8AED0E72D61E53B98")

filing,spec=identify(soup.filename.text.split("\n", 1)[0])

ticker='Goog'

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




#Provision for taxes
inctax = re.compile("(\D*\s?(for)?income\stax{1}(es)?\s?\D*)||(Provision for taxes)")


export_to_csv(ticker,year,balance_sheet,operation_statement,cash_flow_statement)
