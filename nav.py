
# __import__('pysqlite3')
# import sys
# sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
# import streamlit as st

import streamlit as st
import sys
pages = {
    "Gemini AI": [
        st.Page("./main.py", title="Gemini  Chatbot"),
        st.Page("./pages/queryfiles.py", title="Upload Files"),
        st.Page("./pages/search.py", title="AI  search"),
    ],
    "Stockmarket": [
        st.Page("./pages/stockmarket.py", title="Stockmarket Analysis"),

    ],
}

pg = st.navigation(pages)
pg.run()






