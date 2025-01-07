import streamlit as st
from menu import menu

from dotenv import  load_dotenv
load_dotenv()
import os
os.environ["OPENAI_API_KEY"] = os.environ.get('GOOGLE_API_KEY')
from dotenv import  load_dotenv
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.environ.get('GOOGLE_API_KEY')
os.environ["LINKEDIN_COOKIE"]=os.environ.get('LI_AT')
os.environ["SERPER_API_KEY"]=os.environ.get('SERPER_API_KEY')

from openai import OpenAI



with st.sidebar:
    openai_api_key = st.text_input(
        "GOOGLE API KEY", key="langchain_search_api_key_openai", type="password")
    "[Get GOOGLE API KEY](https://ai.google.dev/)"
    Google_Search = st.text_input(
        "SERPER API KEY", key="search_serper_api_key", type="password")

    "[Get SERPER API KEY](https://serper.dev/)"

st.title(" 🔎 Google-Germin")
client = OpenAI(
    api_key=os.environ.get('GOOGLE_API_KEY'),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/")



# Accept user input
if prompt := st.chat_input("What is up?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
            st.markdown(prompt)
    with st.chat_message("assistant"):
     response = client.chat.completions.create(
        model="gemini-1.5-flash",
        n=1,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": prompt
            }
        ],
        stream=True

    )
    for chunk in response:
        #print(chunk.choices[0].delta)

        st.markdown((chunk.choices[0].delta.content))