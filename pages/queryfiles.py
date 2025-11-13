# This pysqlite3 workaround is necessary for ChromaDB on Streamlit Sharing

import streamlit as st
import os
import pandas as pd
import google.generativeai as gen
from google import genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.document_loaders import PyPDFLoader


# --- Utility Functions ---

@st.cache_data
def list_gemini_models():
    """Lists available Gemini models that support content generation."""
    try:
        client = genai.Client(api_key=st.session_state['google_api_key'])
        gen.configure(api_key=st.session_state.germin_api_key)

        models = [
            m.name.split("/")[-1]
            for m in gen.list_models()
            if 'generateContent' in m.supported_generation_methods
        ]
        # Prioritize flash and pro models
        pro_models = sorted([m for m in models if "pro" in m], reverse=True)
        flash_models = sorted([m for m in models if "flash" in m], reverse=True)

        # Combine, with "pro" models listed first
        combined_models = pro_models + [m for m in flash_models if m not in pro_models]
        return combined_models, [f"gemini/{m}" for m in combined_models]
    except Exception as e:
        st.error(f"Error listing models: {e}")
        return [], []


@st.cache_data
def process_uploaded_file(uploaded_file, save_to_disk=False):
    """
    Processes an uploaded file (PDF, TXT, MD) and returns its text content.
    Optionally saves PDF to disk for external tools.
    """
    try:
        if uploaded_file.type == 'application/pdf':
            if not os.path.isdir("temp_dir"):
                os.mkdir("temp_dir")

            file_path = os.path.join("temp_dir", uploaded_file.name)

            with open(file_path, "wb") as f:
                f.write(uploaded_file.getvalue())

            loader = PyPDFLoader(file_path)
            pages = loader.load_and_split()
            article = " ".join([doc.page_content for doc in pages])

            # Don't delete if save_to_disk is True, as the path is needed
            if not save_to_disk:
                os.remove(file_path)

            return article, True, file_path if save_to_disk else None

        else:
            # For TXT or MD files
            article = uploaded_file.read().decode()
            return article, False, None

    except Exception as e:
        st.error(f"Error processing file {uploaded_file.name}: {e}")
        return None, False, None


# --- Cached AI Functions ---

@st.cache_resource
def RAGQuery(prompt, germin_key, model):
    """Queries the LLM with the provided prompt."""
    try:
        llm = ChatGoogleGenerativeAI(model=model, api_key=germin_key)
        answer = llm.invoke(prompt)
        return answer.content
    except Exception as error:
        st.error(error)
        return f"Error querying AI: {error}"


@st.cache_resource
def CVSummary(messages, model, germin_key):
    """Generates a summary for a CV."""
    try:
        llm = ChatGoogleGenerativeAI(model=model, api_key=germin_key)
        answer = llm.invoke(messages)
        return answer.content
    except Exception as error:
        st.error(error)
        return f"Error summarizing CV: {error}"


@st.cache_resource
def getCrewAIMatcher(profession, location, file_path, is_pdf, model, germin_key, serp_api):
    """Runs the CrewAI job matcher."""
    try:
        # Conditional import, assuming CrewAiMatcher is in tools/utils.py
        from tools.utils import CrewAiMatcher

        date = pd.to_datetime('today').date()
        yr = pd.to_datetime('today').year
        results = CrewAiMatcher(
            germin_key, serp_api, profession, yr, date,
            file_path, location, is_pdf, model
        ).run()
        return results
    except ImportError:
        st.error("Error: Could not find 'CrewAiMatcher'. Make sure 'tools/utils.py' exists.")
        return None
    except Exception as error:
        st.error(f"Error running AI Crew: {error}")
        return None


# --- Main Application ---

# Check for API keys from session state (set in nav.py)
if 'google_api_key' not in st.session_state or not st.session_state['google_api_key']:
    st.error("🚫 Google Gemini API Key not found. Please set it in the main app.")
    st.stop()
if 'serper_api_key' not in st.session_state or not st.session_state['serper_api_key']:
    st.error("🚫 Serper API Key not found. Please set it in the main app.")
    st.stop()

# Configure API keys
GEMINI_API_KEY = st.session_state['google_api_key']
SERPER_API_KEY = st.session_state['serper_api_key']
os.environ['GOOGLE_API_KEY'] = GEMINI_API_KEY
os.environ['SERPER_API_KEY'] = SERPER_API_KEY
gen.configure(api_key=GEMINI_API_KEY)

# Get models
model_names, gemini_model_paths = list_gemini_models()
if not model_names:
    st.error("Could not fetch Gemini models. Check your API key.")
    st.stop()

# --- UI Tabs ---
tab1, tab2 = st.tabs(["General File Q&A", "CV & Job Matcher"])

