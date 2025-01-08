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
    webscraper=ScrapeWebsiteTool()
    web_search=WebsiteSearchTool()
    python_coder= CodeInterpreterTool(unsafe=True)
    #directory= DirectoryReadTool("./data")
    #file_reader=FileReadTool()
    pdf_search=PDFSearchTool()
    stockagent =   StockmarketAgents()
   # csv_file_search= CSVSearchTool()
    def __tip_section(self):
        return "If you do your BEST WORK, I'll tip you $100!"

    def Read_Filetask(self,agent,company_stock,historical_data,financial_data,company_info) :
        description_FR = dedent(f"""
            Conduct a thorough analysis of {company_stock}'s stock financial health and market performance by reading and interpreting the csv files .
            Extract these KPI's from the give csv files: 
            PE Ratio,Forward PE, PS Ratio,PB Ratio, Quick Ratio,Current Ratio, beta, 
            bookValue,priceToBook, totalCashPerShare, debtToEquity,revenuePerShare,
            returnOnEquity, revenueGrowth, earningsGrowth  for this  {company_stock} stock. 
            You MUST Explain each value and interpret it . Based on the analysis make    recommadation to buy, hold or sell. 
            You MUST ONLY extract from these files: 
            *** Parameters ***: 
            monthly_{company_stock}_data historical csv file: {historical_data}
            {company_stock}_qfinancial_ratios.csv csv file: {financial_data}
            company stock info  csv file: {company_info}
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
    def financial_analyst_task(self,agent,company_stock,historical_data,financial_data,company_info) :
        date=pd.to_datetime('today').date()
        yr = pd.to_datetime('today').year
        description_FA = dedent(f"""
            Conduct a thorough analysis of {company_stock}'s stock financial health and market performance based on internet research. The current year is {yr} and current date: {date}.
             Also, analyze the stock's performance in comparison
            to its industry peers and overall market trends. Make sure to use the latest data and information.  {self.__tip_section()} """)
        expected_output_FA = dedent("""
            The final report must expand on the summary provided but now
            including a clear assessment of the stock's financial standing, its strengths and weaknesses,
            and how it fares against its competitors in the current market scenario.
            Make sure to use the most recent data possible.
        """)
        output_csv_file = f'./Crew_AI/Reports/{company_stock}_financial_analysis_task.md'

        return Task(description=description_FA,
                                           expected_output=expected_output_FA,
                                           agent=agent,

                                           output_file=  output_csv_file)
    def Research_Analyst_task(self,agent,company_stock)-> Task :
        date=pd.to_datetime('today').date()
        yr = pd.to_datetime('today').year

        description_re = dedent(f"""
                Collect and summarize recent news articles, press
                releases, and market analyses related to the {company_stock} stock and its industry.The current year is {yr} and current date: {date}.
                Pay special attention to any significant events, market sentiments, and analysts' opinions. 
                You Must include the overall trend bullish or bearish.
                Also include upcoming events like earnings and others.  {self.__tip_section()}""")
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
    def  StockmarketExpert_Task(self,agent,context,company_stock) -> Task:
        # draft_job_posting_task:
        date=pd.to_datetime('today').date()
        yr = pd.to_datetime('today').year
        description_F_analysis = dedent(f"""
            Analyze the latest news and sentiments  for
             the stock {company_stock}  in question as well as 10-Q and 10-K filings. The current year is {yr} and current date: {date}.
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




