import numpy as np
import pandas as pd
import yfinance as yf
from .webscraping import  SummaryLoad, QuartelyFinancialAnalysis,AnualAnalysis
import numpy as np
import pandas as pd
import yfinance as yf
import time
from .webscraping import SummaryLoad, QuartelyFinancialAnalysis, AnualAnalysis


def Seasonality_yearly(yearly_seaonality, target_field_name, yearly_seaonalitypercent, df):
    y = round(365.25 * 5 / 7)
    df[yearly_seaonality] = df[target_field_name] - df[target_field_name].shift(y)
    df[yearly_seaonalitypercent] = (df[target_field_name] - df[target_field_name].shift(y)) * 100 / df[
        target_field_name].shift(y)
    df = df.drop(columns=[yearly_seaonality])
    return df


def Seasonality_weekly(weekly_seaonality, target_field_name, weekly_seaonalitypercent, df):
    df[weekly_seaonality] = df[target_field_name] - df[target_field_name].shift(5)
    df[weekly_seaonalitypercent] = (df[target_field_name] - df[target_field_name].shift(5)) * 100 / df[
        target_field_name].shift(5)
    df = df.drop(columns=[weekly_seaonality])
    return df


def Seasonality_3yearly(yearly_seaonality, target_field_name, yearly_seaonalitypercent, df):
    y = round(365.25 * 5 * 3 / 7)
    df[yearly_seaonality] = df[target_field_name] - df[target_field_name].shift(y)
    df[yearly_seaonalitypercent] = (df[target_field_name] - df[target_field_name].shift(y)) * 100 / df[
        target_field_name].shift(y)
    df = df.drop(columns=[yearly_seaonality])
    return df


def Seasonality_5yearly(yearly_seaonality, target_field_name, yearly_seaonalitypercent, df):
    y = round(365.25 * 5* 5/ 7)
    df[yearly_seaonality] = df[target_field_name] - df[target_field_name].shift(y)
    df[yearly_seaonalitypercent] = (df[target_field_name] - df[target_field_name].shift(y)) * 100 / df[
        target_field_name].shift(y)
    df = df.drop(columns=[yearly_seaonality])
    return df


def Seasonality_monthly(monthly_seaonality, target_field_name, monthly_seaonalitypercent, df):
    a = round(365.25 * 5 / (12 * 7))
    df[monthly_seaonality] = df[target_field_name] - df[target_field_name].shift(a)
    df[monthly_seaonalitypercent] = (df[target_field_name] - df[target_field_name].shift(a)) * 100 / df[
        target_field_name].shift(a)
    df = df.drop(columns=[monthly_seaonality])

    return df


def Seasonality_quartely(quartely_seaonality, target_field_name, quartely_seaonalitypercent, df):
    b = round(365.25 * 5 * 3 / (12 * 7))
    df[quartely_seaonality] = df[target_field_name] - df[target_field_name].shift(b)
    df[quartely_seaonalitypercent] = (df[target_field_name] - df[target_field_name].shift(b)) * 100 / df[
        target_field_name].shift(b)
    df = df.drop(columns=[quartely_seaonality])

    return df


def Seasonality_halfyearly(halfyearly_seaonality, target_field_name, halfyearly_seaonalitypercent, df):
    c = round(365.25 * 5 * 6 / (12 * 7))
    df[halfyearly_seaonality] = df[target_field_name] - df[target_field_name].shift(c)
    df[halfyearly_seaonalitypercent] = (df[target_field_name] - df[target_field_name].shift(c)) * 100 / df[
        target_field_name].shift(c)
    df = df.drop(columns=[halfyearly_seaonality])
    return df


def Seasonality_daily(daily_seaonality, target_field_name, daily_seaonalitypercent, df):
    df[daily_seaonality] = df[target_field_name] - df[target_field_name].shift(1)
    df[daily_seaonalitypercent] = (df[target_field_name] - df[target_field_name].shift(1)) * 100 / df[
        target_field_name].shift(1)
    df =df.drop(columns=[daily_seaonality])
    return df


def moving_average(df, span, target_fieldname, ema_field):
    weights = np.arange(1, span + 1)

    sma = 'sma_' + str(span)+'_day'
    wma = 'wma_' + str(span)+'_day'
    ema = 'ema_' + str(span)+'_day'
    df[ema] = df[[target_fieldname]].ewm(span, adjust=False).mean()
    df[sma] = df[[target_fieldname]].rolling(span).mean()
    df[wma] = df[[target_fieldname]].rolling(span).apply(lambda x: np.dot(x, weights) / weights.sum(), raw=True)
    return df


import time

start = time.time()




