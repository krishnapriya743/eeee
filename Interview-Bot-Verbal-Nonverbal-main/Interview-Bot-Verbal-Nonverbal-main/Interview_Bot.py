import os
import time
import openai
import streamlit as st
from PyPDF2 import PdfReader
from dotenv import load_dotenv
from streamlit.components.v1 import html
from llama_index import VectorStoreIndex, SimpleDirectoryReader
import ast
from gtts import gTTS

# from htmlTemplates import css, bot_template, user_template


# List of directory names to be created
dir_names = ['audio', 'data', 'response']

for dir_name in dir_names:
    # Check if the directory already exists
    if not os.path.exists(dir_name):
        # Create the directory
        os.makedirs(dir_name)
        print(f"Directory {dir_name} created.")
    else:
        print(f"Directory {dir_name} already exists.")


def check_openai_api_key(api_key):
    openai.api_key = api_key
    try:
        # Retrieve a specific model
        openai.Model.retrieve("text-davinci-002")
    except Exception as e:
        return False
    else:
        return True



def convert_questions_to_audio(list_of_questions):
    for i, question in enumerate(list_of_questions):
        language = "en"
        # Convert translated text into speech audio
        speak = gTTS(text=question, lang=language, slow=False)
        speak.save(f"./audio/Q_{i}.mp3")
    return True


def nav_page(page_name, timeout_secs=3):
    nav_script = """
        <script type="text/javascript">
            function attempt_nav_page(page_name, start_time, timeout_secs) {
                var links = window.parent.document.getElementsByTagName("a");
                for (var i = 0; i < links.length; i++) {
                    if (links[i].href.toLowerCase().endsWith("/" + page_name.toLowerCase())) {
                        links[i].click();
                        return;
                    }
                }
                var elasped = new Date() - start_time;
                if (elasped < timeout_secs * 1000) {
                    setTimeout(attempt_nav_page, 100, page_name, start_time, timeout_secs);
                } else {
                    alert("Unable to navigate to page '" + page_name + "' after " + timeout_secs + " second(s).");
                }
            }
            window.addEventListener("load", function() {
                attempt_nav_page("%s", new Date(), %d);
            });
        </script>
    """ % (page_name, timeout_secs)
    html(nav_script)


def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text


def build_context(pdf_docs, company_name):
    # Build custom context
    raw_text = get_pdf_text(pdf_docs)
    context = f"""
        This document describes the required information to to know all about conducting a specific interview:
        The candidate whom we are interviewing has the following resume content: \n {raw_text} \n. This is a role for {company_name}, and the job description for the role is mentioned here: \n {job_description} 
    """
    with open('./data/context.txt', 'w') as f:
        # Write some text to the file
        f.write(context)
    documents = SimpleDirectoryReader("data").load_data()
    index = VectorStoreIndex.from_documents(documents)
    query_engine = index.as_query_engine()
    return query_engine


st.set_page_config(
    page_title="Let's Prepare You For That Interview!",
    page_icon="👋",
)

openai_api_key = st.sidebar.text_input('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')
if st.sidebar.button('submit'):
    with open('.env', 'w') as f:
        f.write(f'OPENAI_API_KEY="{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}"')
    load_dotenv()
st.write("# Let's Prepare You For That Interview!")

with st.sidebar:
    st.subheader("Upload Resume")
    pdf_docs = st.file_uploader(
        "Upload your resume in PDF format here", accept_multiple_files=True)
    # if st.button("Process"):
    #     with st.spinner("Processing"):
    #         raw_text = get_pdf_text(pdf_docs)
    #         print(raw_text)

st.title('Job Description')
job_description = st.text_input('Enter the job description')
st.title('Company Name')
company_name = st.text_input('Enter the name of the company')
st.title('Interview Type')
interview_type = st.text_input('Enter the type of interview, for example: behavioural, technical, HR, etc (for '
                               'Non-Verbal, only technical would apply)')
st.title('Time Duration')
time_duration = st.text_input('Enter the anticipated time for this interview')

if st.button("Verbal"):
    query_engine = build_context(pdf_docs, company_name)
    with st.spinner("Processing"):
        query_1 = f"""Assume your role as an interviewer, you have to come up with appropriate number of interview 
        questions to be asked in a {interview_type} interview for {company_name}. The interview is going to be taken 
        verbally, produce appropriate number of question that could be asked in {time_duration} minutes considering 
        realistic situations. Be sure to list down your response in a comma separated manner in a python list format. """
        response_1 = query_engine.query(query_1)
        query_2 = f"This is a python representation of a list of questions\n {response_1}, these are to be fed into a " \
                  f"text to speech module, and each item of this so called list is going to go through a for loop one " \
                  f"by one. Can you vet this list such that all questions to be asked makes sense, once you have " \
                  f"verified, return your response in a similar python list format where each vetted questions is " \
                  f"placed as an item in it "
        response_2 = query_engine.query(query_2)
        print(response_2)
        list_of_questions = ast.literal_eval(str(response_2))
        if convert_questions_to_audio(list_of_questions=list_of_questions):
            nav_page("verbal_module")

if st.button("non-verbal"):
    query_engine = build_context(pdf_docs, company_name)
    with st.spinner("Processing"):
        query_1 = f"""Assume your role as an interviewer, you have to come up with appropriate number of technical questions (problem solving questions) 
        to be solved by a candidate in a {interview_type} interview for {company_name}. The questions should be such, that the answer to them is either wrong or right, but not subjective. The problem solving session is going to be taken 
        in written/typed answer format, produce appropriate number of question that could be asked in {time_duration} minutes considering realistic situations. Make sure that the questions are very specific at all circumstances. Be sure to list down your response in a comma separated manner in a python list format. """
        response_1 = query_engine.query(query_1)
        query_2 = f"This is a python representation of a list of questions\n {response_1}, these are to be fed into a " \
                  f"written/typed question-answering module, and each item of this so called list is going to go " \
                  f"through a for loop one " \
                  f"by one. Can you vet this list such that all questions to be asked makes sense, once you have " \
                  f"verified, return your response in a similar python list format where each vetted questions is " \
                  f"placed as an item in it "
        response_2 = query_engine.query(query_2)
        print(response_2)
        # print(response_1)
        # print("#################################")
        # print(response_2)
        list_of_questions = ast.literal_eval(str(response_2))
        print(list_of_questions)
        with open('./data/nonverbal_questions.txt', 'w') as f:
            for num, each_question in enumerate(list_of_questions):
                # write question in txt file

                if num < len(list_of_questions) - 1:
                    f.write(f"{each_question}, ")
                else:
                    f.write(each_question)
        time.sleep(2)
        nav_page("nonverbal_module")

if st.button("start fresh"):
    directories = ["audio", "data", "response"]
    for directory in directories:
        directory_path = f"{os.getcwd()}/{directory}"
        files_in_directory = os.listdir(directory_path)
        # Iterate over the list of files
        for file in files_in_directory:
            # Construct full file path
            file_path = os.path.join(directory_path, file)

            # If the file is a file (not a directory), then remove it
            if os.path.isfile(file_path):
                os.remove(file_path)
