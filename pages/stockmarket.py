

import pandas as pd

import altair as alt

import streamlit as st

import os

def germinApiKey():
    st.warning('Please enter your Google Gemini API Key')
    "[Get GOOGLE API KEY](https://ai.google.dev/)"
    openai_api_key = st.text_input(
        "GOOGLE API KEY", key="germin_api_key", type="password")
    if  "germin_api_key" not in st.session_state:
        st.session_state['germin_api_key'] = openai_api_key
        st.info("Please add your OpenAI API key to continue.")
        st.stop()
    return  st.session_state['germin_api_key']
def SerpApiKey():
    st.warning('Please enter your Serper API Key')
    "[Get SERPER API KEY](https://serper.dev/)"
    serper_api_key = st.text_input(
        "SERPER API KEY", key="serp_api_key", type="password")
    if  "serp_api_key" not in st.session_state:

        st.session_state['serp_api_key'] = serper_api_key
    return  st.session_state['serp_api_key']
germin_key =  germinApiKey()
serp_key = SerpApiKey()
if germin_key  and serp_key:
    os.environ["GOOGLE_API_KEY"] = germin_key
    os.environ['SERPER_API_KEY'] = serp_key
    os.environ["OPENAI_API_KEY"]=germin_key
    from history.data import DailyQuote, AllStocksPerformnace
    from history.webscraping import SummaryLoad
    from Forecasts.models import VECM_Forecast_Lower_Upper
    import plotly.express as px
    from StockmarketAnalysis.crew import StockMarketCrew
    from News.news_and_marketing import CrewStocknews
    @st.cache_resource
    def get_performance():
        try:
            df_mega = pd.read_csv("./history/data/mega_capCompanies.csv")
            df_stock=pd.DataFrame()

            mega_ticker = df_mega [['Symbol']]
            mega_ticker.columns = ['symbol']
            df_stock= df_stock._append(mega_ticker, ignore_index=True)
            try:
                df_dax = pd.read_csv("./history/data/dax_companies.csv")
                dax_ticker =df_dax[['Ticker']]
                dax_ticker.columns =['symbol']
                df_stock = (df_stock._append(dax_ticker)).reset_index(drop=True)
            except:
                df_stock=df_stock
            df_daq=pd.read_csv(f'.\history\data\nasdaq_100.csv')
            daq_ticker = df_daq[['Symbol']]
            daq_ticker.columns = ['symbol']
            df_stock=(df_stock._append(daq_ticker))
            df_jones = pd.read_csv(f'.\history\data\dow_jones.csv')
            #s_p500

            jones_ticker = df_jones[['Symbol']]
            jones_ticker.columns = ['symbol']

            df_stock=df_stock._append(jones_ticker,ignore_index=True)


            df_stock = df_stock.drop_duplicates(ignore_index=True)
            df=(AllStocksPerformnace(df_stock)).reset_index(drop=True)
            return df
        except Exception as error:
            print(error)


    @st.cache_resource
    def get_historical_data(symbol):
        df,df_monthly,df_data,df_f=DailyQuote(symbol)
        return df,df_monthly,df_data,df_f
    @st.cache_resource
    def get_Forecast_data(df):
        # pred = VECM_Forecast_Lower_Upper(data_df,steps=10,seasons=252,response='close',start_date=td, freq='D')
        df=(df.sort_values('date', ascending=True)).reset_index(drop=True)
        try:
            max_date=(df['date'].dt.date.max() + pd.DateOffset(days=1))
                      #timedelta(days=1))
            print(max_date)
            pred=VECM_Forecast_Lower_Upper(df,steps=20,seasons=252,
                                         response="close",start_date=max_date, freq='B')
            return pred
        except Exception as error:
            print(error)
        return

    def download_markdown_file(file_path,file):
        """Downloads a markdown file from a given path."""
        try:
                st.download_button(
                    label="Download Markdown File",
                    data=file,
                    file_name=os.path.basename(file_path),  # Use original filename
                    mime="text/markdown",  # Specify MIME type
                )
        except FileNotFoundError:
            st.error(f"Error: Markdown file not found at {file_path}")
        except Exception as e:
            st.error(f"An error occurred: {e}")

    @st.cache_resource
    def getCrewAINews(topic):
        try:
            date=pd.to_datetime('today').date()
            yr = pd.to_datetime('today').year
            results=CrewStocknews( germin_key, serp_key,topic,yr,date)
            return results
        except Exception as error:
            return  error
    @st.cache_resource
    def getCrewAIAgentRecommendation(option):
        try:
            history =f'monthly_{option}_data.csv'
            option_lower=str(option).lower()
            # aapl_qfinancial_ratios.
            financal_data=f'_{option_lower }_qfinancial_ratios.csv'
            # company_stock_info_AAPL_data.csv
            company_stock_info=f'company_stock_info_{option}_data'
            results=StockMarketCrew( germin_key,serp_key,option, history, financal_data,company_stock_info).run()
            return results
        except Exception as error:
            return  error


    st.title("Stockmarket Analysis and Financial Advisor with AI")
    @st.cache_data
    def getIndustryPerformance():
        DailyQuote("AMD")
        if 'df1' not in st.session_state:
            df1 = pd.read_csv("./history/data/industry.csv")
        else:
            df1 = st.session_state['df1']
        return  df1
    @st.cache_data
    def getTickers():
        try:

            df4 = pd.read_csv("./history/data/mega_capCompanies.csv")
            df_daq=pd.read_csv(f'./history/data/nasdaq_100.csv')
            df_jone=pd.read_csv(f'./history/data/dow_jones.csv')
            df_symbol_q= df_daq[['Symbol']]

            df_symbol =pd.concat([df_symbol_q, df4[['Symbol']] ],ignore_index=True )
            df_symbol = pd.concat([df_symbol, df_jone[['Symbol']] ],ignore_index=True )

            sy=pd.read_csv("./history/data/dax_companies.csv")
            sy= sy[['Ticker-en']]
            sy.columns=['Symbol']
            df_symbol = pd.concat([df_symbol, sy], ignore_index=True)
            per=pd.read_csv("./history/data/symbol.txt")
            per.columns=['Symbol']
            df_symbol = pd.concat([df_symbol, per], ignore_index=True)
            df_symbol= df_symbol.drop_duplicates(ignore_index=True)


            return   df_symbol
        except Exception as error:
            st.error(error)


    @st.cache_data
    def getSectorerformance():
        if 'df2' not in st.session_state:
            df2 = pd.read_csv("./history/data/sector.csv")
        else:
            df2 =st.session_state['df2']
        return  df2
    @st.cache_data
    def getMegaCapCompanies():
        if 'df3' not in st.session_state:
            df3 = pd.read_csv("./history/data/mega_capCompanies.csv")
        else:
            df3 = st.session_state['df3']
        return  df3
    @st.cache_data
    def getDaXCompanies():
        if 'df4' not in st.session_state:
            df4 = pd.read_csv("./history/data/dax_companies.csv")
        else:
            df4 = st.session_state['df4']
        return  df4
    # @st.cache_data
    # def getStockPerformance():
    #     if 'df_per' not in st.session_state:
    #         df_per = get_performance()
    #         df_per= (df_per.sort_values(by='1yr_performance', ascending=False)).reset_index(drop=True)
    #         return  df_per
    def getETFPerformance():
        if 'df_etf' not in st.session_state:
            #C:\Users\ainea\PycharmProjects\AI Driven applications\Frontend\history\data.py symbol.txt
            df_etf=pd.read_csv("./history/data/df_etf.csv")
            #df_sy = pd.read_csv("./history/data/symbol.txt")
            df_etf=(df_etf.sort_values(by='1yr_performance', ascending=False)).reset_index(drop=True)
            return   df_etf
    @st.cache_data
    def getTop500Companies():
        if 'df5' not in st.session_state:
            df5 = pd.read_csv("./history/data/s_p500.csv")
        else:
            df5 =  st.session_state['df5']
        return  df5
    @st.cache_data
    def getGermanyStocks():
        if 'df6' not in st.session_state:
            df6 = pd.read_csv("./history/data/german_stocks.csv")
        else:
            df6 =st.session_state['df6']
        return  df6
    @st.cache_data
    def getdagAndjones():
        if 'df_dag_jones' not in st.session_state:
            df_dag_jones=pd.DataFrame()
            df_daq=pd.read_csv(f'.\history\data\/nasdaq_100.csv')
            daq_ticker = df_daq[['Symbol']]
            daq_ticker.columns = ['symbol']
            df_dag_jones=(df_dag_jones._append(daq_ticker))
            df_jones = pd.read_csv(f'.\history\data\dow_jones.csv')
            jones_ticker = df_jones[['Symbol']]
            jones_ticker.columns = ['symbol']
            df_dag_jones= df_dag_jones._append(jones_ticker,ignore_index=True)
            df_dag_jones =  df_dag_jones.drop_duplicates(ignore_index=True)
        else:
            df_dag_jones =st.session_state['df_dag_jones']
        return  df_dag_jones




    tab1, tab2, tab3,tab4,tab5 = st.tabs(["Overview","Top 500 Stocks & Germany Stocks",  "Individual Stock", "AI News Article", " AI Stock Recommendation"])

    with tab1:
        st.header("Industry Performance")
        try:
            df1 = getIndustryPerformance()
            df1=df1.replace(',', '', regex=True)
            df1 = df1.replace('%', '', regex=True)
            #df1 = df1.replace("-",  "", regex=True)
            #df.set_index("Date", inplace=True)

            # config = {
            #     "_index": st.column_config.DateColumn("Month", format="MMM YYYY"),
            #     "Total": st.column_config.NumberColumn("Total ($)"),
            # }

            df1['Market Cap'] = (df1['Market Cap'].str.replace('B', '')).astype(float)
            #df1 = df1.astype(float)
            #apply(lambda x: str(x).format('{+:f}'))).astype(float)
            df1['1D Change'] =  (df1['1D Change'].apply(lambda x: str(x).format('{+:f}')))
            df1['1Y Change'] = (df1['1Y Change'].apply(lambda x: str(x).format('{+:f}')))
            df1['Div. Yield'] = df1['Div. Yield'].str.replace('%', '')
            df1['Profit Margin'] = (df1['Profit Margin'].str.replace('%', '')).astype(float)
            #1D Change,1Y Change Div. Yield,PE Ratio,Profit Margin,color="Industry Name"
            col1, col2, col3 = st.columns(3)
            col1.metric("Max 1D Change", df1['1D Change'].max())
            col2.metric("Max Market Cap in Billions",  df1['Market Cap'].max())
            col3.metric("No. Industry", df1['Industry Name'].count())
            #st.dataframe(df1.style.highlight_max(axis=0),use_container_width=True)
            #st.bar_chart(df1.sort_values(by="Market Cap", ascending=False), x="Industry Name", y="Market Cap",  color=["#FF0000"], horizontal=True)
            st.header("1 Day  Performance based on Industry")
            ind_event=st.dataframe(df1.style.highlight_max(axis=0),                 hide_index=True,
                    on_select="rerun",
                    selection_mode="multi-row",use_container_width=True)
            event_ind = ind_event.selection.rows
            if len(event_ind) < 1 :
                df1=df1
            else :
                filtered_df1 = df1.iloc[event_ind]
                df1=filtered_df1
            pie= alt.Chart(df1, title="1 Day  Performance based on Industry").mark_arc(innerRadius=50).encode(
                theta= alt.Theta(field="1D Change",type="quantitative"),
                color=alt.Color(field="Industry Name",type="nominal")
            ).interactive()
            st.altair_chart(pie,  theme="streamlit", use_container_width=True)
            #col1, col2, col3 = st.columns(3)

        except Exception as error:
            st.write(error)
        try:
            st.header("Sector Performance")
            df2 = getSectorerformance()
            df2 = df2.replace(',', '', regex=True)
            df2 = df2.replace('%', '', regex=True)
            col4, col5, col6,col7 = st.columns(4)
            col4.metric("Max 1D Change", df2['1D Change'].max())
            col5.metric("Max Market Cap in Billions",  df2['Market Cap'].max())
            col6.metric("No. Industry", df2['Sector Name'].count())
            col7.multiselect('Sector',df2['Sector Name'])
            sector_event=st.dataframe(df2.style.highlight_max(axis=0),                 hide_index=True,
                    on_select="rerun",
                    selection_mode="multi-row",use_container_width=True)
            event_sec = sector_event.selection.rows
            if len(event_sec) < 1 :
                df2=df2
            else :
                filtered_df2 = df2.iloc[event_sec]
                df2=filtered_df2
            pie2= alt.Chart(df2,title="1 Year Performance based on Sector").mark_arc(innerRadius=50).encode(
                theta= alt.Theta(field="1Y Change",type="quantitative"),
                color=alt.Color(field="Sector Name",type="nominal")
            ).interactive()
            st.header("1 Year Performance based on Sector")
            st.altair_chart(pie2,  theme="streamlit", use_container_width=True,on_select="rerun")
        except  Exception as error1:
            st.write(error1)
        st.header("Mega CAP Companies in B")
        try:
            df3 = getMegaCapCompanies()
            df3 = df3.replace(',', '', regex=True)
            df3 = df3.replace('%', '', regex=True)
            df3['Market Cap'] = (df3['Market Cap'].str.replace('B', '')).astype(float)
            df3['Revenue'] = (df3['Revenue'].str.replace('B', '')).astype(float)
            # df3 = df2.replace(',', '', regex=True)
            #   df3 = df2.replace('%', '', regex=True)

            st.dataframe(df3.style.highlight_max(axis=0),use_container_width=True)
        except Exception as error2:
            st.write(error2)
        st.header("Germany DAX Companies")
        try:
            df4 =  getDaXCompanies()
            df4 = df4.replace(',', '', regex=True)
            df4 = df4.replace('%', '', regex=True)
            #df4['Indexgewicht in %'] = round((df4['Indexgewicht in %']).astype(float)/100,2)
            df4 =df4.round(2)
            dax_companies =df4['Ticker-en'].tolist()
           # df3['Revenue'] = (df3['Revenue'].str.replace('B', '')).astype(float)
            # df3 = df2.replace(',', '', regex=True)
            #   df3 = df2.replace('%', '', regex=True)
            event=st.dataframe(df4.style.highlight_max(axis=0),
                     use_container_width=True,
                     hide_index=True,
                    on_select="rerun",
                    selection_mode="multi-row")
            event = event.selection.rows
            if len(event) < 1 :
                df4=df4
            else :
                filtered_df = df4.iloc[event]
                df4=filtered_df
            pie3= alt.Chart(df4, title="Distribution based on Index weight").mark_arc(innerRadius=50).encode(
                theta=alt.Theta(field="Index weighting (%)1",type="quantitative"),
                color=alt.Color(field="Company",type="nominal")
            ).interactive()
            st.header("Distribution based on Index weight")
            st.altair_chart(pie3,  theme="streamlit", use_container_width=True,on_select="rerun")
        except Exception as error2:
            st.write(error2)

    with tab2:
        st.header("ETFs, DAX, DOW JONES and Mega CAP Companies Performance ")
        # try:
        #     df_per=getStockPerformance()
        #     st.dataframe(df_per, column_config={
        #     "website": st.column_config.LinkColumn()})
        # except Exception as perf:
        #     st.error(perf)
        st.subheader("ETFS Performance")
        try:
            df_etf= getETFPerformance()
            st.dataframe(df_etf)
            #st.bar_chart(df_etf.set_index('Ticker'), values('1yr_performance'))
            bareft= alt.Chart(df_etf, title="EFT'S Performance").mark_bar().encode(
                x='Ticker:N',
                y='1yr_performance:Q',
                color='Ticker:N',
            ).interactive()
            st.header("EFT'S Performance")
            st.altair_chart(bareft,  theme="streamlit", use_container_width=True,on_select="rerun")
        except Exception as etf:
            st.error(etf)
        st.header("Stocks traded in Germany")
        st.header("Top 500 Companies")
        try:
            df5 =  getTop500Companies()
           # df5 = df4.replace(',', '', regex=True)

           # df3['Revenue'] = (df3['Revenue'].str.replace('B', '')).astype(float)
            # df3 = df2.replace(',', '', regex=True)
            #   df3 = df2.replace('%', '', regex=True)
            event5=st.dataframe(df5.style.highlight_max(axis=0),
                     use_container_width=True,
                     hide_index=True,
                    on_select="rerun",
                    selection_mode="multi-row")
            event5 = event5.selection.rows
            if len(event) < 1 :
                df5=df5
            else :
                filtered_df = df5.iloc[event]
                df5=filtered_df
            df_sectory=(df5.groupby('GICS Sector')['Symbol'].count()).reset_index()
            df_sectory.columns= ['Sector', 'Counts']
            bar4= alt.Chart(df_sectory, title="Top Companies based on sector").mark_bar().encode(
                x='Sector:N',
                y='Counts:Q',
                color='Sector:N',
            ).interactive()
            st.header("Top Companies based on sector")
            st.altair_chart(bar4,  theme="streamlit", use_container_width=True,on_select="rerun")
        except Exception as error2:
            st.write(error2)
        #getStockPerformance()
        st.header("Stocks traded in Germany")
        try:
            df6=   round(getGermanyStocks(),2)
           # df5 = df4.replace(',', '', regex=True)

           # df3['Revenue'] = (df3['Revenue'].str.replace('B', '')).astype(float)
            # df3 = df2.replace(',', '', regex=True)
            #   df3 = df2.replace('%', '', regex=True)
            event6=st.dataframe(df6.style.highlight_max(axis=0),
                     use_container_width=True,
                     hide_index=True,
                    on_select="rerun",
                    selection_mode="multi-row")

        except Exception as error2:
            st.write(error2)

    with tab3:
        try:
            st.header("Select Indivual Stock Analysis")
            df_symbol=getTickers()
        except:
            pass

        if 'option' not in st.session_state:
            option = st.selectbox(
                "Which Stock Would you like to buy?", df_symbol['Symbol'],
                index=1

            )
        try:
            df, df_monthly,df_data,df_f=get_historical_data(option )
            st.write("Daily Historical Data")

            event_df =st.dataframe(df.style.highlight_max(axis=0),use_container_width=True)




            fig = px.line(df, x="date", y=['close', 'sma_5_day', 'sma_20_day', 'sma_50_day','sma_200_day'],
                          hover_data={"date": "|%B %d, %Y"},
                          title='Stock price timeseries evolution')
            fig.update_xaxes(
                dtick="M1",
                tickformat="%Y %B",  ticklabelmode="period", minor=dict(ticks="inside", showgrid=True))

            st.plotly_chart(fig, theme="streamlit", use_container_width=True)
            st.write("Monthly Historical Data")

            st.dataframe(df_monthly)

            st.write("Fundamental Analysis - Company Information")
    # "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"
            try:
                #df_data['website']=df_data['website'].apply(lambda x: "[symbol]+("+str(x)+")")
                st.dataframe(df_data,use_container_width=True,  column_config={
            "website": st.column_config.LinkColumn()
        })
            except Exception as error :
                pass
                #st.error(error)

            st.write("Fundamental Analysis - Company Financial Ratios")

            try:
                st.dataframe(st.dataframe(df_f))
            except Exception as f_error:
                pass
                #st.write(f_error)


        except Exception as errordf:
            st.write(errordf)
        st.header("Now Comes Forecasts with VECM Model")
        try:
            pred=get_Forecast_data(df)
            st.dataframe(pred.style.highlight_max(axis=0),use_container_width=True)
        except Exception  as ForecastError:
            st.write(ForecastError)
        try:
            fig1 = px.line(pred, x="prediction_date", y=['close', 'close_lower', 'close_upper', 'high', 'low'],
                          hover_data={"prediction_date": "|%B %d, %Y"},
                          title='Stock price Forecast for the next 20 days')
            fig1.update_xaxes(
                dtick="M1",
                tickformat="%d-%m-%Y", ticklabelmode="period", minor=dict(ticks="inside", showgrid=True))

            st.plotly_chart(fig1, theme="streamlit", use_container_width=True)
        except Exception as errorpred:
            print(errorpred)

    with (tab4):

        st.header("Stock News Artikel generated by AI  Expert Agents")
        df_symbol=getTickers()
        option1 = st.selectbox(
            "Which Stock Would you like to buy?", df_symbol['Symbol'],
            key='option1',
            index=1
        )


        try:

            st.markdown(getCrewAINews(option1))

        except Exception as error:
            st.error(error)
        file_name = f'{option1}_retrieve_news_task.md'
        st.subheader(f"News Retriever for the given stock{option1}")
        try:
            with open(file_name, 'r') as f:
                research = (f.read())
                f.close()
            st.markdown(research)
            file_news = f'{option1}_ai_news_write_task.md'
            with open(file_news, 'r') as f:
                news_expert = (f.read())
                f.close()

            file_path = f"{option1}_ai_article.md"  # Replace with your markdown file path

            st.subheader("Download the news article")
            download_markdown_file(file_path,  news_expert)
        except:
            pass
    with (tab5):
        st.header("Stock Recommandation with Crew AI Stockmarket Expert Agents")
       # st.header("Stock News Artikel generated by AI  Expert Agents")
        df_symbol = getTickers()
        option2 = st.selectbox(
            "Which Stock Would you like to buy?", df_symbol['Symbol']
            ,
            key='option2',
            index=1
        )


        try:
            st.subheader("Summary  and Recommendations")
            results_news=getCrewAIAgentRecommendation(option2)
            st.markdown(results_news)


        except Exception as error:
            st.error(error)
        st.subheader("Reader and Fundamental Analyst")
        file_st = f'./Crew_AI/Reports/{option2}_filereader_task.md'
        try:
            with open(file_st, 'r') as f:
                fil_reader = (f.read())
                f.close()
            st.markdown(fil_reader)

        except:
            pass

        try:

            st.subheader("Finance  Analyst")
            file_f=f'./Crew_AI/Reports/{option2}_financial_analysis_task.md'
            try:
                with open( file_f, 'r') as f:
                    finance_expert=(f.read())
                    f.close()
                st.markdown(finance_expert)

            except:
                pass
            #AAPL_research_task.md
        except Exception as error:
            st.error(error)
        try:

            st.subheader("News  and Market Sentiment Analyst")
            file_r=f'./Crew_AI/Reports/{option2}_research_task.md'
            try:
                with open( file_r, 'r') as f:
                    research_expert=(f.read())
                    f.close()
                st.markdown(research_expert)

                st.subheader("Download the Stock Recommendation")
                file_adv = f'./Crew_AI/Reports/{option2}_recommend.md'
                with open(file_adv, 'r') as f:
                    advisor_expert=(f.read())
                    f.close()

                file_path = f"{option2}_ai_advisor.md"  # Replace with your markdown file path

                # Create a dummy markdown file if it doesn't exist (for testing):

                download_markdown_file(file_path, advisor_expert )
            except:
                pass
            #AAPL_research_task.md
        except Exception as error:
            st.error(error)