#
def YahooStockPerformance(symbol,ifETF=False):
    try:
        p = yf.Ticker(str(symbol))
        data = pd.DataFrame(p.history(period='2y').reset_index())
        data = data[["Date", "Open", "High", "Low", "Close"]]
        data['Date'] = pd.to_datetime(data['Date'], format="%Y-%m-%d")
        data['prevClose'] = data['Close'].shift(1)
        data['week'] = data['Close'].shift(5)
        data['month'] = data['Close'].shift(22)
        data['3month'] = data['Close'].shift(66)
        data['6month'] = data['Close'].shift(132)
        data['1yr'] = data['Close'].shift(252)

        data['1_day_performance'] = (data['Close'] - data['prevClose']) * 100 /data['prevClose']
        data['week_performance'] = (data['Close'] - data['week']) * 100 /data['week']
        data['month_performance'] = (data['Close'] - data['month']) * 100 /  data['month']
        data['3month_performance'] = (data['Close'] - data['3month']) * 100 / data['3month']
        data['6month_performance'] = (data['Close'] - data['6month']) * 100 /  data['6month']
        data['1yr_performance'] = (data['Close'] - data['1yr']) * 100 /  data['1yr']
        min_date = data['Date'].min()
        max_date = data['Date'].max()


        df_yr_max = data.loc[data['Date'] == f"'{max_date}'"][
            ['Date', 'Close', '1_day_performance', 'week_performance', 'month_performance', '3month_performance',
             '6month_performance', '1yr_performance']].round(2)
        df_yr_min = data.loc[data['Date'] == f"'{min_date}'"][['Close']].round(2)

        df_yr_max['2yr_performance'] = (
                    (df_yr_max['Close'].values - df_yr_min['Close'].values) * 100 / df_yr_min['Close'].values)
        df_yr_max['2yr_performance'] = df_yr_max['2yr_performance'].round(2)
        try:
            df_yr_max['Ticker'] = symbol
            if ifETF:
                df_yr_max['quoteType'] = p.info['quoteType']
                df_yr_max['longName'] = p.info['longName']
            else:
                df_yr_max['quoteType'] = p.info['quoteType']
                df_yr_max['longName'] = p.info['longName']
                df_yr_max['sector'] = p.info['sector']
                df_yr_max['industry'] = p.info['industry']
                df_yr_max['website'] = p.info['website']


        except:
            pass

        return df_yr_max
    except Exception as error:
        print(error)


def AllStocksPerformnace(df_stocks):
    try:
        ETFs=['^NDX','^GSPC','^DJI','^GDAXI','^FTSE','URTH','SPY','VOO', 'IVV','VTI','IEFA','VUG','^STOXX50E', '^FCHI','^NYA','^N225',
              '^HSI','^OEX','^N100','GC=F','CL=F','SLVR','^990100-USD-STRD','^BUK100P','SI=F']
        df=pd.DataFrame()
        try:
            for etf in ETFs:
                try:
                    df_etf=YahooStockPerformance(etf)
                    df=df._append(df_etf)
                except:
                    pass

        except:
            pass
        df.to_csv(f'./history/data/df_etf.csv', index=False)
    except Exception as error:
        print(error)

    try:
        df_performance=pd.DataFrame()
        try:
            for n in df_stocks['symbol']:
                try:
                    if n=="RAND":
                        n="RAND.AS"
                    else:
                        n=n
                    df_sy=YahooStockPerformance(n)
                    df_performance=df_performance._append(df_sy)
                except:
                    pass
        except:
            pass
        df_performance.to_csv(f'./history/data/df_performance.csv',index=False)
        return df_performance
    except Exception as error1:
        print(error1)
        return


