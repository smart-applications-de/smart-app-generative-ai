

import streamlit as st



def authenticated_menu():
    # Show a navigation menu for authenticated users
    st.sidebar.page_link("main.py", label="Gemini  Chatbot", icon='🏠')
    st.sidebar.page_link("pages/queryfiles.py", label="Upload files")
    st.sidebar.page_link("pages/search.py", label="AI  search")
    st.sidebar.page_link("pages/Stockmarket.py", label="Stockmarket Analyse")

def menu():

    authenticated_menu()


def menu_with_redirect():

    st.switch_page("main.py")
