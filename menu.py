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

datetime=getpack("datetime")



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



            update_mode(input_tickers)




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
            #Todo
            print("Hey")



        else:
            print("Invalid selection. \n")






def update_mode(input_tickers):
    import RSS_monitor
    import soup
    issue_log=[]
    queue=RSS_monitor.main(input_tickers)



    for q in queue:
        print(q)



        try:
            issue_log.append("Log of" + str(q))
            #ticker, url and date
            soup.make_soup(q[0],q[1],q[2])
            issue_log.append("done")

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



#ToDo does not have the year

def data_request(start_year,endyear,tickers):
    import find_data as ini
    import soup
    queue=ini.main(start_year,endyear,tickers)
    issue_log=[]
    for q in queue:

        try:
            issue_log.append("Log of"+ str(q))
            #ticker, url and date
            soup.make_soup(q[0],q[1],q[2])
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




if __name__ == "__main__":
    main_menu()
