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
time=getpack("time")


bs4 = getpack("bs4")
urllib = getpack("urllib")
requests = getpack("urllib.request")

# get the tickers of all stocks in the SP500
def sp500_tickers():
    resp = requests.get('http://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    soup = bs4.BeautifulSoup(resp.text, 'lxml')
    table = soup.find('table', {'class': 'wikitable sortable'})
    tickers = []
    for row in table.findAll('tr')[1:]:
        ticker = row.findAll('td')[0].text
        ticker = ticker.replace("\n","")
        tickers.append(ticker)

    return tickers



def main_menu():
    print("started")
    SP500 = sp500_tickers()

    choice = 0

    print(
        "\nThis is a scrapjng tool that allows you to extract SP500 companies's data (i.e. balance sheet, income sheet and cashflow statement) as a .csv from the respective 10k in the SEC's EDGAR databank.\n")

    while True:
        try:
            choice = int(input(
                "Please choose an option:\n(1) Initialize continous monitoring.  \n(2) One-time request. \n(0) End \n"))
        except ValueError:
            print("Invalid selection.")
            continue

        if choice == 0:
            conf = input("Are you sure?(Y/N): ")
            if conf == "Y":
                print("\n\nThank you, goodbye.")
                break


        elif choice == 1:
            input_tickers = []
            for ticker in input(
                    "Please enter the ticker or tickers of the respective companies (seperate them with a comma): \n").split(
                ','):
                input_tickers.append(ticker)

            for i in input_tickers:
                if i not in SP500:
                    print(str(i) + " is not a SP500 company ticker, it will be skipped.\n")
                    input_tickers.remove(i)

            if len(input_tickers) == 0:
                print("No valid tickers have been chosen.")
                continue

            input_startyear = int(input("Please insert the startyear (must be >= 2008): "))
            print("\n")

            input_endyear = datetime.datetime.now().year
            print("\n")

            update_intervall = int(input("Please Select an update intervall (in seconds): "))
            print("\n")

            data_request(input_startyear, input_endyear, input_tickers)

            print("Monitoring initiated, interrupt via ctrl+c\n")

            update_mode(input_tickers,update_intervall)




        elif choice == 2:
            input_tickers=[]
            for ticker in input(
                "Please enter the ticker or tickers of the respective companies (seperate them with a comma): \n").split(','):
                input_tickers.append(ticker)

            for i in input_tickers:
                if i not in SP500:
                    print(str(i) + " is not a SP500 company ticker, it will be skipped.\n")
                    input_tickers.remove(i)

            if len(input_tickers)==0:
                print("No valid tickers have been chosen.")
                continue

            print("Please select the timeframe for which you would like to extract the data. \n")
            input_startyear = int(input("Please insert the startyear (must be >= 2008): "))
            print("\n")
            input_endyear = int(input("Please insert the endyear: "))
            print("\n\n")

            data_request(input_startyear,input_endyear,input_tickers)


        else:
            print("Invalid selection. \n")



def data_request(start_year,end_year,tickers):
    import find_data
    import processing
    queue = find_data.main(start_year,end_year,tickers)
    if queue == None:
        return
    processing_log=[]

    for q in queue:
        processing_log_entry=""
        try:
            processing_log_entry+="Log of"+ str(q) +" "
            #ticker, url and date
            processing_log_entry+=processing.make_soup(q[0], q[1], q[2])

        except UnboundLocalError as e:
            processing_log_entry+=str(e)

        except AssertionError as e:
            processing_log_entry+=str(e)

        processing_log.append(processing_log_entry)

    for i in processing_log:
        print(i)





def update_mode(input_tickers,update_intervall):
    import RSS_monitor
    import processing

    processing_log = []

        # hier loop
    while True:
        try:
            queue = RSS_monitor.main(input_tickers)

            if queue != None:
                print("Queue: ")
                for i in queue:
                    print(str(i) + "\n")

                for q in queue:
                    processing_log_entry = ""
                    try:
                        processing_log_entry += "Log of" + str(q) + " "
                        # ticker, url and date
                        processing_log_entry += processing.make_soup(q[0], q[1], q[2])

                    except UnboundLocalError as e:
                        processing_log_entry += str(e)

                    except AssertionError as e:
                        processing_log_entry += str(e)

                    processing_log.append(processing_log_entry)

                for i in processing_log:
                    print(i)

            print("asleep")
            time.sleep(update_intervall)
            print("awake")

        except KeyboardInterrupt:
            print("Monitoring ended \n")
            break

    return



if __name__ == "__main__":
    main_menu()
