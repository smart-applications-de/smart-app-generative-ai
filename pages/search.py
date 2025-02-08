import streamlit as st

from langchain.agents import AgentType, Tool, initialize_agent
from langchain_community.utilities import GoogleSerperAPIWrapper

from langchain_google_genai import ChatGoogleGenerativeAI
import markdown2
from docx import Document
from fpdf import FPDF
import io
from bs4 import BeautifulSoup
import re
import pandas as pd
from tools.utils import   CrewStocknews
date = pd.to_datetime('today').date()
yr = pd.to_datetime('today').year
import datetime
# CrewStocknews(germin_api, serp_api, topic, year, date,model="gemini/gemini-1.5-pro")
tab1, tab2,tab3 = st.tabs(["Agent Google Search"," Agent News Article", "Crew AI News Article"])
def germinApiKey():
    st.warning('Please enter your Google Gemini API Key')
    "[Get GOOGLE API KEY](https://ai.google.dev/)"
    openai_api_key = st.text_input(
        "GOOGLE API KEY", key="germin_api_key", type="password")
    if  "germin_api_key" not in st.session_state:

        st.session_state['germin_api_key'] = openai_api_key
        st.info("Please add your OpenAI API key to continue.")
        st.stop()
    return  st.session_state['germin_api_key']
def SerpApiKey():
    st.warning('Please enter your Serper API Key')
    "[Get SERPER API KEY](https://serper.dev/)"
    serper_api_key = st.text_input(
        "SERPER API KEY", key="serp_api_key", type="password")
    if  "serp_api_key" not in st.session_state:
        st.session_state['serp_api_key'] = serper_api_key
    return  st.session_state['serp_api_key']
@st.cache_resource
def SearchAgent(germin_key,SERPAPI_API_KEY,query,model="gemini-1.5-pro"):
    try:
        llm = ChatGoogleGenerativeAI(model=model, api_key=germin_key, temperature=0.3,
                                     max_tokens=None,
                                     timeout=None,
                                     max_retries=3,
                                     )
        search = GoogleSerperAPIWrapper(api_key=SERPAPI_API_KEY,

                                        # gl="de",
                                        #  hl= "de",
                                          num= 10

                                        )
        tools = [
            Tool(
                name="Search",
                func=search.run,
                description="useful for when you need to ask with search. ",
            )
        ]

        search_agent = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                                        handle_parsing_errors=True, verbose=True)
        messages = [
            (
                "system",
                f"""You are a helpful assistant that with decades of experience on Google Search. 
                 You takes the user query and search on internet and returns the top results.
                 You MUST  Also Include  source-information links for further reading.
                 Formatted in markdown without . The Current year is {yr} and current date is {date} ```""",
            ),
            ("human", query),
        ]
        response = search_agent.run(messages)

        st.session_state.searches.append({"role": "user", "content": query})
        return  response
    except Exception as error:
        st.error(error)
#search = GoogleSerperAPIWrapper(type="places")
#results = search.results("Italian restaurants in Upper East Side")

@st.cache_resource
def SearchNews(germin_key, SERPAPI_API_KEY,topic,model="gemini-1.5-pro"):
    try:

        llm = ChatGoogleGenerativeAI(model=model, api_key=germin_key, temperature=0.3,

                                     max_tokens=None,
                                     timeout=None,
                                     max_retries=3
                                     )
        news = GoogleSerperAPIWrapper(api_key=SERPAPI_API_KEY,

                                      #    gl= "de",
                                       #  hl= "de",
                                          num= 20,
                                         type="news"
                                        )
        tools_news = [
            Tool(
                name="news",
                func=news.run,
                description="useful for when you need to  search for latest news. ",
            )
        ]

        #langauge_news = st.radio(label="select output language", options=['German', 'English', 'French', 'Spanish', 'Italian'], key='l_news')
        news_agent = initialize_agent(tools_news, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, handle_parsing_errors=True,
                                        verbose=True)

        messages_news = [
            (
                "system",
                f"""You are a news Report Expert and you have decades of experience. 
                            You takes the user input on a given topic and search on internet for the latest news. 
                            You MUST write an article with the most important  and latest news.  The current date is:{date} and current year:{yr} .You MUST  Also Include  source urls for further reading.
                            Formatted in markdown without ```""",
            ),
            ("human", topic),
        ]
        response = news_agent.run(messages_news)
        return response
    except Exception as error:
        st.error(error)
