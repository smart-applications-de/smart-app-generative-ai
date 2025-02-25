import streamlit as st


#from nav import menu

from dotenv import  load_dotenv

from openai import OpenAI
import markdown2
from docx import Document
from fpdf import FPDF
import io
from bs4 import BeautifulSoup
import re
import datetime
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
    serper_api_key = st.text_input(
        "SERPER API KEY", key="serp_api_key", type="password")
    if  "serp_api_key" not in st.session_state:
        "[Get SERPER API KEY](https://serper.dev/)"
        st.session_state['serp_api_key'] = serper_api_key
    return  st.session_state['serp_api_key']

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
                #pdf.multi_cell(0, 10, txt=paragraph)  # handle multiple lines in paragraph
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
                        #pdf.set_font("Arial", style="B", size=12)
                        item_cell = (item.strip().replace("</li>", "")).replace("</ul>", "")
                        item_cell = (item_cell.replace("<a href=", "")).replace('"', '')
                        item_cell = item_cell.replace("</a>", "")
                        pdf.set_font("Arial", style="B", size=10)
                        pdf.cell(10, 10, txt=". " + item_cell.split(">")[0], ln=1)
                        pdf.set_font("Arial", size=12)

            else:
                text =(line.strip()).replace("</ul>","")
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
        #doc.add_paragraph(clean_html(html_content))

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
                #pdf.multi_cell(0, 10, txt=paragraph)  # handle multiple lines in paragraph
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
                        #pdf.set_font("Arial", style="B", size=12)
                        item_cell = (item.strip().replace("</li>", "")).replace("</ul>", "")
                        item_cell = (item_cell.replace("<a href=", "")).replace('"', '')
                        item_cell = item_cell.replace("</a>", "")
                        main_list.add_run(f". { item_cell}\n")


            else:
                text =(line.strip()).replace("</ul>","")
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


germinApiKey()
try:
        if st.session_state['germin_api_key']:
            st.title("💬 Chatbot With   Google-Gemini")
            container1 =st.container(border=True)
            model1= container1.radio(
                "Choose a Model",
                ["gemini-1.5-pro", "gemini-1.5-flash-8b", "gemini-1.5-flash",
                 "gemini-2.0-flash-exp", "gemini-exp-1206", "gemini-2.0-flash-thinking-exp-01-21"],
                key='model1'
            )
            client = OpenAI(
                api_key=st.session_state['germin_api_key'],
                #st.session_state['germin_api_key'],
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/")


            if "messages" not in st.session_state:
                st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

            download_text =[]

            for msg in st.session_state.messages:
                st.chat_message(msg["role"]).write(msg["content"])
                download_text.append(msg["content"])





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
                    model=model1,
                    #"gemini-1.5-flash",
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
            if len(download_text) > 0:
                text= " ".join([w for w in download_text])
                st.subheader("Download Chat History")
                html_output = convert_markdown_to_html(text)
                download_format1 = st.radio("Download as:", ("TXT", "PDF", "HTML", "MD", "DOCX","PPTX"), key='download1')

                if download_format1:

                        now = datetime.datetime.now()
                        if download_format1 == "TXT":
                            formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
                            st.download_button(
                                label="Download TXT",
                                data=text.encode("utf-8"),  # Encode to bytes for download
                                file_name=f"{formatted_time}_gemini_chatbot.txt",
                                mime="text/plain",
                            )
                        elif download_format1 == "PDF":
                            formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
                            st.download_button(
                                label="Download PDF",
                                data=convert_markdown_to_pdf(text.encode("utf-8")),
                                # Encode to bytes for download
                                file_name=f"{formatted_time}_gemini_chatbot.pdf",
                                mime="application/pdf",
                            )
                        elif download_format1 == "MD":
                            formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
                            st.download_button(
                                label="Download Markdown",
                                data=text.encode("utf-8"),  # Encode to bytes for download
                                file_name=f"{formatted_time}_gemini_chatbot.md",
                                mime="text/plain",
                            )
                            # convert_markdown_to_pptx
                        # Customize format as needed.
                        elif download_format1 == "HTML":
                            formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
                            st.download_button(
                                label="Download HTML",
                                data=html_output.encode("utf-8"),  # Encode to bytes for ownload
                                file_name=f"{formatted_time}_gemini_chatbot.html",
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
                                    file_name=f"{formatted_time}_gemini_chatbot.docx",
                                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                )
                        elif download_format1 == "PPTX":
                            formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
                            pptx_bytes = convert_markdown_to_pptx(html_output)
                            st.download_button(
                                label="Download PPTX",
                                data=pptx_bytes,
                                file_name=f"{formatted_time}_gemini_chatbot.pptx",
                                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation")


        # for chunk in response:
            #     #print(chunk.choices[0].delta)
            #
            #     st.markdown((chunk.choices[0].delta.content))
except Exception as error:
   print(error)
