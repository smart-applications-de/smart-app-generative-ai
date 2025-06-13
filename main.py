import os

import streamlit as st

import markdown2
from chromadb.utils.fastapi import fastapi_json_response
from docx import Document
from fpdf import FPDF
import io
from bs4 import BeautifulSoup
import re
import datetime
import google.generativeai as geneai
from google.genai import types
#import google.genai as gen
from langchain_community.document_loaders import (PyPDFLoader)

from pytubefix import YouTube
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

def TakePhoto():
    try:
        kamera = st.camera_input("Take Photo")
        if kamera:
            st.success("Ask Anything about this  Picture and get help from AI")
            #st.image(kamera)
            file_type = kamera.type
            return kamera,  file_type
    except Exception as camerainput:
        st.error(camerainput)

def getAudioStreamTodownload(video):
    try:
        yt = YouTube(video_url)
        audio_stream = yt.streams.filter(only_audio=True).first()
        return audio_stream
    except Exception as audio:
        st.error(audio)
@st.cache_resource
def geminiGetInformationFromPhoto(model,input,data,photo_file):
    try:
        response = client.models.generate_content(
            model=model,
            contents=[input,
                      types.Part.from_bytes(data=data.getvalue(), mime_type=photo_file)])
        return response
    except Exception as model:
        st.error(model)
#@st.cache_resource
def geminiGetTextFromYouTubeVideo(model,input,data):
    try:
        response = client.models.generate_content(
            model=model,
            contents=[input,
                      types.Part.from_bytes(data=data.read(), mime_type="audio/mpeg")])
        return response
    except Exception as model:
        st.error(model)
def getVideoStreamTodownload(video):
    try:
        yt = YouTube(video_url)
        video_stream =  yt.streams.get_highest_resolution()
        return video_stream
    except Exception as vid:
        st.error(vid)

