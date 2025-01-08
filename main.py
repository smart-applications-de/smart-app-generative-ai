import streamlit as st


#from nav import menu

from dotenv import  load_dotenv

from openai import OpenAI

def germinApiKey():
    st.warning('Please enter your Google Germin API Key')
    openai_api_key = st.text_input(
        "GOOGLE API KEY", key="germin_api_key", type="password")
    if  "germin_api_key" not in st.session_state:
        "[Get GOOGLE API KEY](https://ai.google.dev/)"
        st.session_state['germin_api_key'] = openai_api_key
        st.info("Please add your OpenAI API key to continue.")
        st.stop()
    return  st.session_state['germin_api_key']

def SerpApiKey():
    st.warning('Please enter your Serper API Key')
    serper_api_key = st.text_input(
        "SERPER API KEY", key="serp_api_key", type="password")
    if  "serp_api_key" not in st.session_state:
        "[Get SERPER API KEY](https://serper.dev/)"
        st.session_state['serp_api_key'] = serper_api_key
    return  st.session_state['serp_api_key']


germinApiKey()
try:
        if st.session_state['germin_api_key']:
            st.title("💬 Chatbot With   Google-Gemini")
            client = OpenAI(
                api_key=st.session_state['germin_api_key'],
                #st.session_state['germin_api_key'],
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
