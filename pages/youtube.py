import shutil

import streamlit as st
from pytube.request import filesize
#from pytube import YouTube
from pytubefix import YouTube
from pydub import AudioSegment
import os
import io
from openai import OpenAI
import google.generativeai as geneai
from qdrant_client.http import model
from retry import retry
from pytubefix.cli import on_progress

from pydub import AudioSegment

from langchain_google_genai import ChatGoogleGenerativeAI

from youtube_transcript_api import YouTubeTranscriptApi
import pandas as pd
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

@st.cache_resource
def askQuery(Ask,transcript, model,germin_key):
        try:
            llm = ChatGoogleGenerativeAI(model=model, api_key=germin_key)
            prompt = f""" Here's a transcript:\n\n
            {transcript}\n\n\n\n. You are expert on YouTube Transcript api. You can synthesize and interpret any given transcript and 
            You  provide accurate answers to this question.:{Ask}"""
            answer = llm.invoke(prompt)
            return answer.content
        except Exception as error:
            st.error(error)

                # Clean up the temporary audio file
                #os.remove(audio_path)
#main()
video_url = st.text_input("Enter YouTube Video URL:")

if video_url:
    try:
        yt = YouTube(video_url)
        container = st.container(border=True)
        # Display video information
        container.subheader("Video Information")
        container.write(f"Title: {yt.title}")
        container.write(f"Author: {yt.author}")
        container.write(f"Views: {yt.views}")
        container.write(f"Length: {round(yt.length/60,2)} minutes")

        container1 = st.container(border=True)
        container1.subheader("Display YouTube Video")

        # Display video
        container1.video(video_url)



        # Download video
        container2 = st.container(border=True)
        container2.subheader("You can the Download Video")
        video_stream = yt.streams.get_highest_resolution()  # Get highest resolution by default
        buffer = io.BytesIO()
        video_stream.stream_to_buffer(buffer)
        buffer.seek(0)

        container2.download_button("Download Video", data=buffer.read(), file_name=f"{yt.title}.mp4", mime="video/mp4")



        # Extract MP3 audio
        container3 = st.container(border=True)
        container3.subheader("Download Audio (MP3)")
        buffer1 = io.BytesIO()
        audio_stream = yt.streams.filter(only_audio=True).first()
        audio_stream.stream_to_buffer(buffer1)
        buffer1.seek(0)
        container3.download_button("Download Audio", data=buffer1.read(), file_name=f"{yt.title}.mp3", mime="audio/mpeg")
        container4 = st.container(border=True)

        # Extract transcript
        container4.subheader("YouTube Transcript")
        lang = container4.selectbox(
            "Choose language",
            ["en","de","fr","eo","zh-Hans","el","iw","hi","ru","sw"],
            key='language'
        )


        try:
            transcript = YouTubeTranscriptApi.get_transcript(yt.video_id, languages=[lang],)
            long_text=''
            for text in transcript:
                print(text['text'])
                long_text += text['text'] + ' '
            container4.subheader("Entire Transcript")
            container4.write(long_text)
            api_key = germinApiKey()
            if api_key:
                geneai.configure(api_key=api_key)
                os.environ['GOOGLE_API_KEY'] = api_key
            choice = []
            flash_vision = []
            for m in geneai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    st.write(m.name)
                    model_name = m.name.split("/")[1]
                    choice.append(model_name)
                    if "2.0" in str(model_name).lower() or "-exp" in model_name:
                        flash_vision.append(model_name)
            question = container4.text_input(
                "### Ask something about Transcript:",
                placeholder="Can you give me a short summary in German?",
                disabled=not api_key,
            )
            model1 = container4.radio(
                "Choose a Model",
                flash_vision,
                key='model1')
            container4.markdown(askQuery(Ask=question, transcript= long_text, model=model1, germin_key= api_key))



        except Exception as e:
            st.error(f"Error getting transcript: {e}")  # Handle potential transcript errors

    except Exception as e:
        st.error(f"Error processing video: {e}")  # Handle invalid URL or other PyTube errors
