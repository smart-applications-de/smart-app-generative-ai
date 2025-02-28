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
def YouTubeTranscript(video_id,lang):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[lang])
        long_text=''
        for text in transcript:
            print(text['text'])
            long_text += text['text'] + ' '
        return long_text
    except Exception as error:
        st.error(error)


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
if video_url  not in st.session_state:
    st.session_state['video_url']=video_url


if  st.session_state['video_url']:
    try:
        yt = YouTube(st.session_state['video_url'])
        container = st.container(border=True)
        # Display video information
        container.subheader("Video Information")
        container.write(f"Title: {yt.title}")
        container.write(f"Author: {yt.author}")
        container.write(f"Views: {yt.views}")
        container.write(f"Length: {round(yt.length/60,2)} minutes")
        if yt not in st.session_state:
            st.session_state['video_id']=yt.video_id


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
        long_text = ''
        try:

            container5 = st.container(border=True)
            container4.warning('Please enter your Google Gemini API Key')
            "[Get GOOGLE API KEY](https://ai.google.dev/)"
            openai_api_key = container4.text_input(
                "GOOGLE API KEY", key="germin_api_key", type="password")
            if "germin_api_key" not in st.session_state:
                st.session_state['germin_api_key'] = openai_api_key


            if openai_api_key:
                geneai.configure(api_key=st.session_state['germin_api_key'])
                os.environ['GOOGLE_API_KEY'] = st.session_state['germin_api_key']
                choice = []
                flash_vision = []
                for m in geneai.list_models():
                    if 'generateContent' in m.supported_generation_methods:
                        #st.write(m.name)
                        model_name = m.name.split("/")[1]
                        choice.append(model_name)
                        if "2.0" in str(model_name).lower() or "-exp" in model_name:
                            flash_vision.append(model_name)
                lang = container4.radio(
                    "Choose a language",
                    ["en", "de", "fr", "eo", "sw", "ru", "hi", "el", "zh-Hans"],
                    key='lang')

                if "lang" not in st.session_state:
                    st.session_state['lang']=lang
                if st.session_state['lang'] and st.session_state['video_id'] :
                    text =YouTubeTranscript(st.session_state['video_id'],st.session_state['lang'])
                    container4.subheader("Entire Transcript")
                    container4.write(text)
                    if text not in st.session_state:
                        st.session_state['text']=text

                question = container5.text_input(
                    "### Ask something about Transcript:",
                    placeholder="Can you give me a short summary in German?",
                    key='question'
                )
                model1 = container5.radio(
                    "Choose a Model",
                    flash_vision,
                    key='model1')
                if "model1" not in st.session_state:
                    st.session_state['model1'] = model1
                if "question" not in st.session_state:
                    st.session_state['question'] = question
                if st.session_state['question'] and  st.session_state['model1'] and st.session_state['text']:
                    container5.subheader("Summary created by  AI")
                    container5.markdown(askQuery(Ask=question, transcript= st.session_state['text'], model=model1, germin_key=openai_api_key))






                # if container5.button(label='Get Transcript and AI Summary', key='Yt'):
                #     transcript = YouTubeTranscriptApi.get_transcript(yt.video_id, languages=[lang])
                #     for text in transcript:
                #         print(text['text'])
                #         long_text += text['text'] + ' '
                #     container4.subheader("Entire Transcript")
                #     text =YouTubeTranscript(st.session_state['video_id'],st.session_state['lang'])
                #     container4.write(text)
                #
                #     container5.subheader("Summary created by  AI")
                #     container5.markdown(askQuery(Ask=question, transcript= text, model=model1, germin_key=openai_api_key))



        except Exception as e:
            st.error(f"Error getting transcript: {e}")  # Handle potential transcript errors

    except Exception as e:
        st.error(f"Error processing video: {e}")  # Handle invalid URL or other PyTube errors