@st.cache_resource
def SearchPlaces(germin_key, SERPAPI_API_KEY,topic,model="gemini-1.5-pro"):
    try:
        llm = ChatGoogleGenerativeAI(model=model, api_key=germin_key, temperature=0.3,

                                     max_tokens=None,
                                     timeout=None,
                                     max_retries=3,
                                     )

        places = GoogleSerperAPIWrapper(api_key=SERPAPI_API_KEY,
                                        num=10,
                
                                      type="places"
                                        )
        tools_news = [
            Tool(
                name="Google Places",
                func=places.run,
                description="useful for when you need to  search for  Google Places. ",
            )
        ]

        #langauge_news = st.radio(label="select output language", options=['German', 'English', 'French', 'Spanish', 'Italian'], key='l_news')
        news_agent = initialize_agent(tools_news, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, handle_parsing_errors=True,
                                        verbose=True)

        messages_news = [
            (
                "system",
                f"""You are  Expert on searching for Google places and locations. 
                            You takes the user input on a given topic and search for places related to the given topic. 
                            The current date is:{date} and current year:{yr}.
                            The Output must be Formatted in markdown without ```""",
            ),
            ("human", topic),
        ]
        response = news_agent.run(messages_news)
        return response
    except Exception as error:
        st.error(error)

    def extract_link_and_text(html_tag):
        """Extracts link and text from a simple <a> tag.  NOT ROBUST!"""
        match = re.search(r'<a href="(.*?)">(.*?)</a>', html_tag)
        if match:
            link = match.group(1)
            text = match.group(2)
            return link, text
        else:
            return None, None


# @st.cache_resource

def convert_markdown_to_html(markdown_text):
    """Converts Markdown to HTML."""
    return markdown2.markdown(markdown_text)


def convert_markdown_to_pdf(markdown_text):
    """Converts Markdown text to a PDF using FPDF."""

    html = markdown2.markdown(markdown_text)  # Convert markdown to HTML for better rendering

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)  # Choose a font

    lines = html.splitlines()
    for line in lines:
        if line.strip().startswith("<h1>"):
            title = line.strip()[4:-5]  # Extract title from <h1> tags
            pdf.set_font("Arial", style="B", size=18)  # Bold title
            pdf.cell(0, 10, txt=title, ln=1, align="C")  # Centered title
            pdf.set_font("Arial", size=12)  # Reset font
        elif line.strip().startswith("<h2>"):
            subtitle = line.strip()[4:-5]  # Extract title from <h1> tags
            pdf.set_font("Arial", style="B", size=16)  # Bold title
            pdf.cell(0, 10, txt=subtitle, ln=1, align="C")  # Centered title
            pdf.set_font("Arial", size=12)  # Reset font
        elif line.strip().startswith("<h3>"):
            subtitle = line.strip()[4:-5]  # Extract title from <h1> tags
            pdf.set_font("Arial", style="B", size=14)  # Bold title
            pdf.cell(0, 10, txt=subtitle, ln=1, align="C")  # Centered title
            pdf.set_font("Arial", size=12)
        elif line.strip().startswith("<p>"):
            paragraph = ((line.strip()[3:-4]).replace("<strong>", "")).replace("</strong>", "")
            paragraph = (paragraph.replace("<a href=", "")).replace('"', '')
            paragraph = paragraph.replace("</a>", "")

            # link, link_text = extract_link_and_text(paragraph)
            # if link :
            #     pdf.set_link(link)  # Set the link destination
            #     pdf.write(5, link_text)
            # else:
            pdf.multi_cell(0, 10, txt=paragraph)

            # if paragraph.strip().startswith("<strong>"):
            #     text = line.strip()[8:-9]
            #     pdf.set_font("Arial", style="B", size=12)
            #     pdf.cell(0, 10, txt=text)
            #     pdf.set_font("Arial", size=12)
            #
            # else:
            # pdf.multi_cell(0, 10, txt=paragraph)  # handle multiple lines in paragraph
        # elif line.strip().startswith("<ul>"):
        #
        #     for item in line.strip()[4:-5].split("<li>"):
        #         if item.strip():
        #             pdf.cell(10, 10, txt=". " + item.strip().replace("</li>", ""), ln=1)
        elif line.strip().startswith("<li><strong>"):

            for item in line.strip()[4:-5].split("<li><strong>"):
                item = item.replace("</strong>", "")
                item = item.replace("<strong>", "")
                item = item.replace("</ul>", "")
                if item.strip():
                    # pdf.set_font("Arial", style="B", size=12)
                    item_cell = (item.strip().replace("</li>", "")).replace("</ul>", "")
                    item_cell = (item_cell.replace("<a href=", "")).replace('"', '')
                    item_cell = item_cell.replace("</a>", "")
                    pdf.set_font("Arial", style="B", size=10)
                    pdf.cell(10, 10, txt=". " + item_cell.split(">")[0], ln=1)
                    pdf.set_font("Arial", size=12)

        else:
            text = (line.strip()).replace("</ul>", "")
            text = (text.replace("<ul>", "")).replace("<ol>", "")
            text = (text.replace("</ol>", "")).replace("</p>", "")

            pdf.multi_cell(0, 10, txt=text)

    # You can add more PDF content here if needed

    return pdf.output(dest="S").encode("latin-1")  # Return PDF as bytes


