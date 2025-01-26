from  StockmarketAnalysis.agents.stock_agents import  StockmarketAgents
from crewai import Agent, Crew, Process, Task
from dotenv import  load_dotenv
from instructor import llm_validator
import os
import pandas as pd
from test_unstructured.staging.test_prodigy import output_csv_file

from textwrap import dedent
from crewai_tools import (YoutubeChannelSearchTool,WebsiteSearchTool,
                          YoutubeVideoSearchTool,CodeInterpreterTool,
     ScrapeWebsiteTool,SeleniumScrapingTool,SerperDevTool,
                          CSVSearchTool, DirectoryReadTool,

                          FileReadTool, PDFSearchTool)
class StockmarketTasks():
    def __init__(self,germin_key,serp_key):
        self.germin_key=germin_key
        self.serp_key=serp_key
        os.environ["GOOGLE_API_KEY"]=self.germin_key
        os.environ['SERPER_API_KEY']=self.serp_key
    webscraper=ScrapeWebsiteTool()
    web_search=WebsiteSearchTool()
    python_coder= CodeInterpreterTool(unsafe=True)

    def __tip_section(self):
        return "If you do your BEST WORK, I'll tip you $10000!"

    def Read_Filetask(self,agent,company_stock,historical_data,financial_data,company_info,company, sector) :
        import yfinance as yf
        p = yf.Ticker(str(company_stock))
        currentPrice = p.info['currentPrice']
        if  p.info['beta']:
          beta = p.info['beta']
        else:
          beta =None
          
        #beta = p.info['beta']
        quickRatio = p.info['quickRatio']
        currentRatio = p.info['currentRatio']
        trailingPE = p.info['trailingPE']
        if  p.info['earningsGrowth']:
             earningsGrowth=p.info['earningsGrowth']
        else:
           earningsGrowth=None
        if  p.info['revenueGrowth']:
          revenueGrowth = p.info['revenueGrowth']
        else:
           earningsGrowth =None
          
          
        #earningsGrowth= p.info['earningsGrowth']
        #revenueGrowth = p.info['revenueGrowth']

        description_FR = dedent(f""" You are working for the MOST IMPORTANT customer and you have to impress  him with the BEST Results!. 
            Conduct a thorough analysis of {company_stock}'s stock 
            financial health and market performance by reading and interpreting the csv files .
            Extract these KPI's from the give csv files: 
            PE Ratio,Forward PE, PS Ratio,PB Ratio, Quick Ratio,Current Ratio, beta, 
            bookValue,priceToBook, totalCashPerShare, debtToEquity,revenuePerShare,
            returnOnEquity, revenueGrowth, earningsGrowth  for this  {company_stock} stock. 
            You MUST Explain each value and interpret it . Based on the analysis make    recommadation to buy, hold or sell. 
            You MUST ONLY extract from these files: 
            *** Parameters ***: 
            monthly historical csv file: {historical_data}
            KPI ratios csv file: {financial_data}
            company stock info  csv file: {company_info}
            company name: {company}
            sector: {sector}
            *** Addtionaly Informations from Yahoo Finance ***: 
            Current Stock price: {currentPrice }
            Yahoo Beta : {beta}
            Current Ratio: {currentRatio}
            Quick Ratio: {quickRatio}
            Trailing PE: {trailingPE}
            Yahoo Finance Eanrings Growth: {earningsGrowth}
            Yahoo Finance Revenue Growth: {revenueGrowth}
             {self.__tip_section()}
            """)
        expected_output_FR = dedent("""
            The final report MUST expand on the summary provided but now
            including a clear assessment of the stock's financial healthy and suggestions.
        """)

        output_csv_file=f'./Crew_AI/Reports/{company_stock}_filereader_task.md'

        return Task(description=description_FR,
                                           expected_output=expected_output_FR,
                                           agent=agent,
                                           output_file=output_csv_file)
    def financial_analyst_task(self,agent,company_stock,company, sector,summary,industry,website) :
        date=pd.to_datetime('today').date()
        yr = pd.to_datetime('today').year
        description_FA = dedent(f""" You are working for the MOST IMPORTANT customer and you have to impress  him with the BEST Results !.
            Conduct a thorough analysis of {company_stock}'s stock financial health and market performance based on internet research. The current year is {yr} and current date: {date}.
             Also, analyze the stock's performance in comparison
            to its industry peers and overall market trends. Make sure to use the latest data and information.  
            You MUST INCLUDE  a section with Top 5 Giants Companies  in this industry {industry} and sector:  {sector} as bullet points.
            *** Parameters ***: 
            company name: {company}
            sector: {sector}
            industry:{industry}
            company description: {summary}
            company website: {website}
             
               {self.__tip_section()} """)
        expected_output_FA = dedent("""
            The final report must expand on the summary provided but now
            including company overview,  a clear assessment of the stock's financial standing, its strengths and weaknesses,
            and how it fares against its competitors   in the current market scenario.
            Make sure to use the most recent data possible.
        """)
        output_csv_file = f'./Crew_AI/Reports/{company_stock}_financial_analysis_task.md'

        return Task(description=description_FA,
                                           expected_output=expected_output_FA,
                                           agent=agent,

                                           output_file=  output_csv_file)
    def Research_Analyst_task(self,agent,company_stock,company,sector,industry, summary, website)-> Task :
        date=pd.to_datetime('today').date()
        yr = pd.to_datetime('today').year



        description_re = dedent(f"""
               You are working for the MOST IMPORTANT customer and you have to impress  him with the BEST Results !.
                Collect and summarize recent news articles, press
                releases, and market analyses related to the {company_stock} stock and its industry.The current year is {yr} and current date: {date}.
                Pay special attention to any significant events, market sentiments, and analysts' opinions. 
                You Must include the overall trend bullish or bearish.
                Also include upcoming events like earnings and others.
            *** Parameters ***: 
                company name: {company}
                sector: {sector}
                industry:{industry}
                company description: {summary}
                company website: {website}
                  
                {self.__tip_section()}""")
        expected_output_re = dedent("""
        A report that includes a comprehensive summary of the latest news, current date ,
        any notable shifts in market sentiment, and potential impacts on the stock. Also make sure to return the stock ticker as {company_stock}.
        Make sure to use the most recent data as possible.
        """)
        output_csv_file = f'./Crew_AI/Reports/{company_stock}_research_task.md'
        return Task(description=description_re,
                                            expected_output=expected_output_re,
                                            agent=agent,
                                            output_file= output_csv_file)
    def  StockmarketExpert_Task(self,agent,context,company_stock, company) -> Task:
        # draft_job_posting_task:
        date=pd.to_datetime('today').date()
        yr = pd.to_datetime('today').year
        description_F_analysis = dedent(f"""
            You are working for the MOST IMPORTANT customer and you have to impress  him with the BEST Results !.
            Analyze the latest news and sentiments  for
             the stock {company_stock} and company name: {company}  in question as well as 10-Q and 10-K filings. The current year is {yr} and current date: {date}.
            Focus on key sections like Management's Discussion and analysis,
             financial statements, insider trading activity,
            and any disclosed risks.
            Extract relevant data and insights that could influence
            the stock's future performance.Use also  analyses provided by the File Reader Expert, 
            Staff Research Analyst and ,The Best Financial Analyst
             {self.__tip_section()}
            """)
        expected_output_Filings = dedent("""
            Final answer must be an expanded report that now also highlights significant findings
            from these filings including any red flags or positive indicators for your customer.
        """)
        output_csv_file = f'./Crew_AI/Reports/{company_stock}_investment_advisor.md'
        return Task(description=description_F_analysis,
                                    expected_output=expected_output_Filings,
                                    agent=agent,
                                    context=[context],
                                    output_file= output_csv_file)




