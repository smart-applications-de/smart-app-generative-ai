# -*- coding: utf-8 -*-
"""News and  Marketing.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1wJtD_aKmLQ85hSh_7moUIdYhRYquaBlL
"""


#/content/cv.md

from crewai import Agent, Task, Crew, Process
from crewai import LLM
from pydantic import BaseModel, ValidationError
from crewai_tools import (YoutubeChannelSearchTool,WebsiteSearchTool,YoutubeVideoSearchTool,CodeInterpreterTool,FileWriterTool,
     ScrapeWebsiteTool,SeleniumScrapingTool,SerperDevTool, CSVSearchTool, DirectoryReadTool, FileReadTool, PDFSearchTool)
import os
from typing import List
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from pydantic import BaseModel, Field
from textwrap import dedent
from dotenv import  load_dotenv


def CrewStocknews(germin_api, serp_api, topic, year, date,company, sector, summary,model="gemini/gemini-1.5-pro"):
    os.environ["GOOGLE_API_KEY"] = germin_api
    os.environ['SERPER_API_KEY'] = serp_api
    os.environ['model'] = model
    company=company
    sector=sector
    summary=summary
    GOOGLE_API_KEY =germin_api
       # (os.environ.get('GOOGLE_API_KEY'))
    google_tool = SerperDevTool(
        n_results=5,
        api_key=serp_api,
       # SERPER_API_KEY,
        verbose=True
    )

    """# Agents"""

    # retrieve_news:
    web_search_tool = WebsiteSearchTool()
    seper_dev_tool = SerperDevTool(
	n_results=10,
        api_key=serp_api,
       # SERPER_API_KEY,
        verbose=True
    )
    llm = LLM(
    model =model,
    temperature = 0.5,
    verbose = True,
    api_key = GOOGLE_API_KEY
    )
    role_retiever = dedent(f"""
            {topic} AI News Retriever""")
    goal_retriever = dedent(f"""
            Retrieve the latest news and information related to {topic}
            Uncover cutting-edge developments in {topic}""")

    backstory_retriever = dedent("""
            You're a seasoned researcher with a knack for uncovering the latest
            developments in {topic}. Known for your ability to find the most relevant
            information and present it in a clear and concise manner.""")

    retrieve_news = Agent(
    llm = llm,
    role = role_retiever,
    goal = goal_retriever,
    backstory = backstory_retriever,
    tools = [google_tool],
    allow_delegation = False,
    memory = True,
    verbose = True)

    # website_scraper:
    role_scraper = dedent("""
            AI News Website  Researcher""")
    goal_scraper = dedent("""
            Search   and provide a summary  on  the latest news and  information.""")
    backstory_scraper = dedent("""
            You're a skilled Researcher and decades of experience  with a knack for extracting valuable information
            from websites. Known for your attention to detail and ability to navigate through information sources.""")

    website_scraper = Agent(
    llm = llm,
    role = role_scraper,
    goal = goal_scraper,
    backstory = backstory_scraper,
    tools = [google_tool, web_search_tool],
    allow_delegation = False,
    memory = True,
    verbose = True)

    # ai_news_writer:
    role_writer = dedent("""
            AI News Writer""")
    goal_writer = dedent("""
            Write a concise and informative news article based on the provided information. You MUST include the information sources as url for further reading.""")
    backstory_writer = dedent("""
            You're a skilled writer with a knack for crafting engaging and informative
            news articles. Known for your ability to distill complex information into
            clear and concise prose""")
    ai_news_writer = Agent(
    llm = llm,
    role = role_writer,
    goal = goal_writer,
    backstory = backstory_writer,

    allow_delegation = False,
    memory = True,
    verbose = True
    )

    # file_writer:
    role_fwriter = dedent("""
            AI News File Writer""")
    goal_fwriter = dedent("""
            Write the news article to a file. Make Sure you include all the information sources including urls.""")
    backstory_fwriter = dedent("""
            You're a skilled file writer with a knack for writing news articles to a file.""")
    file_writer = Agent(
    llm = llm,
    role = role_fwriter,
    goal = goal_fwriter,
    backstory = backstory_fwriter,
    tools = [FileWriterTool()],
    allow_delegation = False,
    memory = True,
    verbose = True
    )

    """Tasks Definition AI news"""

    # retrieve_news_task:
    description_ret = dedent(f"""
            Conduct a thorough research about the company stock {topic}, company name: {company}, 
            sector : {sector} and company description : {summary}
            Make sure you find any interesting and relevant latest information given
            the current year is {year}. Pay special attention to any significant events, market sentiments, and analysts' opinions. 
            You Must include the overall trend bullish or bearish. """)
    expected_output_ret = dedent("""
            A Summary on research about {topic} and  list of Top 10 websites with the most relevant information about company stock {topic} Formated as markdown. 
            You MUST Include  source urls.""")

    # agent: retrieve_news

    retrieve_news_task = Task(
    description = description_ret,
    expected_output = expected_output_ret,
    agent = retrieve_news,
    async_execution = False,
    output_file = f'{topic}_retrieve_news_task.md',

    )

    # website_scrape_task:
    description_scraper = dedent(f"""
        Get all informations provided  by AI News Retriever for  company stock {topic}, 
        company name: {company}, 
        sector : {sector} and company description : {summary}
         
         and extract ONLY the latest news.
         Search for more information like trading activies about the compay stock {topic} and company name {company} .
         Don't scrape the website because you don't have access on 
        the website content, You MUST include the summary provided by AI News Retriever. """)
    expected_output_scraper = dedent("""
        A Summary of the latest news from  formated as markdown.""")
    website_scrape_task = Task(description=description_scraper,
    expected_output = expected_output_scraper,
    agent = website_scraper,
    context = [retrieve_news_task],
    output_file = f'{topic}_website_scrape_task.md')
    # agent: website_scraper

    # ai_news_write_task:
    description_writer = dedent("""
        Summarize the information from the websites into a fully fledge news article in markdown format without '```'.""")
    expected_output_writer = dedent("""
        A fully fledge news article with the main topics, each with a full section of information.
        Formatted as markdown""")
    ai_news_write_task = Task(description=description_writer,
    expected_output = expected_output_writer,
    agent = ai_news_writer,
    context = [retrieve_news_task, website_scrape_task],
    output_file = f'{topic}_ai_news_write_task.md')
    # agent: ai_news_writer Formatted as markdown without '```'"""

    # file_write_task:
    description_fwriter = dedent("""
        Write the news article to a file""")
    expected_output = dedent("""
        A fully fledge news article with all information from previous task.  
        You MUST Include  source urls for further reading.
         Formatted in markdown without ``` """)
    file_write_task = Task(description=description_fwriter,
    expected_output = expected_output,
    agent = ai_news_writer,
    context = [ai_news_write_task, website_scrape_task, retrieve_news_task],
    output_file = f'{topic}file_write_task.md')

    input={
            'topic':topic,
            'year':year,
            'date':date
        }

    crew = Crew(
        agents=[retrieve_news,website_scraper,ai_news_writer,file_writer],
        tasks=[retrieve_news_task,website_scrape_task,ai_news_write_task,file_write_task],
        process=Process.sequential,
        memory=True,
        cache=True,
        verbose=True,
        max_rpm=50 ,
        share_crew=True)
    result = crew.kickoff(inputs=input)
    return result