def clean_html(html_content):
    """Removes HTML tags from the given HTML content using BeautifulSoup."""
    soup = BeautifulSoup(html_content, "html.parser")
    text = soup.get_text(" ", strip=True)  # strip=True removes extra whitespace.
    return text


# @st.cache_resource
def convert_html_to_docx(html_content):
    """Converts HTML to DOCX (simplified, may not handle all HTML perfectly)."""
    doc = Document()
    #  A very basic approach -  for more robust conversion, explore dedicated HTML to DOCX libraries.
    # doc.add_paragraph(clean_html(html_content))

    lines = html_content.splitlines()
    for line in lines:

        if line.strip().startswith("<h1>"):
            title = line.strip()[4:-5]  # Extract title from <h1> tags
            doc.add_heading(title)

        elif line.strip().startswith("<h2>"):
            subtitle = line.strip()[4:-5]  # Extract title from <h1> tags
            doc.add_heading(subtitle)
        elif line.strip().startswith("<h3>"):
            subtitle = line.strip()[4:-5]  # Extract title from <h1> tags
            doc.add_section(subtitle)

        elif line.strip().startswith("<p>"):
            paragraph = ((line.strip()[3:-4]).replace("<strong>", "")).replace("</strong>", "")
            paragraph = (paragraph.replace("<a href=", "")).replace('"', '')
            paragraph = paragraph.replace("</a>", "")

            # link, link_text = extract_link_and_text(paragraph)
            # if link :
            #     pdf.set_link(link)  # Set the link destination
            #     pdf.write(5, link_text)
            # else:
            doc.add_paragraph(paragraph)

            # if paragraph.strip().startswith("<strong>"):
            #     text = line.strip()[8:-9]
            #     pdf.set_font("Arial", style="B", size=12)
            #     pdf.cell(0, 10, txt=text)
            #     pdf.set_font("Arial", size=12)
            #
            # else:
            # pdf.multi_cell(0, 10, txt=paragraph)  # handle multiple lines in paragraph
        elif line.strip().startswith("<ul>"):
            main_list = doc.add_paragraph()
            main_list.style = doc.styles['List Paragraph']
            for item in line.strip()[4:-5].split("<li>"):
                if item.strip():
                    main_list.add_run(f". {item}\n")
        #             pdf.cell(10, 10, txt=". " + item.strip().replace("</li>", ""), ln=1)
        elif line.strip().startswith("<li><strong>"):

            for item in line.strip()[4:-5].split("<li><strong>"):
                item = item.replace("</strong>", "")
                item = item.replace("<strong>", "")
                item = item.replace("</ul>", "")
                main_list = doc.add_paragraph()
                main_list.style = doc.styles['List Paragraph']
                if item.strip():
                    # pdf.set_font("Arial", style="B", size=12)
                    item_cell = (item.strip().replace("</li>", "")).replace("</ul>", "")
                    item_cell = (item_cell.replace("<a href=", "")).replace('"', '')
                    item_cell = item_cell.replace("</a>", "")
                    main_list.add_run(f". {item_cell}\n")


        else:
            text = (line.strip()).replace("</ul>", "")
            text = (text.replace("<ul>", "")).replace("<ol>", "")
            text = (text.replace("</ol>", "")).replace("</p>", "")
            doc.add_paragraph(text)

    # You can add more PDF content here if needed

    return doc


