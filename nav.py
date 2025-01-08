

import streamlit as st

import streamlit as st
import sys
pages = {
    "Gemini AI": [
        st.Page("./main.py", title="Gemini  Chatbot"),
        st.Page("./pages/queryfiles.py", title="Upload Files"),
        st.Page("./pages/search.py", title="AI  search"),
    ],
    "Stockmarket": [
        st.Page("./pages/stockmarket.py", title="Stockmarket Analyse"),

    ],
}

pg = st.navigation(pages)
pg.run()

# def authenticated_menu():
#     # Show a navigation menu for authenticated users
#     st.sidebar.page_link("main.py", label="Gemini  Chatbot", icon='🏠')
#     st.sidebar.page_link("pages/queryfiles.py", label="Upload files")
#     st.sidebar.page_link("pages/search.py", label="AI  search")
#     st.sidebar.page_link("pages/Stockmarket.py", label="Stockmarket Analyse")
#
# def menu():
#
#     authenticated_menu()


def menu_with_redirect():

    st.switch_page("main.py")
