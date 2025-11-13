#This pysqlite3 workaround is necessary for ChromaDB on Streamlit Sharing
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import streamlit as st

# Set a default page config for the navigation app
st.set_page_config(
    page_title="AI Analysis Dashboard",
    page_icon="🤖",
    layout="wide"
)

st.title("AI Analysis Dashboard")

# Define the app structure with standardized paths and icons
pages = {
    "Gemini AI": [
        # This path is updated. You must move 'main.py' to 'pages/gemini_chatbot.py'
        st.Page("./main.py", title="Gemini Chatbot", icon="💬"),
        st.Page("./pages/queryfiles.py", title="Upload & Query Files", icon="🗂️"),
        st.Page("./pages/search.py", title="AI Web Search", icon="🔎"),
        # st.Page("./pages/youtube.py", title="YouTube Video Analysis"),
    ],
    "Stockmarket": [
        # This path assumes 'stockmarket.py' is inside the 'pages' folder
        st.Page("./pages/stockmarket.py", title="Stockmarket Analysis", icon="📈"),
    ],
}

# Create and run the navigation
pg = st.navigation(pages)
pg.run()