with tab1:
    st.header("Upload and Query Any File")
    st.write("Upload a local file (PDF, TXT, or MD) and ask questions about it.")

    uploaded_file = st.file_uploader("Upload an article", type=("txt", "md", "pdf"), key="tab1_uploader")

    if uploaded_file:
        st.info(f"File '{uploaded_file.name}' uploaded.")
        question = st.text_input(
            "Ask something about the uploaded file",
            placeholder="Can you give me a short summary in German?",
            key="tab1_question"
        )
        modelfile = st.radio(
            "Choose a Model",
            model_names,
            key='modelfile_tab1'
        )

        if question:
            with st.spinner(f"Processing '{uploaded_file.name}'..."):
                article, _, _ = process_uploaded_file(uploaded_file, save_to_disk=False)

            if article:
                prompt = f"""Here's an article:\n\n{article}\n\n\n\nUser Question: {question}"""

                with st.spinner("AI is thinking..."):
                    answer = RAGQuery(prompt, GEMINI_API_KEY, modelfile)
                    st.write("### Answer")
                    st.markdown(answer)

with tab2:
    st.header("CV & Job Matcher")
    st.write("Upload your CV to get a summary and find matching job openings.")

    uploaded_cv = st.file_uploader("Upload your CV", type=("txt", "md", "pdf"), key="tab2_uploader")

    if uploaded_cv:
        # Process and cache the CV data in session_state
        if 'current_cv_name' not in st.session_state or st.session_state.current_cv_name != uploaded_cv.name:
            with st.spinner(f"Processing CV: {uploaded_cv.name}..."):
                cv_text, is_pdf, file_path = process_uploaded_file(uploaded_cv, save_to_disk=True)
                if cv_text:
                    st.session_state.cv_text = cv_text
                    st.session_state.cv_is_pdf = is_pdf
                    st.session_state.cv_file_path = file_path
                    st.session_state.current_cv_name = uploaded_cv.name
                    # Clear old summary if a new CV is uploaded
                    if 'cv_summary' in st.session_state:
                        del st.session_state.cv_summary
                    st.success(f"Successfully processed '{uploaded_cv.name}'.")
                else:
                    st.error("Could not process the CV.")
                    if 'cv_text' in st.session_state:
                        del st.session_state.cv_text

    # Show options only if a CV has been processed and is in session
    if "cv_text" in st.session_state:

        # --- Step 1: CV Summary ---
        with st.expander("Step 1: Generate CV Summary (Optional)"):
            question1 = st.text_input(
                "Prompt for CV Summary",
                placeholder="Extract skills, profession, languages, education, and years of experience.",
                key="cv_summary_prompt"
            )
            modelfile1 = st.radio(
                "Choose a Model for Summary",
                model_names,
                key='modelfile_tab2'
            )

            if st.button("Generate Summary", key='cv_summary_button'):
                if question1:
                    messages = f"""
                    You are a helpful assistant with decades of Experience in Human Resources.
                    Here is the cv: {st.session_state.cv_text}.
                    Task: {question1}
                    The output MUST Be Formatted in markdown without ```"""

                    with st.spinner("Summarizing CV..."):
                        answer = CVSummary(messages, modelfile1, GEMINI_API_KEY)
                        st.session_state.cv_summary = answer  # Cache summary
                        st.write("### CV Summary")
                        st.markdown(answer)
                else:
                    st.warning("Please enter a prompt for the summary.")

            # If summary already exists in session, show it
            elif 'cv_summary' in st.session_state:
                st.write("### Cached CV Summary")
                st.markdown(st.session_state.cv_summary)

        # --- Step 2: Job Matcher ---
        st.subheader("Step 2: Match CV to Jobs")
        container = st.container(border=True)
        model1_match = container.radio(
            "Choose a Model for Matching",
            gemini_model_paths,  # CrewAI might need the full path
            key='model_match'
        )
        profession = container.text_input(
            "Your Profession",
            placeholder="e.g., Java Developer"
        )
        location = container.text_input(
            "Preferred Job Location",
            placeholder="e.g., Frankfurt"
        )

        if container.button("Match Jobs", key="match_button"):
            if not profession or not location:
                container.error("Please provide both a Profession and a Location.")
            else:
                with st.spinner("AI Crew is searching for jobs... This may take a moment."):
                    # *** FIXED BUG ***: Calling getCrewAIMatcher with correct keyword arguments
                    results = getCrewAIMatcher(
                        profession=profession,
                        location=location,
                        file_path=st.session_state.cv_file_path,
                        is_pdf=st.session_state.cv_is_pdf,
                        model=model1_match,
                        germin_key=GEMINI_API_KEY,
                        serp_api=SERPER_API_KEY
                    )

                    if results:
                        st.markdown(results)
                        # Try to read and display the job posting file
                        try:
                            st.subheader("Top 5 Job Postings")
                            file_adv = f'./Crew_AI/Reports/{profession}_posting.md'
                            with open(file_adv, 'r', encoding='utf-8') as f:
                                advisor_expert = f.read()
                            st.markdown(advisor_expert)
                        except FileNotFoundError:
                            st.info("Job posting detail file not found (this may be normal).")
                        except Exception as e:
                            st.error(f"Error reading job posting file: {e}")
                    else:
                        st.error("The AI Crew failed to return a result.")

    elif uploaded_cv and "cv_text" not in st.session_state:
        st.error("There was an issue processing your CV. Please try uploading it again.")
    else:
        st.info("Please upload your CV to begin.")
