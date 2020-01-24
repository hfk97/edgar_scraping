# import necessary packages
import subprocess
import sys
import importlib

# import our other scripts
import find_data
import RSS_monitor
import processing
import init_companies


def getpack(package):
    try:
        return importlib.import_module(package)
        # import package
    except ImportError:
        subprocess.call([sys.executable, "-m", "pip", "install", package])
        return importlib.import_module(package)
        # import package


datetime = getpack("datetime")
time = getpack("time")
bs4 = getpack("bs4")
requests=getpack("requests")
import pickle


# get the tickers of all stocks in the SP500
def sp500_tickers():
    resp = requests.get('http://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    soup = bs4.BeautifulSoup(resp.text, 'lxml')
    table = soup.find('table', {'class': 'wikitable sortable'})
    tickers = []
    for row in table.findAll('tr')[1:]:
        ticker = row.findAll('td')[0].text
        ticker = ticker.replace("\n", "")
        tickers.append(ticker)

    return tickers


# this function loads a pickled object
def load_obj(name):
    with open(name+".pkl", 'rb') as pickle_file:
        return pickle.load(pickle_file)


def main_menu():
    print("started")

    # import SP500 companies
    SP500 = sp500_tickers()

    # try to load and else initialize companies dictionary (this contains ticker, name and CIK for all SP500 companies)
    try:
        companies = load_obj("companies")

    except FileNotFoundError:
        print("companies.pkl is missing. The program now need to initialize all SP500 companies."
              "This might take some time.")
        init_companies.initialize_companies(SP500)
        companies = load_obj("companies")

    # short introduction
    print(
        "\nThis is a scraping tool that allows you to extract SP500 companies's data (i.e. balance sheet, income sheet"
        " and cashflow statement) as a .csv from the respective 10k in the SEC's EDGAR database.\n")

    # main program loop that will be 'broken' upon user selection
    while True:
        try:
            # list options and use variable to keep track of the users choice
            choice = int(input(
                "Please choose an option:\n(1) Initialize continuous monitoring.  \n(2) One-time request. \n(0) End \n"))

        # if input is not an integer
        except ValueError:
            print("Invalid selection.")
            continue

        # choice to end the program
        if choice == 0:
            conf = input("Are you sure?(Y/N): ")
            if conf == "Y":
                print("\n\nThank you, goodbye.")
                break

        # continuous monitoring
        elif choice == 1 or choice == 2:
            input_tickers = []
            for ticker in input("Please enter the ticker or tickers of the respective companies (separate them with a comma): \n").split(','):
                ticker = ticker.replace(" ","")
                if ticker in SP500:
                    input_tickers.append(companies[ticker])
                else:
                    print(str(ticker) + " is not a valid SP500 company ticker, it will be skipped.\n")
                    continue

            if len(input_tickers) == 0:
                print("No valid tickers have been chosen.")
                continue

            input_startyear = int(input("Please insert the start year (must be >= 2008): "))
            print("\n")

            if choice == 1:
                input_endyear = datetime.datetime.now().year
                update_intervall = int(input("Please Select an update intervall (in seconds): "))
                print("\n")

            else:
                input_endyear = int(input(f"Please insert the end year (must be < {datetime.datetime.now().year}): "))
                print("\n")

            data_request(input_startyear, input_endyear, input_tickers)

            if choice == 1:
                print("Monitoring initiated, interrupt using 'ctrl+c'\n")
                update_mode(input_tickers, update_intervall)

        else:
            print("Invalid selection. \n")


# function that combines find_data.py and processing.py to download the requested data
def data_request(start_year, end_year, tickers):
    queue = find_data.main(start_year, end_year, tickers)
    if queue is None:
        return
    processing_log = []

    for q in queue:
        print(f"Processing: {q[1]}.\n")
        processing_log_entry = ""
        try:
            processing_log_entry += f"Log of {q} "
            processing_log_entry += processing.make_soup(q[0], q[1], q[2])

        except UnboundLocalError as e:
            processing_log_entry += str(e)

        except AssertionError as e:
            processing_log_entry += str(e)

        processing_log.append(processing_log_entry)

    for i in processing_log:
        print(i)


# function that checks whether new form 10Ks are available for a given group of tickers every x seconds
# it does so by calling functions in RSS_monitor.py
def update_mode(input_tickers, update_intervall):

    processing_log = []

    # tickers are monitored until keyboard interrupt (ctrl+c) is used
    while True:
        try:
            queue = RSS_monitor.check_new10Ks(input_tickers)

            if queue is not None:
                print("Queue: ")
                for i in queue:
                    print(f"{i}\n")

                for q in queue:
                    processing_log_entry = ""
                    try:
                        processing_log_entry += f"Log of {q} "
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