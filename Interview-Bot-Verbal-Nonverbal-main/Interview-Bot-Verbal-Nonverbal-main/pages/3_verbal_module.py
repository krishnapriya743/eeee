import os
import whisper
import streamlit as st
from audio_recorder_streamlit import audio_recorder
from llama_index import VectorStoreIndex, SimpleDirectoryReader
from Interview_Bot import nav_page

# Get the list of files in the directory
file_list = os.listdir("./audio")
model = whisper.load_model("base")


def transcribe_question_answer():
    # Adding question-response
    with open('./data/context.txt', 'r') as file:
        # Read the entire content of the file
        context = file.read()
        updated_context = f"{context} \n After the interview was conducted, the response of the candidate to each " \
                          f"question was " \
                          f"recorded. Below are the list of questions followed by their answer given by the " \
                          f"candidate is " \
                          f"listed.\n "
    with open('./data/updated_context.txt', 'w') as f:
        f.write(updated_context)

    question_answer_temp = list(list())
    for i, response in enumerate(response_list):
        last_part = response.split('_')[-1]
        # Now, split by '.' and take the first part to get the index
        idx = last_part.split('.')[0]
        question_text = model.transcribe(f"./audio/Q_{idx}.mp3")['text']
        response_text = model.transcribe(response)['text']
        question_answer_temp.append([question_text, response_text])
        with open('./data/updated_context.txt', 'a') as f:
            # Updating context.txt
            f.write(f"The question.{idx} asked was:\n{question_text}")
            f.write(f"The response to question.{idx} given by the candidate was:\n{response_text}")
    return question_answer_temp


# Print the list of files
print("Files in the directory:")
response_list = list()
for idx, file_name in enumerate(file_list):
    print(file_name)
    st.title(f'Question {idx}')
    audio_file = open(f'audio/{file_name}', 'rb')
    audio_bytes = audio_file.read()
    st.audio(audio_bytes, format='audio/mp3')
    st.title(f'Speak here for response {idx}')
    audio_bytes = audio_recorder(energy_threshold=(-1.0, 1.0), pause_threshold=120.0, key=f'audio_recorder_{idx}')
    if audio_bytes:
        with open(f'response/response_{idx}.wav', 'wb') as f:
            f.write(audio_bytes)
            response_list.append(f'response/response_{idx}.wav')
        st.audio(audio_bytes, format="audio/wav")

if st.button("Submit"):
    with st.spinner("Processing.."):
        question_answer = transcribe_question_answer()
        # print(question_answer[0][1])
        # st.text(f" question was : \n {question_answer[0][0]}")
        # st.text(f" response was : \n {question_answer[0][1]}")
        nav_page("verbal_feedback")
