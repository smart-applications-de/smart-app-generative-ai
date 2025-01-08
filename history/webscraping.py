from operator import index

import requests as rq
import requests_oauthlib
import bs4
import pandas as pd

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
           "Accept-Encoding": "gzip, deflate",
           "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT": "1",
           "Connection": "close", "Upgrade-Insecure-Requests": "1"}

def DAXMarketCAP():
    try:
        html = pd.read_html('https://de.wikipedia.org/wiki/DAX')
        df = html[2]
        df.dropna(inplace=True)
        dax_marketCap = f'.\history\data\dax_market_Cap.csv'
        df.to_csv(dax_marketCap, index=False)
        return df
    except  Exception as error:
        print(error)
        return

def DAXCompanies():
    try:
        #'https://de.wikipedia.org/wiki/DAX'
        html = pd.read_html('https://en.wikipedia.org/wiki/DAX')
        df = html[4]
        df['Ticker-en'] = df['Ticker'].apply(lambda x: x.split('.')[0])
        #df.dropna(inplace=True)
        dax_companies = f'.\history\data\dax_companies.csv'
        df = df.drop(columns=['Logo'])
        df.to_csv(dax_companies,index=False)
        return df
    except Exception as error:
        print(error)
        return


def Top500Companies():
    try:
        html = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
        df = html[0]
        Top500_companies = f'.\history\data\s_p500.csv'
        df.to_csv(Top500_companies,index=False)
        return df
    except Exception as error:
        print(error)
        return
def Nasdaq_100():
    try:
        html = pd.read_html('https://en.wikipedia.org/wiki/Nasdaq-100')
        df = html[4]
        nasdaq_companies = f'.\history\data\/nasdaq_100.csv'
        df.to_csv(nasdaq_companies,index=False)
        return df
    except Exception as error:
        print(error)
        return
def DowJones():
    try:
        html = pd.read_html('https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average')
        df = html[2]
        dow_companies = f'.\history\data\dow_jones.csv'
        df.to_csv(dow_companies,index=False)
        return df
    except Exception as error:
        print(error)
        return

def MegaCapCompanies():
    try:
        url = 'https://stockanalysis.com/list/mega-cap-stocks'

        r = rq.get(url, headers=headers)
        soup = bs4.BeautifulSoup(r.content, 'html.parser')

        tb = soup.find(id="main-table")
        # print(tb)
        html = pd.read_html(tb.prettify())

        df = html[0]
        megaCap = f'.\history\data\mega_capCompanies.csv'
        df.to_csv(megaCap,index=False)
        return df
    except Exception as error:
        print(error)
        return


def IndustryPerformance():
    try:
        # Industry :
        Industry_url = "https://stockanalysis.com/stocks/industry/all/"
        r = rq.get(Industry_url, headers=headers)
        soup_ind = bs4.BeautifulSoup(r.content, 'html.parser')
        # print(soup.prettify())
        # soup.find_all("div", {"class": "stylelistrow"})
        tb_ind = soup_ind.find("table", {"class": "svelte-qmv8b3"})
        # print(tb)
        html_ind = pd.read_html(tb_ind.prettify())

        df_ind = html_ind[0]
        industry = f'.\history\data\industry.csv'
        df_ind.to_csv(industry,index=False)
        return  df_ind
    except Exception as error:
        print(error)
        return

def  SectorPerformance():

    try:
        sector_url = "https://stockanalysis.com/stocks/industry/sectors/"
        r = rq.get(sector_url, headers=headers)
        soup_se = bs4.BeautifulSoup(r.content, 'html.parser')

        tb_se = soup_se.find("table", {"class": "svelte-qmv8b3"})

        html_se = pd.read_html(tb_se.prettify())

        df_se = html_se[0]
        sector = f'.\history\data\sector.csv'
        df_se.to_csv(sector,index=False)

        return df_se
    except Exception as error:
        print(error)
        return


def QuartelyFinancialAnalysis(symbol):
    try:
        symbol=str(symbol).lower()
        #https://stockanalysis.com/stocks/aapl/financials/ratios/
        #https: // stockanalysis.com / stocks / aapl / financials / ratios /?p = quarterly
        url = f'https://stockanalysis.com/stocks/{symbol}/financials/ratios/?p=quarterly'

        r = rq.get(url, headers=headers)
        soup = bs4.BeautifulSoup(r.content, 'html.parser')

        tb = soup.find(id="main-table")

        html = pd.read_html(tb.prettify())

        df = html[0]
        financial_ratios = f'.\history\data\_{symbol}_qfinancial_ratios.csv'
        df=df.T
        df.to_csv(financial_ratios,index=False )
        return df
    except Exception as error:
        print(error)
        return



def AnualAnalysis(symbol):
        try:
            symbol = str(symbol).lower()
            # https://stockanalysis.com/stocks/aapl/financials/ratios/
            url = f'https://stockanalysis.com/stocks/{symbol}/financials/ratios/'

            r = rq.get(url, headers=headers)
            soup = bs4.BeautifulSoup(r.content, 'html.parser')
            # print(soup.prettify())

            tb = soup.find(id="main-table")
            # print(tb)
            html = pd.read_html(tb.prettify())

            df = html[0]
            financial_ratios = f'.\history\data\_{symbol}_yr_financial_ratios.csv'
            try:

                return df.T
            except Exception as error:
                print(error)
            df=df.T
            df.to_csv(financial_ratios,index=False)
            return df
        except Exception as error:
            print(error)
        return


def ListGermanyStockExchange():
    try:
        url = f'https://stockanalysis.com/list/deutsche-boerse-xetra/'
        # https://stockanalysis.com/quote/etr/VEE/

        r = rq.get(url, headers=headers)
        soup = bs4.BeautifulSoup(r.content, 'html.parser')

        tb = soup.find(id="main-table")

        html = pd.read_html(tb.prettify())

        df = html[0]
        german_stocks = f'.\history\data\german_stocks.csv'
        df.to_csv(german_stocks, index=False)
        return df
    except Exception as error:
        print(error)
def SummaryLoad():
        try:
            df1 =DAXMarketCAP()
            print(df1.head(3))
        except:
            pass
        try:
            df2 = DAXCompanies()
            print(df2.head(3))
            dax=True
        except:
            dax=False
            df2 = None
        try:
            df3 = Top500Companies()
            print(df3.head(3))
        except:
            pass
        try:
            df4 = MegaCapCompanies()
            print(df4.head(5))
            df_daq=Nasdaq_100()
            df_jone=DowJones()
            df_symbol_q= df_daq[['Symbol']]

            df_symbol =pd.concat([df_symbol_q, df4[['Symbol']] ],ignore_index=True )
            df_symbol = pd.concat([df_symbol, df_jone[['Symbol']] ],ignore_index=True )
            symbol = pd.read_csv("symbol.txt")
            df_symbol = pd.concat([df_symbol, symbol[['Symbol']]], ignore_index=True)

            if dax :
                sy =df2[['Ticker-en']]
                df_symbol = pd.concat([df_symbol, sy], ignore_index=True)
            df_symbol =df_symbol.drop_duplicates(ignore_index=True)

            df_symbol.to_csv(f'.\history\data\Tickers.csv', index=False)





        except:
            pass
        try:
            df5=IndustryPerformance()
            print(df5.head(5))
        except:
            pass
        try:
            df6 =SectorPerformance()
            print(df6.head(5))
        except:
            pass

        try:
            df7 =ListGermanyStockExchange()
            print(df7.head(5))
        except:
            pass


