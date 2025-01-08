from  StockmarketAnalysis.tasks.stock_tasks import StockmarketTasks
from  StockmarketAnalysis.agents.stock_agents import StockmarketAgents
from crewai import Crew, Process, Task
import pandas as pd
import yfinance as yf
from textwrap import dedent
from dotenv import  load_dotenv
load_dotenv()
import os

class StockMarketCrew:

    def __init__(self,germin_key,serp_key, company_stock, hist_csv, financial_csv, company_info="company_info.csv"):
        self.germin_key=germin_key
        self.serp_key=serp_key
        self.company_stock =company_stock
        self.hist_csv = hist_csv
        self.financial_csv =financial_csv
        self.company_info = company_info
    def LoadYahoofinanceData(self):
        ticker = yf.Ticker(self.company_stock)
        # Fetch historical market data
        historical_data = ticker.history(period="1y")
        historical_data=(historical_data[['Close','Volume']].sort_values('Date', ascending=False))
        historical_csv = self.hist_csv
        financial_csv_f = self.financial_csv
        (historical_data).to_csv(f"./agents/data/{historical_csv}")
        df_info = (pd.DataFrame(ticker.info)).fillna(0)
        df_info.to_csv(f"./agents/data/{self.company_info}")
        df_financials = df_financials = ((ticker.financials).T)  # Change 'asytpe' to 'astype'
        print(df_financials.head(10))
        # C:\Users\ainea\PycharmProjects\AI Driven applications\StockmarketAnalysis\data
        df_financials.to_csv(f"./agents/data/{financial_csv_f}")
        ticker.actions.to_csv("./agents/data/actions.csv")
    def __tip_section(self):
        return "If you do your BEST WORK, I'll tip you $100!"


    def run(self):
        SK =StockmarketTasks()
        stockagent=StockmarketAgents()
        file_reader=stockagent.FileReader(self.germin_key,self.serp_key)
        stock_f_analysis_agent= stockagent.FinancialAnalysist(self.germin_key,self.serp_key)
        research_agent=stockagent.Research_Analyst(self.germin_key,self.serp_key)
        stock_experte_agent= stockagent.StockmarketExpert(self.germin_key,self.serp_key)
        stock_adivor_agent = stockagent.PrivateInvestorAdvisor(self.germin_key,self.serp_key)
        try:
            file_reader_tsk=SK.Read_Filetask(file_reader,self.company_stock,self.hist_csv,self.financial_csv,self.company_info)
        except Exception as fileerr:
            print(fileerr)
        try:
            stock_f_analysis_tsk=  SK.financial_analyst_task(stock_f_analysis_agent,self.company_stock,self.hist_csv,self.financial_csv,self.company_info)
        except Exception as f_anerror:
            print(f_anerror)
        research_tsk=  SK.Research_Analyst_task(research_agent,self.company_stock)

        context_exp=file_reader_tsk
        stock_experte_tsk = SK.StockmarketExpert_Task(stock_experte_agent, context_exp,self.company_stock)
        #context_rec=file_reader_tsk,stock_f_analysis_tsk,research_tsk, stock_experte_tsk

        description_recommend = dedent(f"""
                    Review and synthesize the analyses provided by the
                    previous tasks .
                    Combine these insights to form a comprehensive
                    investment recommendation. You MUST Consider all aspects, including financial
                    health, market sentiment, and qualitative and quantative analysis.
                    Make sure to include a section that shows insider
                    trading activity, and upcoming events like earnings.
                    You Must also include the urls sources for further  analysis.
                     {self.__tip_section()}
                """)
        expected_output_recommend = dedent("""
                    Your final answer MUST be a recommendation for your customer.
                    It MUST include the overall recommandation with values Buy, Hold or Sell.
                    It should be a full super detailed report, providing a
                    clear investment stance and strategy with supporting evidence.
                    Make it pretty and well formatted for your customer.Formatted in markdown without ``` """)
        output_csv_file = f'./Crew_AI/Reports/{self.company_stock}_recommend.md'


        stock_recommend_tsk =Task(description=description_recommend,
                              expected_output=expected_output_recommend,
                              agent= stock_adivor_agent ,
                              context=[file_reader_tsk, stock_f_analysis_tsk, research_tsk,stock_experte_tsk],
                              output_file=output_csv_file)


        crew = Crew(
            agents=[file_reader,
                   stock_f_analysis_agent,
                    research_agent,stock_experte_agent,
                   stock_adivor_agent ],
            tasks=[ file_reader_tsk,stock_f_analysis_tsk, research_tsk, stock_experte_tsk, stock_recommend_tsk],
            process=Process.sequential,
            memory=True,
            cache=True,
            verbose=True,
            max_rpm=50,
            share_crew=True
        )
        result = crew.kickoff()
        return result





# if __name__ == "__main__":
#     #text = input("Yell something at a mountain: ")
#     StockMarketCrew("AAPL", "historical_data.csv", "financial_data.csv").run()
#
#     ftse100_tickers = ['III.L', 'AV.L', 'ABF.L', 'AZN.L']  # Replace with actual FTSE 100 tickers
#     data = yf.download(ftse100_tickers, start="2023-01-01", end="2023-12-31")
#     print(data)
