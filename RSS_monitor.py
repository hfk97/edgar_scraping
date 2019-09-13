import subprocess
import sys
import importlib
import datetime
now = datetime.datetime.now()

# function that imports a library if it is installed, else installs it and then imports it
def getpack(package):
    try:
        return (importlib.import_module(package))
        # import package
    except ImportError:
        subprocess.call([sys.executable, "-m", "pip", "install", package])
        return (importlib.import_module(package))
        # import package

feedparser=getpack("feedparser")


import pickle


def save_obj(obj, name ):
    with open(name+".pkl", 'wb') as pickle_file:
        pickle.dump(obj, pickle_file,pickle.HIGHEST_PROTOCOL)


def load_obj(name ):
    with open(name+".pkl", 'rb') as pickle_file:
        return pickle.load(pickle_file)


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


def check_new10Ks(request_tickers):

    queue=[]
    try:
        processed_links
    except NameError:
        try:
            processed_links=load_obj("processed_links")


        except FileNotFoundError:
            processed_links={}
            for i in request_tickers:
                processed_links[i]=[]




    newlinks=0

    for i in request_tickers:

        NewsFeed = feedparser.parse("https://sec.report/CIK/"+str(i[2])+".rss")

        for j in NewsFeed.entries:
            if "10-K" in j.title:
                #print(j.links[0].href,type(j.links[0].href))
                if j.links[0].href not in processed_links[i[0]]:
                    queue.append((i[0],j.links[0].href,(datetime.datetime.now().year)-1))
                    processed_links[i[0]].append(j.links[0].href)
                    if newlinks==0:
                        newlinks=1



    if newlinks==1:
        #print(queue)
        save_obj(processed_links, "processed_links")
        return queue

    else:
        print("no new 10Ks")
        return None


def main(request_tickers):
    for n,i in enumerate(request_tickers):
        request_tickers[n]=companies[i]
    return check_new10Ks(request_tickers)


if __name__ == "__main__":
    main()


#This program checks for new 10Ks every update frame (in seks) if there are new 10Ks to process it gives back a list of tuples with company name and link to the form