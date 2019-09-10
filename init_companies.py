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


def initialize_companies():

    SP500=["MMM","ABT","ABBV","ABMD","ACN","ATVI","ADBE","AMD","AAP","AES","AMG","AFL","A","APD","AKAM","ALK","ALB","ARE","ALXN","ALGN","ALLE","AGN","ADS","LNT","ALL","GOOGL","GOOG","MO","AMZN","AMCR","AEE","AAL","AEP","AXP","AIG","AMT","AWK","AMP","ABC","AME","AMGN","APH","APC","ADI","ANSS","ANTM","AON","AOS","APA","AIV","AAPL","AMAT","APTV","ADM","ARNC","ANET","AJG","AIZ","ATO","T","ADSK","ADP","AZO","AVB","AVY","BHGE","BLL","BAC","BK","BAX","BBT","BDX","BRK.B","BBY","BIIB","BLK","HRB","BA","BKNG","BWA","BXP","BSX","BMY","AVGO","BR","BF.B","CHRW","COG","CDNS","CPB","COF","CPRI","CAH","KMX","CCL","CAT","CBOE","CBRE","CBS","CE","CELG","CNC","CNP","CTL","CERN","CF","SCHW","CHTR","CVX","CMG","CB","CHD","CI","XEC","CINF","CTAS","CSCO","C","CFG","CTXS","CLX","CME","CMS","KO","CTSH","CL","CMCSA","CMA","CAG","CXO","COP","ED","STZ","COO","CPRT","GLW","CTVA","COST","COTY","CCI","CSX","CMI","CVS","DHI","DHR","DRI","DVA","DE","DAL","XRAY","DVN","FANG","DLR","DFS","DISCA","DISCK","DISH","DG","DLTR","D","DOV","DOW","DTE","DUK","DRE","DD","DXC","ETFC","EMN","ETN","EBAY","ECL","EIX","EW","EA","EMR","ETR","EOG","EFX","EQIX","EQR","ESS","EL","EVRG","ES","RE","EXC","EXPE","EXPD","EXR","XOM","FFIV","FB","FAST","FRT","FDX","FIS","FITB","FE","FRC","FISV","FLT","FLIR","FLS","FMC","FL","F","FTNT","FTV","FBHS","FOXA","FOX","BEN","FCX","GPS","GRMN","IT","GD","GE","GIS","GM","GPC","GILD","GPN","GS","GWW","HAL","HBI","HOG","HIG","HAS","HCA","HCP","HP","HSIC","HSY","HES","HPE","HLT","HFC","HOLX","HD","HON","HRL","HST","HPQ","HUM","HBAN","HII","IDXX","INFO","ITW","ILMN","IR","INTC","ICE","IBM","INCY","IP","IPG","IFF","INTU","ISRG","IVZ","IPGP","IQV","IRM","JKHY","JEC","JBHT","JEF","SJM","JNJ","JCI","JPM","JNPR","KSU","K","KEY","KEYS","KMB","KIM","KMI","KLAC","KSS","KHC","KR","LB","LHX","LH","LRCX","LW","LEG","LEN","LLY","LNC","LIN","LKQ","LMT","L","LOW","LYB","MTB","MAC","M","MRO","MPC","MKTX","MAR","MMC","MLM","MAS","MA","MKC","MXIM","MCD","MCK","MDT","MRK","MET","MTD","MGM","MCHP","MU","MSFT","MAA","MHK","TAP","MDLZ","MNST","MCO","MS","MOS","MSI","MSCI","MYL","NDAQ","NOV","NKTR","NTAP","NFLX","NWL","NEM","NWSA","NWS","NEE","NLSN","NKE","NI","NBL","JWN","NSC","NTRS","NOC","NCLH","NRG","NUE","NVDA","ORLY","OXY","OMC","OKE","ORCL","PCAR","PKG","PH","PAYX","PYPL","PNR","PBCT","PEP","PKI","PRGO","PFE","PM","PSX","PNW","PXD","PNC","PPG","PPL","PFG","PG","PGR","PLD","PRU","PEG","PSA","PHM","PVH","QRVO","PWR","QCOM","DGX","RL","RJF","RTN","O","REG","REGN","RF","RSG","RMD","RHI","ROK","ROL","ROP","ROST","RCL","CRM","SBAC","SLB","STX","SEE","SRE","SHW","SPG","SWKS","SLG","SNA","SO","LUV","SPGI","SWK","SBUX","STT","SYK","STI","SIVB","SYMC","SYF","SNPS","SYY","TMUS","TROW","TTWO","TPR","TGT","TEL","FTI","TFX","TXN","TXT","TMO","TIF","TWTR","TJX","TMK","TSS","TSCO","TDG","TRV","TRIP","TSN","UDR","ULTA","USB","UAA","UA","UNP","UAL","UNH","UPS","URI","UTX","UHS","UNM","VFC","VLO","VAR","VTR","VRSN","VRSK","VZ","VRTX","VIAB","V","VNO","VMC","WAB","WMT","WBA","DIS","WM","WAT","WEC","WCG","WFC","WELL","WDC","WU","WRK","WY","WHR","WMB","WLTW","WYNN","XEL","XRX","XLNX","XYL","YUM","ZBH","ZION","ZTS"]
    #sample=["NVDA","QCOM","INTC","AMD","MU","AMAT"]

    Companies={}

    #for i in sample:
    for i in SP500:

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
        print(i, name, CIK)

    save_obj(Companies, "companies")

    return

initialize_companies()





