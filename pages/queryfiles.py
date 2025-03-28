import streamlit as st

from langchain_google_genai import ChatGoogleGenerativeAI
import os
from tools.utils import CrewAiMatcher
import pandas as  pd
import google.generativeai as geneai
import os
from langchain_community.document_loaders import (PyPDFLoader)


# Initialize the tool allowing for any PDF content search if the path is provided during execution
tab1, tab2,tab3 = st.tabs(["Upload local files","Upload Cv", "Match CV to Job"])

def germinApiKey():
    st.warning('Please enter your Google Gemini API Key')
    "[Get GOOGLE API KEY](https://ai.google.dev/)"
    openai_api_key = st.text_input(
        "GOOGLE API KEY", key="gemini_api_key", type="password")
    if  "gemini_api_key" not in st.session_state:
        st.session_state['gemini_api_key'] = openai_api_key
        st.info("Please add your OpenAI API key to continue.")
        st.stop()
    return  st.session_state['gemini_api_key']
def SerpApiKey():
    st.warning('Please enter your Serper API Key')
    "[Get SERPER API KEY](https://serper.dev/)"
    serper_api_key = st.text_input(
        "SERPER API KEY", key="serp_api_key", type="password")
    if  "serp_api_key" not in st.session_state:
        st.session_state['serp_api_key'] = serper_api_key
    return  st.session_state['serp_api_key']
@st.cache_resource
def RAGQuery(prompt,germin_key,model):
    try:
        llm = ChatGoogleGenerativeAI(model=model, api_key=germin_key)
        answer = llm.invoke(prompt)
        return answer.content
    except Exception as error:
        st.error(error)
@st.cache_resource
def CVSummary(messages,model,germin_key):
    try:
        llm = ChatGoogleGenerativeAI(model=model, api_key=germin_key)
        answer = llm.invoke(messages)
        return answer.content
    except Exception as error:
        st.error(error)


germin_key=germinApiKey()
serp_api= SerpApiKey()
if germin_key:
    geneai.configure(api_key= germin_key)
    os.environ['GOOGLE_API_KEY'] = germin_key
    choice = []
    flash_vision = []
    #"gemini/gemini-1.5-pro"
    for m in geneai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            # st.write(m.name)
            model_name = m.name.split("/")[1]
            if "2.0" in str(model_name).lower() or "-exp" in model_name or "1.5-pro" in  model_name:
                flash_vision.append(f'gemini/{model_name}')
                choice.append(model_name)
    llm = ChatGoogleGenerativeAI(model="gemini-pro", api_key=germin_key)
    @st.cache_resource
    def getCrewAIMatcher(profession, location,file,ispdf,model="gemini/gemini-1.5-pro"):
        try:
            date=pd.to_datetime('today').date()
            yr = pd.to_datetime('today').year
            results=CrewAiMatcher(germin_key, serp_api, profession, yr, date,file,location,ispdf,model)
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
            modelfile = st.radio(
                "Choose a Model",
                choice,
                key='modelfile')
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
            #llm = ChatGoogleGenerativeAI(model="gemini-pro", api_key=germin_key)
            #answer=llm.invoke(prompt)
            st.write("### Answer")
            if  question:
                st.write("### Answer")
                st.markdown(RAGQuery( prompt,germin_key,modelfile))
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

            modelfile1 = st.radio(
                "Choose a Model",
                choice,
                key='modelfile1')
            if st.button("Process CV",key='cv_key'):
                st.write("### Answer")
                answer =CVSummary(messages,modelfile1,germin_key)
                st.markdown(answer)
                os.remove(f'temp_dir/{uploaded_cv.name}')
    with tab3:
            if uploaded_cv:
                container = st.container(border=True)
                model1= container.radio(
                        "Choose a Model",
                            flash_vision,
                       key='model1')
                profession = container.text_input(
                    "### Give your Profession",
                    placeholder="Give your Profession e.g Java developer",
                    disabled=not uploaded_cv)
                location = container.text_input(
                    "### Give your Preferred Job Location",
                    placeholder="Give your Job Location eg. Frankfurt",
                    disabled=not uploaded_cv)
                file = f'temp_dir/{uploaded_cv.name}'
                try:
                    if st.button("Submit",key="match"):
                        st.markdown(getCrewAIMatcher(profession, location,answer, ispdf,model1))
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