from typing import List
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool, ScrapeWebsiteTool
from pydantic import BaseModel, Field

class MarketStrategy(BaseModel):
	"""Market strategy model"""
	name: str = Field(..., description="Name of the market strategy")
	tatics: List[str] = Field(..., description="List of tactics to be used in the market strategy")
	channels: List[str] = Field(..., description="List of channels to be used in the market strategy")
	KPIs: List[str] = Field(..., description="List of KPIs to be used in the market strategy")

class CampaignIdea(BaseModel):
	"""Campaign idea model"""
	name: str = Field(..., description="Name of the campaign idea")
	description: str = Field(..., description="Description of the campaign idea")
	audience: str = Field(..., description="Audience of the campaign idea")
	channel: str = Field(..., description="Channel of the campaign idea")

class Copy(BaseModel):
	"""Copy model"""
	title: str = Field(..., description="Title of the copy")
	body: str = Field(..., description="Body of the copy")


def CrewMarketAnalysis(germin_api, serp_api,year,customer_domain,project_description):
    GOOGLE_API_KEY =germin_api
       # (os.environ.get('GOOGLE_API_KEY'))
    google_tool = SerperDevTool(
        n_results=5,
        api_key=serp_api,
       # SERPER_API_KEY,
        verbose=True
    )

    """# Agents"""

    # retrieve_news:
    web_search_tool = WebsiteSearchTool()
    seper_dev_tool = SerperDevTool(country='de',

    locale = 'de')
    llm = LLM(
    model = "gemini/gemini-1.5-pro",
    temperature = 0.5,
    verbose = True,
    api_key = GOOGLE_API_KEY
    )
    # lead_market_analyst:
    role_lmarket_analyst = dedent("""
        Lead Market Analyst""")
    goal_lmarket_analyst = dedent("""
        Conduct amazing analysis of the products and competitors, providing in-depth
        insights to guide marketing strategies.""")
    backstory_lmarket_analyst = dedent("""
        As the Lead Market Analyst at a premier digital marketing firm, you specialize
        in dissecting online business landscapes.""")
    lead_market_analyst = Agent(
        llm=llm,
        role=role_lmarket_analyst,
        goal=goal_lmarket_analyst,
        tools=[ google_tool , ScrapeWebsiteTool()],
        allow_delegation=False,
        memory=True,
        verbose=True,
        backstory=backstory_lmarket_analyst)
    # chief_marketing_strategist:
    role_cm_strategist = dedent("""
        Chief Marketing Strategist""")
    goal_cm_strategist = dedent("""
        Synthesize amazing insights from product analysis to formulate incredible
        marketing strategies.""")
    backstory_cm_strategist = dedent("""
        You are the Chief Marketing Strategist at a leading digital marketing agency,
        known for crafting bespoke strategies that drive success.""")
    chief_marketing_strategist = Agent(
        llm=llm,
        role=role_cm_strategist,
        goal=goal_cm_strategist,
        tools=[google_tool , ScrapeWebsiteTool()],
        allow_delegation=False,
        memory=True,
        verbose=True,
        backstory=backstory_cm_strategist)

    # creative_content_creator:
    role_cc_creator = dedent("""
        Creative Content Creator""")
    goal_cc_creator = dedent("""
        Develop compelling and innovative content for social media campaigns, with a
        focus on creating high-impact ad copies.""")
    backstory_cc_creator = dedent("""
        As a Creative Content Creator at a top-tier digital marketing agency, you
        excel in crafting narratives that resonate with audiences. Your expertise
        lies in turning marketing strategies into engaging stories and visual
        content that capture attention and inspire action.""")
    creative_content_creator = Agent(
        llm=llm,
        role=role_cc_creator,
        goal=goal_cc_creator,
        backstory=backstory_cc_creator,
        tools=[google_tool , ScrapeWebsiteTool()],
        allow_delegation=False,
        memory=True,
        verbose=True,
    )

    # chief_creative_director:
    role_cc_director = dedent("""
        Chief Creative Director """)
    goal_cc_director = dedent("""
        Oversee the work done by your team to make sure it is the best possible and
        aligned with the product goals, review, approve, ask clarifying questions or
        delegate follow-up work if necessary.""")
    backstory_cc_director = dedent("""
        You are the Chief Content Officer at a leading digital marketing agency
        specializing in product branding. You ensure your team crafts the best
        possible content for the customer.""")
    chief_creative_director = Agent(
        llm=llm,
        role=role_cc_director,
        goal=goal_cc_director,
        tools=[ google_tool , ScrapeWebsiteTool()],
        allow_delegation=False,
        memory=True,
        verbose=True,
        backstory=backstory_cc_director)
    #research_task:
    description_re = dedent(f"""
        Conduct a thorough research about the customer and competitors in the context
        of {customer_domain}.
        Make sure you find any interesting and relevant information given the
        current year is {year}.
        We are working with them on the following project: {project_description}.""")
    expected_output_re = dedent("""
        A complete report on the customer and their customers and competitors,
        including their demographics, preferences, market positioning and audience engagement.""")
    output_file_re=f'{customer_domain}_research.md'
    research_task = Task(
        description=description_re,
        expected_output=expected_output_re,
        agent=lead_market_analyst,
        async_execution=False,
        output_file=output_file_re)
    # project_understanding_task:
    description_project = dedent("""
        Understand the project details and the target audience for
        {project_description}.
        Review any provided materials and gather additional information as needed.""")
    expected_output_project = dedent("""
        A detailed summary of the project and a profile of the target audience.""")

    project_understanding_task = Task(
        description=description_project,
        expected_output=expected_output_project,
        agent=chief_marketing_strategist,
        async_execution=False,
        output_file='project_understanding.md')

    # marketing_strategy_task:
    description_m_strategy = dedent("""
        Formulate a comprehensive marketing strategy for the project
        {project_description} of the customer {customer_domain}.
        Use the insights from the research task and the project understanding
        task to create a high-quality strategy.""")
    expected_output_m_strategy = dedent("""
        A detailed marketing strategy document that outlines the goals, target
        audience, key messages, and proposed tactics, make sure to have name, tatics, channels and KPIs""")
    output_file_st = f'{customer_domain}_strategy.md'
    marketing_strategy_task = Task(
        description=description_m_strategy,
        expected_output=expected_output_m_strategy,
        agent=chief_marketing_strategist,
        async_execution=False,
        output_file=output_file_st)

    # campaign_idea_task:
    description_campaign_idea = dedent("""
        Develop creative marketing campaign ideas for {project_description}.
        Ensure the ideas are innovative, engaging, and aligned with the overall marketing strategy.""")
    expected_output_campaign_idea = dedent("""
        A list of 5 campaign ideas, each with a brief description and expected impact.""")
    output_file_cp = f'{customer_domain}_campaing.md'
    campaign_idea_task = Task(
        description=description_campaign_idea,
        expected_output=expected_output_campaign_idea,
        agent=chief_creative_director,
        async_execution=False,
        output_file=output_file_cp)

    # copy_creation_task:
    description_copy = dedent("""
        Create marketing copies based on the approved campaign ideas for {project_description}.
        Ensure the copies are compelling, clear, and tailored to the target audience.""")
    expected_output_copy = dedent("""
        A list of 5 marketing copy ideas, each with a brief description and expected impact.
        Marketing copies for each campaign idea.""")
    output_file_copy = f'{customer_domain}_copy.md'
    copy_creation_task = Task(
        description=description_copy,
        expected_output=expected_output_copy,
        agent=creative_content_creator,
        async_execution=False,
        context=[marketing_strategy_task, campaign_idea_task],
        output_file=output_file_copy)

    inputs = {
        'customer_domain': customer_domain,
        'project_description': project_description}
    crew = Crew(
    agents=[lead_market_analyst,chief_marketing_strategist,creative_content_creator,chief_creative_director],
    tasks=[research_task,project_understanding_task,marketing_strategy_task,campaign_idea_task,copy_creation_task],
    process=Process.sequential,
    memory=True,
    cache=True,
    verbose=True,
    max_rpm=50 ,
    share_crew=True
    )
    result = crew.kickoff(inputs=inputs)
    return result



