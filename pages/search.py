import streamlit as st

from langchain.agents import AgentType, Tool, initialize_agent
from langchain_community.utilities import GoogleSerperAPIWrapper

from langchain_google_genai import ChatGoogleGenerativeAI

import pandas as pd

date = pd.to_datetime('today').date()
yr = pd.to_datetime('today').year

tab1, tab2,tab3 = st.tabs(["Google Search","News Article", "Google Places"])
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
@st.cache_resource
def SearchAgent(germin_key,SERPAPI_API_KEY,query):
    try:
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", api_key=germin_key, temperature=0.3,
                                     max_tokens=None,
                                     timeout=None,
                                     max_retries=3,
                                     )
        search = GoogleSerperAPIWrapper(api_key=SERPAPI_API_KEY,
                                         # gl="de",
                                        #  hl= "de",
                                          num= 10
                                        )
        tools = [
            Tool(
                name="Search",
                func=search.run,
                description="useful for when you need to ask with search. ",
            )
        ]

        search_agent = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                                        handle_parsing_errors=True, verbose=True)
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
        response = search_agent.run(messages)

        st.session_state.searches.append({"role": "user", "content": query})
        return  response
    except Exception as error:
        st.error(error)
#search = GoogleSerperAPIWrapper(type="places")
#results = search.results("Italian restaurants in Upper East Side")

@st.cache_resource
def SearchNews(germin_key, SERPAPI_API_KEY,topic):
    try:
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", api_key=germin_key, temperature=0.3,
                                     max_tokens=None,
                                     timeout=None,
                                     max_retries=3,
                                     )
        news = GoogleSerperAPIWrapper(api_key=SERPAPI_API_KEY,
                                      #    gl= "de",
                                       #  hl= "de",
                                          num= 20,
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

        messages_news = [
            (
                "system",
                f"""You are a news Report Expert and you have decades of experience. 
                            You takes the user input on a given topic and search on internet for the latest news. 
                            You MUST write an article with the most important  and latest news.  The current date is:{date} and current year:{yr} .You MUST  Also Include  source urls for further reading.
                            Formatted in markdown without ```""",
            ),
            ("human", topic),
        ]
        response = news_agent.run(messages_news)
        return response
    except Exception as error:
        st.error(error)
@st.cache_resource
def SearchPlaces(germin_key, SERPAPI_API_KEY,topic):
    try:
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", api_key=germin_key, temperature=0.3,
                                     max_tokens=None,
                                     timeout=None,
                                     max_retries=2,
                                     )
        places = GoogleSerperAPIWrapper(api_key=SERPAPI_API_KEY,
                                        num=10,
                                      type="places"
                                        )
        tools_news = [
            Tool(
                name="Google Places",
                func=places.run,
                description="useful for when you need to  search for  Google Places. ",
            )
        ]

        #langauge_news = st.radio(label="select output language", options=['German', 'English', 'French', 'Spanish', 'Italian'], key='l_news')
        news_agent = initialize_agent(tools_news, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, handle_parsing_errors=True,
                                        verbose=True)

        messages_news = [
            (
                "system",
                f"""You are  Expert on searching for Google places and locations. 
                            You takes the user input on a given topic and search for places related to the given topic. 
                            You MUST Extract the exact places including the adresses.  The current date is:{date} and current year:{yr}.
                            The Output must be Formatted in markdown without ```""",
            ),
            ("human", topic),
        ]
        response = news_agent.run(messages_news)
        return response
    except Exception as error:
        st.error(error)
germin_key =  germinApiKey()
SERPAPI_API_KEY = SerpApiKey()
if germin_key:
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

        #langauge= st.radio(label="select output language",options=['German', 'English', 'French','Spanish', 'Italian'])
       # search_agent = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, handle_parsing_errors=True, verbose=True)
        if query :=st.text_input(key='query',placeholder="Who won World cup in 2022 ?",label="Ask Anything"):
            response=SearchAgent(germin_key,SERPAPI_API_KEY,query)
            st.markdown(response)
    with tab2:

        #langauge_news = st.radio(label="select output language", options=['German', 'English', 'French', 'Spanish', 'Italian'], key='l_news')
        if news_topic := st.text_input(key='news_topic', placeholder="Randstad Deutschland?", label="Give a Topic"):
            response = SearchNews(germin_key,SERPAPI_API_KEY,news_topic)
            st.markdown(response)
    with tab3:

        #langauge_news = st.radio(label="select output language", options=['German', 'English', 'French', 'Spanish', 'Italian'], key='l_news')
        if place := st.text_input(key='place', placeholder="Italian Restaurant in Darmstadt", label="Give a Place"):
            response = SearchPlaces(germin_key,SERPAPI_API_KEY,place)
            st.markdown(response)

# for msg in st.session_state.searches:
#     st.chat_message(msg["role"]).write(msg["content"])





