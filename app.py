import streamlit as st
from streamlit.runtime.caching import cache_data

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

# # Initialize st.session_state.role to None
# if "role" not in st.session_state:
#     st.session_state.role = None
#
# # Retrieve the role from Session State to initialize the widget
# st.session_state._role = st.session_state.role
#
# def set_role():
#     # Callback function to save the role selection to Session State
#     st.session_state.role = st.session_state._role
#
#
# # Selectbox to choose role
# st.selectbox(
#     "Select your role:",
#     [None, "user", "admin", "super-admin"],
#     key="_role",
#     on_change=set_role,
# )
import streamlit_authenticator as stauth

import yaml
from yaml.loader import SafeLoader
with open('./config/config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)
hashed_passwords = stauth.Hasher.hash_passwords(config['credentials'])

#print(hashed_passwords)
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']

)
authenticator.login()
if st.session_state['authentication_status']:
    authenticator.logout()
elif st.session_state['authentication_status'] is False:
    st.error('Username/password is incorrect')
elif st.session_state['authentication_status'] is None:
    st.warning('Please enter your username and password')

def germinApiKey():
    if  st.session_state['authentication_status']:
        if "germin_api_key" not in st.session_state:
          st.session_state['germin_api_key']= config['keys']['GOOGLE_API_KEY']       #os.environ.get('GOOGLE_API_KEY')
    else:
        "[Get GOOGLE API KEY](https://ai.google.dev/)"
        st.warning('Please enter your Google Germin API Key')
        openai_api_key = st.text_input(
            "GOOGLE API KEY", key="openai_key", type="password")
        if openai_api_key and "germin_api_key" not in st.session_state:
            st.session_state['germin_api_key'] = openai_api_key
        if not st.session_state['germin_api_key']:
            st.info("Please add your OpenAI API key to continue.")
            st.stop()
    return  st.session_state['germin_api_key']
def SerpApiKey():
    if  st.session_state['authentication_status']:
        if "serp_api_key" not in st.session_state:
          st.session_state['serp_api_key']= config['keys']['SERPER_API_KEY']          #os.environ.get('SERPER_API_KEY')
    else:
        "[Get SERPER API KEY](https://serper.dev/)"
        st.warning('Please enter your Serper API Key')
        serper_api_key = st.text_input(
            "SERPER API KEY", key="search_serper_api_key", type="password")
        if   serper_api_key and "serp_api_key" not in st.session_state:
            st.session_state['serp_api_key'] = serper_api_key
    return  st.session_state['serp_api_key']


try:
    g=germinApiKey()
    if st.session_state['germin_api_key']:
        menu()
        #st.title(" 🔎 Google-Germin")
        st.title("💬 Chatbot With   Google-Germin")
        client = OpenAI(
            api_key=st.session_state['germin_api_key'],
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/")


        if "messages" not in st.session_state:
            st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

        for msg in st.session_state.messages:
            st.chat_message(msg["role"]).write(msg["content"])

        if prompt := st.chat_input():
            if not st.session_state['germin_api_key']:
                st.info("Please add your Germin  API key to continue.")
                st.stop()

            st.session_state.messages.append({"role": "user", "content": prompt})
            #st.chat_message("user").write(prompt)
            #response = client.chat.completions.create(model="gpt-3.5-turbo", messages=st.session_state.messages)
            # msg = response.choices[0].message.content
            # st.session_state.messages.append({"role": "assistant", "content": msg})
            # st.chat_message("assistant").write(msg)



            # Display user message in chat message container
            with st.chat_message("user"):
                    st.markdown(prompt)
            with st.chat_message("assistant"):
             response = client.chat.completions.create(
                model="gemini-1.5-flash",
                n=1,
                messages=st.session_state.messages
                # [{"role": "system", "content": "You are a helpful assistant."},
                #     { "role": "user",
                #     "content": prompt }],
               # stream=True

            )
            msg = response.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": msg})
            st.chat_message("assistant").write(msg)
            # for chunk in response:
            #     #print(chunk.choices[0].delta)
            #
            #     st.markdown((chunk.choices[0].delta.content))
except Exception as error:
   print(error)
