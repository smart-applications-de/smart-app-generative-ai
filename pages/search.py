import streamlit as st
from instructor.cli.usage import api_key
from joblib.externals.loky.backend.resource_tracker import VERBOSE
from menu import menu_with_redirect
import time
from crewai import Agent, LLM
from langchain_openai import ChatOpenAI
from langchain.agents import AgentType, Tool, initialize_agent
from langchain_community.utilities import GoogleSerperAPIWrapper
from mpmath.calculus.extrapolation import limit
from openai import OpenAI
from langchain_core.messages import HumanMessage
from langchain.prompts import PromptTemplate
from app import germinApiKey, SerpApiKey
germin_key =  germinApiKey()
SERPAPI_API_KEY =SerpApiKey()
from langchain_google_genai import ChatGoogleGenerativeAI
#
from langchain_core.prompts import ChatPromptTemplate
#from langchain.callbacks import StreamlitCallbackHandler
# Verify the user's role
import os
import pandas as pd

date = pd.to_datetime('today').date()
yr = pd.to_datetime('today').year
tab1, tab2,tab3 = st.tabs(["Google Search","News Article", "Google Image Search"])
if not germin_key and not SERPAPI_API_KEY:
    st.info("Please add your Gemin  API key to continue.")
    st.stop()
llm= ChatGoogleGenerativeAI(model="gemini-1.5-pro", api_key=germin_key,temperature=0,
                            max_tokens=None,
                            timeout=None,
                            max_retries=2,
                            )
#                            streaming=True
   #                         )





if "searches" not in st.session_state:
    st.session_state["searches"] = [
        {"role": "assistant", "content": "Hi, I'm a chatbot who can search the web. How can I help you?"}
    ]
with tab1:
    search = GoogleSerperAPIWrapper(api_key=SERPAPI_API_KEY,
                                    num=4,
                                 #   gl="de"
                                    )
    tools = [
        Tool(
            name="Search",
            func=search.run,
            description="useful for when you need to ask with search. ",
        )
    ]

    #langauge= st.radio(label="select output language",options=['German', 'English', 'French','Spanish', 'Italian'])
    search_agent = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, handle_parsing_errors=True, verbose=True)
    if query :=st.text_input(key='query',placeholder="Who won World cup in 2022 ?",label="Ask Anything"):

        messages = [
            (
                "system",
                f"""You are a helpful assistant that with decades of experience on Google Search. 
                 You takes the user query and search on internet and returns the top results.
                 You MUST  Also Include  source-information links for further reading.
                 Formatted in markdown without . The Current year is {yr} and current date is {date} ```""",
            ),
            ("human", query),
        ]
        response = search_agent.run(messages )

        st.session_state.searches.append({"role": "user", "content": query})
        st.markdown(response)
with tab2:
    news = GoogleSerperAPIWrapper(api_key=SERPAPI_API_KEY,
                                    num=4,
                                    gl="de",
                                  type="news"
                                    )
    tools_news = [
        Tool(
            name="news",
            func=news.run,
            description="useful for when you need to  search for latest news. ",
        )
    ]

    #langauge_news = st.radio(label="select output language", options=['German', 'English', 'French', 'Spanish', 'Italian'], key='l_news')
    news_agent = initialize_agent(tools_news, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, handle_parsing_errors=True,
                                    verbose=True)
    if news_topic := st.text_input(key='news_topic', placeholder="Randstad Deutschland?", label="Give a Topic"):
        messages_news = [
            (
                "system",
                f"""You are a news Report Expert and you have decades of experience. 
                 You takes the user input on a given topic and search on internet for the latest news. 
                 You MUST write an article with the most important  and latest news.  The current date is:{date} and current year:{yr} .You MUST  Also Include  source urls for further reading.
                 Formatted in markdown without ```""",
            ),
            ("human", news_topic),
        ]
        response =news_agent.run(messages_news)
        st.markdown(response)

# for msg in st.session_state.searches:
#     st.chat_message(msg["role"]).write(msg["content"])



from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI



message = HumanMessage(
    content=[
        {
            "type": "text",
            "text": "What's in this image?",
        },  # You can optionally provide text parts
        {"type": "image_url", "image_url": "https://picsum.photos/seed/picsum/200/300"},
    ]
)



