
from crewai import Agent, LLM
from dotenv import  load_dotenv
import os
from StockmarketAnalysis.Tools.ai_tools  import *
import streamlit as st

from textwrap import dedent


#germinApiKey()
#SerpApiKey()

from crewai_tools import (WebsiteSearchTool,
                          CodeInterpreterTool,
                          ScrapeWebsiteTool, SerperDevTool,
                          CSVSearchTool, DirectoryReadTool,FileWriterTool,

                          FileReadTool, PDFSearchTool)


class StockmarketAgents():
    def __init__(self,germin_key,serp_key,model="gemini/gemini-1.5-pro"):
        self.germin_key=germin_key
        self.serp_key=serp_key
        self.model=model
      
        os.environ["GOOGLE_API_KEY"]=self.germin_key
        os.environ['SERPER_API_KEY']=self.serp_key

    def FileReader(self) :
      
        llm = LLM(
            model=self.model,
            temperature=0.3,
            verbose=True,
            api_key=self.germin_key)
        seper_dev_tool = SerperDevTool(
        n_results=5,
       # country='de',
       # locale='de',
        api_key=self.serp_key,
        verbose=True
        )
        return Agent(llm=llm,
                          role=' File Reader Expert',
                          goal='Extract relevant information from a given file with columns like  Close, high,open, volume and low stock prices. Identity any patterns that can influence future stock price. ',
                          memory=True,
                          backstory=("""
                                 With years of experience  with yfinance historical data, you quickly identity trends, volatility and financial healthy of any company stock. 
                                 You're python expert and you can read any file and extract  relevant information  and patterns. 
                               """),
                          tools=[DirectoryReadTool("./history/data"),
                           FileReadTool(),
                            seper_dev_tool,
                            FileWriterTool()
                                ],
                          allow_delegation=False,
                          verbose=True

                          )


    def FinancialAnalysist(self):
        llm = LLM(
            model=self.model,
            temperature=0.3,
            verbose=True,
            api_key=self.germin_key)
        seper_dev_tool = SerperDevTool(
          #country='de',
        api_key=self.serp_key,
        verbose=True
        #locale='de'
        )
        role_fa = "The Best Financial Analyst"
        goal_fa = "Impress all customers with your financial data and market trends analysis. You are expert in coding with python and expert in solving mathematical operations."
        backstory_fa = """The most seasoned financial analyst with lots of expertise in stock market analysis and investment
            strategies that is working for a super important customer."""

        return Agent(
            role=role_fa,
            goal=goal_fa,
            backstory=backstory_fa,
            llm=llm,
            tools=[
                    seper_dev_tool,
                 # ScrapeWebsiteTool(),
                CalculatorTool(),
                FileWriterTool()
                #CodeInterpreterTool(unsafe_mode=True)
                    ],
            allow_delegation=False,
                verbose=True)

    def Research_Analyst(self):
        llm = LLM(
            model=self.model,
            temperature=0.7,
            verbose=True,
            api_key=self.germin_key)
        web_search_tool = WebsiteSearchTool()
        seper_dev_tool = SerperDevTool(
          #country='de',
                                       api_key=self.serp_key
                                      # locale='de'
                                      )
        role_ra = dedent("Staff Research Analyst")
        goal_ra = """Being the best at gathering, interpreting data and amazing
            your customer with it"""
        backstory_ra = """Known as the BEST research analyst, you're skilled in sifting through news, company announcements,
            and market sentiments. Now you're working on a super important customer."""

        return Agent(
            role=role_ra,
            goal=goal_ra,
            backstory=backstory_ra,
            llm=llm,
            tools=[

                seper_dev_tool,
               # web_search_tool,

              #ScrapeWebsiteTool()
                FileWriterTool(),

                  ],
            allow_delegation=True,
                verbose=True)

    def StockmarketExpert(self):
        llm = LLM(
            model=self.model,
            temperature=0.3,
            verbose=True,
            api_key=self.germin_key)
        web_search_tool = WebsiteSearchTool()
        seper_dev_tool = SerperDevTool(
          #country='de',
                                       api_key=self.serp_key
                     #                  locale='de'
                                      )
        role_fe = "The BEST and MOST Experience Stockmarket Expert"
        goal_fe= ("Conduct a thorough a examination of a give  company stock."
                  "Comparing it to indices like   S&P 500 I, DAX, MSCI world and other ETFS. ")
        backstory_fe = """You have decades of experience in daily trading and long term investment with great success. 
        You always impress investors with outstanding analysis skills."""

        return Agent(
            role=role_fe,
            goal=goal_fe,
            backstory=backstory_fe,
            llm=llm,
            tools=[
                    seper_dev_tool,
                #ScrapeWebsiteTool(),
                    CalculatorTool(),
                FileWriterTool()
                    ],
            allow_delegation=False,
                verbose=True)

    def PrivateInvestorAdvisor(self) :
        llm = LLM(
            model=self.model,
            temperature=0.3,
            verbose=True,
            api_key=self.germin_key)
        seper_dev_tool = SerperDevTool(
          #country='de',
                                       api_key=self.serp_key
                             #          locale='de'
        )
        role_IA = dedent("Private Investment Advisor")
        goal_IA =dedent( """
            Impress your customers with full analyses over stocks and summerizing all information provided by other agents""")
        backstory_IA = """You're the most experienced investment advisor with decades of successful investiments in different company stocks 
            and you combine various analytical insights to formulate
            strategic investment advice. You are now working for
            a super important customer you need to impress."""
        return Agent(role=role_IA, goal=goal_IA,
                                   backstory=backstory_IA,
                                   llm=llm,
                                   tools=[seper_dev_tool,
                                   FileWriterTool()],
                                   allow_delegation=False,
                                   memory=True,
                                   verbose=True

                                   )