def DailyQuote(symbol):
    


        try:
            try:
                df_symbol = pd.read_csv("./history/data/dax_companies.csv")
                if symbol in df_symbol['Ticker-en'].values:
                    isdax=True
                else:
                    isdax:bool=False
                if isdax:
                    dax_symbol = df_symbol.loc[df_symbol['Ticker-en']==f'{symbol}']
                    #print(df.loc[df['B'].isin(['one','three'])])
                    print(dax_symbol)
                    symbol_yahoo=dax_symbol['Ticker'].values[0]
                elif symbol=="RAND":
                   symbol_yahoo="RAND.AS"

                else:
                    symbol_yahoo= symbol
            except Exception as Err:
                print(Err)
                print("DAX in DE Symbol Stock was not successful")
                symbol_yahoo = symbol
            p = yf.Ticker(str(symbol_yahoo))
            data = pd.DataFrame(p.history(period='5y').reset_index())
            df_financials =(p.financials).T
            #print(p.info)
            df_info =pd.DataFrame(p.info)
            df_data=df_info.copy()
            try:
                
                df_data= df_data[['website','beta','trailingPE', 'symbol','longName', 'marketCap', 'bookValue',
                                  'priceToBook', 'currentPrice', 'recommendationKey', 'totalCash', 'totalCashPerShare',
                                   'quickRatio', 'currentRatio','totalRevenue','previousClose','debtToEquity', 'revenuePerShare',
                                  'returnOnEquity',
                                  'freeCashflow',  'earningsGrowth', 'revenueGrowth', 'grossMargins', 'ebitdaMargins',
                                   'operatingMargins','trailingPegRatio', 'sector', 'longBusinessSummary','industry','regularMarketOpen']]
                company_stock_info = f'./history/data/company_stock_info_{symbol}_data.csv'
                df_data.to_csv(company_stock_info)
            except Exception as error:
                df_data= df_data[['website','trailingPE', 'symbol','longName', 'marketCap', 'bookValue',
                  'priceToBook', 'currentPrice', 'recommendationKey', 'totalCash', 'totalCashPerShare',
                   'quickRatio', 'currentRatio','totalRevenue','previousClose','debtToEquity', 'revenuePerShare',
                  'returnOnEquity', 'sector', 'longBusinessSummary','industry','regularMarketOpen']]
                company_stock_info = f'./history/data/company_stock_info_{symbol}_data.csv'
                df_data.to_csv(company_stock_info)
                print(error)
            try:
                df_f = df_financials[['EBITDA','Gross Profit', 'Total Revenue','Operating Revenue']]

                df_f= df_f.reset_index()
                df_f.columns= ['Date', 'EBITDA', 'Gross Profit', 'Total Revenue','Operating Revenue']
                monthly_revenue = f'./history/data/revenue_{symbol}_data.csv'

                df_f.dropna(inplace=True)
                df_f.to_csv(monthly_revenue)
            except:
                pass

            if len(data) >1:
                try:
                    data = data[["Date", "Open", "High", "Low", "Close"]]
                    data['Date'] = pd.to_datetime(data['Date'],format="%Y-%m-%d")
                    t = '2020-11-18'
                    file_name= f'./history/data/_{symbol}_data.csv'
                    monthly_file = f'./history/data/monthly_{symbol}_data.csv'
                    #monthly_revenue = f'.\data\revenue_{symbol}_data.csv'
                    #data = data.query(f"Date < '{today}'").reset_index(drop=True)

                    data.columns = ['date', 'open', 'high', 'low', 'close']
                    data['month']=data['date'].dt.month
                    data['year'] = data['date'].dt.year
                    data['week'] = data['date'].dt.isocalendar().week
                    data['quarter'] = data['date'].dt.quarter
                    #data['date'] = data['date'].dt.date
                    #.quarter

                    data = Seasonality_daily('change', 'close', 'daily_trend', data)
                    data = Seasonality_weekly('change_weekly', 'close', 'weekly_trend', data)
                    data = Seasonality_monthly('change_monthly', 'close', 'monthly_trend', data)
                    data = Seasonality_quartely('change_quartely', 'close', 'quartely_trend', data)
                    data = Seasonality_halfyearly('change_halfyearly', 'close', '6_monthly_trend', data)
                    data = Seasonality_yearly('change_yearly', 'close', 'yearly_trend', data)
                    #data = Seasonality_3yearly('change_3years', 'close', '3years_performance', data)
                    data = moving_average(data, 5, 'close', 'close')
                    data = moving_average(data, 20, 'close', 'close')
                    data = moving_average(data, 50, 'close', 'close')
                    data = moving_average(data, 200, 'close', 'close')
                    data.dropna(inplace=True)
                    data = (data.round(2)).reset_index(drop=True)
                    data.to_csv(file_name)
                    print(data.head(10))
                    df_monthly = (data.groupby(['year','month'])[['close','open','high','low','daily_trend','monthly_trend',
                                                                  'sma_5_day','sma_20_day','sma_50_day', 'sma_200_day']].mean()).reset_index()
                    df_monthly_max = (data.groupby(['year','month'])[['close','open','high','low','daily_trend']].max()).reset_index()
                    df_monthly_max.columns=['year','month','close_max','open_max','high_max','low_max','daily_trend_max']
                    df_monthly= df_monthly.merge(df_monthly_max, on=['year','month'])
                    df_monthly_low = (data.groupby(['year','month'])[['close','open','high','low','daily_trend']].min()).reset_index()
                    df_monthly_low.columns=['year','month','close_min','open_min','high_min','low_min','daily_trend_max']
                    df_monthly=df_monthly.merge(df_monthly_low, on=['year','month'])
                    df_monthly=df_monthly.round(2)
                    print(df_monthly.head(10))
                    df_monthly.to_csv(monthly_file)
                    try:
                        SummaryLoad()
                    except:
                        pass
                    try:
                        df2 = QuartelyFinancialAnalysis(str(symbol))
                        print(df2.head(5))
                    except:
                        df1= df_f
                    try:
                        df1 = AnualAnalysis(str(symbol))
                        print(df1.head(5))
                    except:
                        df1 = df_f

                    return      data,df_monthly,df_data,df1



                except (Exception) as error1:
                     print("Failed Dowload", error1)

        except (Exception) as error:
            print("Failed Dowload", error)
            return
