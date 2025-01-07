import streamlit as st

import streamlit as st

# if "logged_in" not in st.session_state:
#     st.session_state.logged_in = False
#
# def login():
#     if st.button("Log in"):
#         st.session_state.logged_in = True
#         st.rerun()
#
# def logout():
#     if st.button("Log out"):
#         st.session_state.logged_in = False
#         st.rerun()
#
# login_page = st.Page(login, title="Log in", icon=":material/login:")
# logout_page = st.Page(logout, title="Log out", icon=":material/logout:")
#
# dashboard = st.Page(
#     "reports/stockmarket.py", title="Stock Market Analyse", icon=":material/dashboard:", default=True
# )
# jobposting = st.Page("reports/Marketing.py", title="Job Postings", icon=":material/bug_report:")
# alerts = st.Page(
#     "reports/alerts.py", title="System alerts", icon=":material/notification_important:"
# )
#
# search = st.Page("tools/gemini.py", title="Google Gemini", icon=":material/search:")
# #history = st.Page("tools/history.py", title="History", icon=":material/history:")
#
# if st.session_state.logged_in:
#     pg = st.navigation(
#         {
#             "Account": [logout_page],
#             "Reports": [dashboard, jobposting, alerts],
#             "Tools": [search],
#         }
#     )
# else:
#     pg = st.navigation([login_page])
#
# pg.run()


def authenticated_menu():
    # Show a navigation menu for authenticated users
    st.sidebar.page_link("app.py", label="Gemini  Chatbot", icon='🏠')
    st.sidebar.page_link("pages/queryfiles.py", label="Upload files")
    st.sidebar.page_link("pages/search.py", label="AI  search")
    st.sidebar.page_link("pages/Marketing.py", label="Marketing Compaign")
    st.sidebar.page_link("pages/Stockmarket.py", label="Stockmarket Analyse")
    # if st.session_state.role in ["admin", "super-admin"]:
    #     st.sidebar.page_link("pages/admin.py", label="Manage users")
    #     st.sidebar.page_link(
    #         "pages/search.py",
    #         label="Manage admin access",
    #         disabled=st.session_state.role != "super-admin",
    #     )


def unauthenticated_menu():
    # Show a navigation menu for unauthenticated users
    st.sidebar.page_link("app.py", label="Log in")


def menu():

    authenticated_menu()


def menu_with_redirect():

    st.switch_page("app.py")
    menu()