import streamlit as st
from instructor.cli.usage import api_key
from menu import menu_with_redirect
import time
from langchain.agents import AgentType, Tool, initialize_agent
from langchain_community.utilities import GoogleSerperAPIWrapper
from openai import OpenAI
from langchain_core.messages import HumanMessage
from langchain.prompts import PromptTemplate
from app import germinApiKey, SerpApiKey
germin_key =  germinApiKey()
serp_api = SerpApiKey()

import os
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from tools.utils import CrewAiMatcher
import pandas as  pd
#CrewAiMatcher(germin_api, serp_api, profession, year, date,cv_path,location,ispdf=False):
from crewai_tools import PDFSearchTool
from langchain_community.document_loaders import (PyPDFLoader,PDFPlumberLoader,
                                                  UnstructuredPDFLoader,
                                                  UnstructuredPowerPointLoader,
                                                  UnstructuredFileLoader)


# Initialize the tool allowing for any PDF content search if the path is provided during execution
tab1, tab2,tab3 = st.tabs(["Upload local files","Upload Cv", "Match CV to Job"])
llm = ChatGoogleGenerativeAI(model="gemini-pro", api_key=germin_key)
@st.cache_resource
def getCrewAIMatcher(profession, location,file,ispdf):
    try:
        date=pd.to_datetime('today').date()
        yr = pd.to_datetime('today').year
        results=CrewAiMatcher(germin_key, serp_api, profession, yr, date,file,location,ispdf)
        return results
    except Exception as error:
        return  error
with tab1:
    st.write("Upload a local file and get a summary. You can translate it to any language")
    uploaded_file = st.file_uploader("Upload an article", type=("txt", "md", "pdf"))
    if uploaded_file:
        st.info(uploaded_file.name)
        question = st.text_input(
            "### Ask something about the uploaded file",
            placeholder="Can you give me a short summary in German?",
            disabled=not uploaded_file,
        )
    from io import StringIO
    if uploaded_file and question and germin_key:
        if uploaded_file.type == 'application/pdf':
            #os.mkdir("temp_dir")
            if  not os.path.isdir("temp_dir"):
                os.mkdir("temp_dir")
            path = os.path.join("temp_dir", uploaded_file.name)
            with open(path, "wb") as f:
                f.write(uploaded_file.getvalue())
            loader = PyPDFLoader(f'temp_dir/{uploaded_file.name}')
            pages = loader.load_and_split()
            article= " ".join([doc.page_content  for doc in pages])
        else:
           article = uploaded_file.read().decode()
        prompt = f""" Here's an article:\n\n
        {article}\n\n\n\n{question}"""
        llm = ChatGoogleGenerativeAI(model="gemini-pro", api_key=germin_key)
        answer=llm.invoke(prompt)
        st.write("### Answer")
        st.markdown(answer.content)
with tab2:
    st.write("### Upload your cv as pdf or md")
    uploaded_cv = st.file_uploader("Upload a cv", type=("txt", "md", "pdf"))
    if  uploaded_cv:
        st.info(uploaded_cv.name)
        if uploaded_cv.type == 'application/pdf':
            #os.mkdir("temp_dir")
            if  not os.path.isdir("temp_dir"):
                os.mkdir("temp_dir")
            path = os.path.join("temp_dir", uploaded_cv.name)
            with open(path, "wb") as f:
                f.write(uploaded_cv.getvalue())
            loader = PyPDFLoader(f'temp_dir/{uploaded_cv.name}')
            pages = loader.load_and_split()
            cv= " ".join([doc.page_content  for doc in pages])
            ispdf=True
        else:
           cv = uploaded_cv.read().decode()
           ispdf=False

        question1 = st.text_input(
        "### Ask something about the uploaded file",
        placeholder=" Extract a summary of the cv including Job Skills,profession, language, education, key achievements and years of experience",
        disabled=not uploaded_cv)

        messages= f"""
            You are a helpful assistant that with decades of Experience in Extracting  Job Skills,profession, language, education, key achievements and years of experience . 
            Here is the cv {cv}.{question1}
            The output MUST Be Formatted in markdown without ```"""
        ChatGoogleGenerativeAI(model="gemini-pro", api_key=germin_key)
        answer = llm.invoke(messages)
        st.write("### Answer")
        st.markdown(answer.content)
with tab3:
        if uploaded_cv:
            profession = st.text_input(
                "### Give your Profession",
                placeholder="Give your Profession e.g Java developer",
                disabled=not uploaded_cv)
            location = st.text_input(
                "### Give your Preferred Job Location",
                placeholder="Give your Job Location eg. Frankfurt",
                disabled=not uploaded_cv)
            file = f'temp_dir/{uploaded_cv.name}'
            try:
                if profession and location:
                    st.markdown(getCrewAIMatcher(profession, location,answer.content, ispdf))
                    try:
                        st.subheader("Top 5 Job Postings")
                        file_adv = f'./Crew_AI/Reports/{profession}_posting.md'
                        with open(file_adv, 'r') as f:
                            advisor_expert = (f.read())
                            f.close()
                        st.markdown(advisor_expert)
                    except Exception as error:
                        st.error(error)

            except Exception as error:
                st.error(error)