germinApiKey()
try:
        if st.session_state['germin_api_key']:
            st.title("💬 Chatbot With   Google-Gemini")
            container1 =st.container(border=True)
            choice = []
            flash_vision = []
            os.environ['api_key']=st.session_state['germin_api_key']
            geneai.configure(api_key=st.session_state['germin_api_key'])
            from google import genai

            client = genai.Client(api_key=os.environ['api_key'])
            if "messages" not in st.session_state:
                st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?","user":''}]

            download_text = set()

            for msg in st.session_state.messages:
                # st.chat_message(msg["role"]).write(msg["content"])
                if "How can I help you?" not in msg["content"]:
                    download_text.add(msg["content"])
            st.info("You can upload your Images,pdfs, videos files for AI analysis or just asking Anything ")
            col1, col2= container1.columns(2, border=False,gap='medium')
            opt = col1.radio(label="Choose Image or Video  source", options=[None, "camera","youtube"])
            if opt  and opt=="camera":
                photo, photo_file=TakePhoto()
                if photo:
                   pic_text = col1.text_input("Ask anything about the picture",placeholder="Describe this picture")
                   if pic_text:
                       for m in geneai.list_models():
                           if 'generateContent' in m.supported_generation_methods:
                               # st.write(m.name)
                               model_name = m.name.split("/")[1]

                               if "2" in str(model_name).lower() and "flash" in str(model_name).lower():
                                   flash_vision.append(model_name)
                                   choice.append(model_name)
                       #                ["gemini-1.5-pro", "gemini-1.5-flash-8b", "gemini-1.5-flash",
                       #   "gemini-2.0-flash-exp", "gemini-exp-1206", "gemini-2.0-flash-thinking-exp-01-21"],
                       model1 = col2.radio(
                           "Choose a Model",
                           choice,
                           key='model1'
                       )
                       response=geminiGetInformationFromPhoto(model=model1,input=pic_text,data=photo,photo_file=photo_file)



                       if response:
                           # st.markdown(response.text)
                           msg = response.text
                           st.session_state.messages.append({"role": "assistant", "content": msg, "user": pic_text})
                           st.chat_message("assistant").write(msg)
                           download_text.add(pic_text)
                           download_text.add(msg)
            elif opt=="youtube":
                video_url = st.text_input("Enter YouTube Video URL:")
                if  video_url:
                    if video_url not in st.session_state:
                        st.session_state['video_url'] = video_url
                    for m in geneai.list_models():
                        if 'generateContent' in m.supported_generation_methods:
                            # st.write(m.name)
                            model_name = m.name.split("/")[1]

                            if "2.0" in str(model_name).lower() and "flash" in str(model_name).lower():
                                flash_vision.append(model_name)
                                choice.append(model_name)

                    if st.session_state['video_url']:
                        try:
                            yt = YouTube(st.session_state['video_url'])
                            st.warning("choose a model")
                            model1 = col2.radio(
                                "Choose a Model",
                                choice,
                                key='model1'
                            )
                            container = st.container(border=True)
                            # Display video information
                            container.subheader("Video Information")
                            container.write(f"Title: {yt.title}")
                            container.write(f"Author: {yt.author}")
                            container.write(f"Views: {yt.views}")
                            container.write(f"Length: {round(yt.length / 60, 2)} minutes")
                            if yt not in st.session_state:
                                st.session_state['video_id'] = yt.video_id

                            container1 = st.container(border=True)
                            container1.subheader("Display YouTube Video")

                            # Display video
                            container1.video(video_url)

                            # Download video
                            container2 = st.container(border=True)
                            col3, col4 = container2.columns(2, gap="large")
                            col4.markdown("You can download this Audio")



                            try:
                                audio_stream =  yt.streams.filter(only_audio=True).first()
                                
                
                                if audio_stream:
                                    buffer = io.BytesIO()
                                   
                                    audio_stream.stream_to_buffer(buffer)
                                 
                                    buffer.seek(0)

                                    pic_text = col3.text_input("Ask anything about the YouTube Video",
                                                             placeholder="Give a summary in German")

                                    if pic_text and model1:
                                        try:
                                            response=geminiGetTextFromYouTubeVideo(model=model1, input=pic_text, data=buffer)


                                            buffer1 = io.BytesIO()
                                            audio_stream.stream_to_buffer(buffer1)
                                            buffer1.seek(0)
                                            col4.audio(buffer1.read(), format='audio/mpeg')
                                            visible="hidden"

                                            if response:
                                                # st.markdown(response.text)
                                                msg = response.text
                                                st.session_state.messages.append(
                                                    {"role": "assistant", "content": msg, "user": pic_text})
                                                container2.chat_message("assistant").write(msg)
                                                download_text.add(pic_text)
                                                download_text.add(msg)
                                                visible="visible"
                                                container2.warning("Checkout Download Video  if yu want to download the YouTube video")
                                            dv=container2.checkbox(label="Download Video",disabled=not response, label_visibility=visible)
                                            if dv:
                                                now = datetime.datetime.now()
                                                try:
                                                    formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
                                                    video_stream =  yt.streams.get_highest_resolution()
                                                    #getVideoStreamTodownload(st.session_state['video_url'])
                                                    if video_stream:
                                                        buffer3 = io.BytesIO()
                                                        video_stream.stream_to_buffer(buffer3)
                                                        buffer3.seek(0)

                                                        container2.download_button("Download Video", data=buffer3.read(),
                                                                                   file_name=f"video_{formatted_time}.mp4", mime="video/mp4")
                                                except Exception  as vid:
                                                    st.error(vid)
                                        except Exception as modelerror:
                                            st.error(modelerror)
                                        now = datetime.datetime.now()
                                        formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
                                        buffer2 = io.BytesIO()
                                        audio_stream.stream_to_buffer(buffer2)
                                        buffer2.seek(0)

                                        col4.download_button("Download Audio", data= buffer2.read(),
                                                               file_name=f"audio_{formatted_time }.mp3", mime="audio/mpeg")
                            except Exception as videoError:
                                st.error( videoError)
                        except Exception as youtubeeror:
                            st.error(youtubeeror)

            else:
                for m in geneai.list_models():
                    if 'generateContent' in m.supported_generation_methods:
                        # st.write(m.name)
                        model_name = m.name.split("/")[1]

                        if "2.0" in str(model_name).lower() or "-exp" in model_name or "2.5-pro" in str(
                                model_name).lower():
                            flash_vision.append(model_name)
                            choice.append(model_name)

                model1 = col2.radio(
                    "Choose a Model",
                    choice,
                    key='model1'
                )
                container3 = st.container()

                if prompt := container3.chat_input(placeholder="Enter your Prompt or upload a file  and ask questions", key=None, max_chars=3000, accept_file=True):
                    if not st.session_state['germin_api_key']:
                        container3.info("Please add your Germin  API key to continue.")

                        st.stop()


                    if prompt.text and not   prompt["files"]  and  model1:
                        container3.chat_message("user").markdown(prompt.text)
                        response = client.models.generate_content(
                            model=model1,
                            contents=[prompt.text])

                        if response:
                            #st.markdown(response.text)
                            msg = response.text
                            st.session_state.messages.append({"role": "assistant", "content": msg,"user":prompt.text})
                            container3.chat_message("assistant").write(msg)
                            download_text.add(prompt.text)
                            download_text.add(msg)


                    elif   prompt["files"]:
                        st.warning(" Wrtite a prompt to ask anything about the uploaded files")
                        container3.chat_message("user").markdown(prompt.text)
                        file_type=prompt["files"][0].type
                        file_name=prompt["files"][0].name
                        for m in geneai.list_models():
                            if 'generateContent' in m.supported_generation_methods:

                                model_name = m.name.split("/")[1]

                                if "2.0" in str(model_name).lower() and  "flash" in str(model_name).lower() :
                                    flash_vision.append(model_name)
                                    choice.append(model_name)
                        if model1 and file_type:

                            if "audio" in  file_type:
                                try:
                                    audio_data=prompt["files"][0]
                                    st.audio(audio_data)
                                    #  types.Part.from_bytes(data=audio_data.read(),mime_type=file_type)]
                                    response = client.models.generate_content(
                                        model=model1,
                                        contents=[prompt.text, types.Part.from_bytes(data=audio_data.getvalue(),mime_type=file_type)])
                                    if response:
                                        if response:
                                            # st.markdown(response.text)
                                            msg = response.text
                                            st.session_state.messages.append({"role": "assistant", "content": msg,"user":prompt.text})
                                            container3.chat_message("assistant").write(msg)
                                            download_text.add(prompt.text)
                                            download_text.add(msg)
                                except Exception as audio:
                                    st.error("Error Processing Audio: ", audio)

                            elif "video" in file_type:
                                try:
                                    video = prompt["files"][0]
                                    st.video(video)
                                    response = client.models.generate_content(
                                        model=model1,
                                        contents=[prompt.text,  types.Part.from_bytes(data=video.getvalue(),mime_type=file_type)])

                                    if response:
                                        # st.markdown(response.text)
                                        msg = response.text
                                        st.session_state.messages.append({"role": "assistant", "content": msg,"user":prompt.text})
                                        container3.chat_message("assistant").write(msg)
                                        #download_text.add(faq)
                                        download_text.add(msg)
                                except Exception as video:
                                    st.error("Error Processing Video: ",video)

                            elif "image" in file_type:
                                try:
                                    image = prompt["files"][0]
                                    st.image(image)
                                    response = client.models.generate_content(
                                        model=model1,
                                        contents=[prompt.text,  types.Part.from_bytes(data=image.getvalue(),mime_type=file_type)])
                                    if response:
                                        # st.markdown(response.text)
                                        msg = response.text
                                        st.session_state.messages.append({"role": "assistant", "content": msg,"user":prompt.text})
                                        container3.chat_message("assistant").write(msg)
                                        #download_text.add(faq)
                                        download_text.add(msg)
                                except Exception as image:
                                    st.error("Error Processing Image: ", image)

                            elif "pdf" in file_type:
                                    try:
                                        uploaded_file=prompt["files"][0]
                                        if not os.path.isdir("temp_dir"):
                                            os.mkdir("temp_dir")
                                        path = os.path.join("temp_dir", uploaded_file.name)
                                        with open(path, "wb") as f:
                                            f.write(uploaded_file.getvalue())
                                        loader = PyPDFLoader(f'temp_dir/{uploaded_file.name}')
                                        pages = loader.load_and_split()
                                        article = " ".join([doc.page_content for doc in pages])
                                        response = client.models.generate_content(
                                        model=model1,
                                        contents=[prompt.text, article ])
                                        os.remove(path)
                                        if response:
                                            # st.markdown(response.text)
                                            msg = response.text
                                            st.session_state.messages.append({"role": "assistant", "content": msg,"user":prompt.text})
                                            container3.chat_message("assistant").write(msg)
                                            #download_text.add(faq)
                                            download_text.add(msg)
                                    except Exception as pdf:
                                        st.error( "Error processing pdf:",pdf)

                        else:
                            try:
                                uploaded_file = prompt["files"][0]

                                from langchain_google_genai import ChatGoogleGenerativeAI

                                article = uploaded_file.read().decode()
                                qst = f""" Here's an article:\n\n
                                           {article}\n\n\n\n{prompt.text}"""

                                llm = ChatGoogleGenerativeAI(model=model1, api_key=st.session_state['germin_api_key'])
                                response = llm.invoke(qst)
                                if  response:
                                    msg = response.text
                                    st.session_state.messages.append({"role": "assistant", "content": msg, "user":prompt.text})
                                    container3.chat_message("assistant").write(msg)
                                    download_text.add(prompt.text)
                                    download_text.add(msg)
                            except Exception  as error1:
                                st.error(error1)
                    else:
                        st.error("No files  was found")
                else:
                    st.chat_message("assistant").write("How Can I help You ?")
            container4 = st.container()
            col7,col8 = container4.columns(2,gap="large")
            container5 = st.container()

            if  col7.button("clear"):
                download_text =  download_text.clear()
                text = ''

            if len(download_text) > 0:
                    text = " ".join([w for w in download_text])
                    st.subheader("Download Chat History")
                    html_output = convert_markdown_to_html(text)
                    download_format1 = col8.radio("Download as:", ("TXT", "PDF", "HTML", "MD", "DOCX", "PPTX"),
                                                key='download1')

                    if download_format1:
                        container4.warning("This history will be downloaded")
                        container5.markdown(text)
                        now = datetime.datetime.now()
                        if download_format1 == "TXT":
                            formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
                            col7.download_button(
                                label="Download TXT",
                                data=text.encode("utf-8"),  # Encode to bytes for download
                                file_name=f"{formatted_time}_gemini_chatbot.txt",
                                mime="text/plain",
                            )
                        elif download_format1 == "PDF":
                            formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")

                            col7.download_button(
                                label="Download PDF",
                                data=convert_markdown_to_pdf(text.encode("utf-8")),
                                # Encode to bytes for download
                                file_name=f"{formatted_time}_gemini_chatbot.pdf",
                                mime="application/pdf",
                            )
                        elif download_format1 == "MD":

                            formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")

                            col7.download_button(
                                label="Download Markdown",
                                data=text.encode("utf-8"),  # Encode to bytes for download
                                file_name=f"{formatted_time}_gemini_chatbot.md",
                                mime="text/plain",
                            )
                            # convert_markdown_to_pptx
                        # Customize format as needed.
                        elif download_format1 == "HTML":
                            formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
                            col7.download_button(
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
                                col7.download_button(
                                    label="Download DOCX",
                                    data=buffer.getvalue(),
                                    file_name=f"{formatted_time}_gemini_chatbot.docx",
                                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                )
                        elif download_format1 == "PPTX":

                            formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
                            pptx_bytes = convert_markdown_to_pptx(html_output)
                            col7.download_button(
                                label="Download PPTX",
                                data=pptx_bytes,
                                file_name=f"{formatted_time}_gemini_chatbot.pptx",
                                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation")






except Exception as error:
   print(error)