def convert_markdown_to_pptx(markdown_text):
    from pptx import Presentation
    from pptx.util import Inches
    import io
    html = markdown2.markdown(markdown_text)  # Convert to HTML first (easier to handle)

    prs = Presentation()
    title_slide_layout = prs.slide_layouts[0]
    slide = prs.slides.add_slide(title_slide_layout)
    title = slide.shapes.title
    subtitle = slide.placeholders[1]

    # Extract Title and Subtitle from HTML (assuming they're in h1 and h2 tags)
    try:
        soup = BeautifulSoup(html, "html.parser")
        title_text = soup.h1.text if soup.h1 else "Untitled Presentation"
        subtitle_text = soup.h2.text if soup.h2 else ""
        title.text = title_text
        subtitle.text = subtitle_text
    except AttributeError:
        title.text = "Untitled Presentation"
        subtitle.text = ""

    # Add content slides (basic paragraphs)
    bullet_slide_layout = prs.slide_layouts[1]
    for paragraph in BeautifulSoup(html, 'html.parser').find_all('p'):
        slide = prs.slides.add_slide(bullet_slide_layout)
        shapes = slide.shapes
        title_shape = shapes.title
        body_shape = shapes.placeholders[1]
        title_shape.text = paragraph.find('strong').text if paragraph.find('strong') else 'Paragraph'
        tf = body_shape.text_frame
        tf.text = paragraph.text

    with io.BytesIO() as buffer:
        prs.save(buffer)
        return buffer.getvalue()


germin_key =  germinApiKey()
SERPAPI_API_KEY = SerpApiKey()

if germin_key:
    llm= ChatGoogleGenerativeAI(model="gemini-1.5-pro", api_key=germin_key,temperature=0,
                            max_tokens=None,
                            timeout=None,
                            max_retries=2,
                            )
#                            streaming=True
   #                         )
    if "searches" not in st.session_state:
        st.session_state["searches"] = [
            {"role": "assistant", "content": "Hi, I'm a chatbot who can search the web. How can I help you?"}
        ]
    with tab1:

        #langauge= st.radio(label="select output language",options=['German', 'English', 'French','Spanish', 'Italian'])
       # search_agent = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, handle_parsing_errors=True, verbose=True)
        if query :=st.text_input(key='query',placeholder="Who won World cup in 2022 ?",label="Ask Anything"):
            container1 =st.container(border=True)
            model1= container1.radio(
                "Choose a Model",
                ["gemini-1.5-pro", "gemini-1.5-flash-8b", "gemini-1.5-flash",
                 "gemini-2.0-flash-exp", "gemini-exp-1206", "gemini-2.0-flash-thinking-exp-01-21"],
                key='model1'
            )
            response=SearchAgent(germin_key,SERPAPI_API_KEY,query,model1)
            st.markdown(response)
    with tab2:

        #langauge_news = st.radio(label="select output language", options=['German', 'English', 'French', 'Spanish', 'Italian'], key='l_news')
        if news_topic := st.text_input(key='news_topic', placeholder="Randstad Deutschland?", label="Give a Topic"):
            container2 =st.container(border=True)
            model2= container2.radio(
                "Choose a Model",
                ["gemini-1.5-pro", "gemini-1.5-flash-8b", "gemini-1.5-flash",
                 "gemini-2.0-flash-exp", "gemini-exp-1206", "gemini-2.0-flash-thinking-exp-01-21"],
                key='model2'
            )
            response = SearchNews(germin_key,SERPAPI_API_KEY,news_topic,model2)
            st.markdown(response)
    with tab3:

        #langauge_news = st.radio(label="select output language", options=['German', 'English', 'French', 'Spanish', 'Italian'], key='l_news')
        if topic := st.text_input(key='topic', placeholder="Germany Elections", label="News topic"):
            container3 = st.container(border=True)
            model3= container3.radio(
                "Choose a Model",
                ["gemini/gemini-1.5-pro", "gemini/gemini-1.5-flash-8b", "gemini/gemini-1.5-flash",
                 "gemini/gemini-2.0-flash-exp", "gemini/gemini-exp-1206", "gemini/gemini-2.0-flash-thinking-exp-01-21"],
                key='model3'

            )
            date=pd.to_datetime('today').date()
            yr = pd.to_datetime('today').year
            try:
                results = CrewStocknews(germin_api=germin_key, serp_api=SERPAPI_API_KEY, topic=topic, year=yr, date=date, model=model3)
                #response = SearchPlaces(germin_key,SERPAPI_API_KEY,place,model3)
                st.markdown(results)
                file_name=f'{model3}_{topic}_editor_task.md'
                with open(file_name, 'r') as f:
                    news_article = (f.read())
                    f.close()
            except Exception as e:
                st.error(e)
            try:
                if news_article:
                        text = news_article
                        st.subheader("Download the News article")
                        html_output = convert_markdown_to_html(text)
                        download_format1 = st.radio("Download as:", ("TXT", "PDF", "HTML", "MD", "DOCX", "PPTX"),
                                                    key='download1')

                        if download_format1:

                            now = datetime.datetime.now()
                            if download_format1 == "TXT":
                                formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
                                st.download_button(
                                    label="Download TXT",
                                    data=text.encode("utf-8"),  # Encode to bytes for download
                                    file_name=f"{formatted_time}_article.txt",
                                    mime="text/plain",
                                )
                            elif download_format1 == "PDF":
                                formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
                                st.download_button(
                                    label="Download PDF",
                                    data=convert_markdown_to_pdf(text.encode("utf-8")),
                                    # Encode to bytes for download
                                    file_name=f"{formatted_time}_article.pdf",
                                    mime="application/pdf",
                                )
                            elif download_format1 == "MD":
                                formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
                                st.download_button(
                                    label="Download Markdown",
                                    data=text.encode("utf-8"),  # Encode to bytes for download
                                    file_name=f"{formatted_time}_article.md",
                                    mime="text/plain",
                                )
                                # convert_markdown_to_pptx
                            # Customize format as needed.
                            #html_output = convert_markdown_to_html(text)
                            elif download_format1 == "HTML":
                                formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
                                st.download_button(
                                    label="Download HTML",
                                    data=html_output.encode("utf-8"),  # Encode to bytes for ownload
                                    file_name=f"{formatted_time}_article.html",
                                    mime="text/html",
                                )
                            elif download_format1 == "DOCX":
                                formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
                                docx_output = convert_html_to_docx(html_output)
                                # Save to in-memory buffer for download
                                with io.BytesIO() as buffer:
                                    docx_output.save(buffer)
                                    st.download_button(
                                        label="Download DOCX",
                                        data=buffer.getvalue(),
                                        file_name=f"{formatted_time}_article.docx",
                                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                    )
                            elif download_format1 == "PPTX":
                                formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
                                pptx_bytes = convert_markdown_to_pptx(html_output)
                                st.download_button(
                                    label="Download PPTX",
                                    data=pptx_bytes,
                                    file_name=f"{formatted_time}_article.pptx",
                                    mime="application/vnd.openxmlformats-officedocument.presentationml.presentation")
            except Exception as e:
                st.error(e)

# for msg in st.session_state.searches:
#     st.chat_message(msg["role"]).write(msg["content"])





