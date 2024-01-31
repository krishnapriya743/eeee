import os
import streamlit as st
from llama_index import VectorStoreIndex, SimpleDirectoryReader
from Interview_Bot import nav_page

file_list = os.listdir("./response")

documents = SimpleDirectoryReader("data").load_data()
index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine()
static_query = """Imagine three different experts are evaluating this interview. They will brainstorm the answers given by the
candidate step by step reasoning carefully and taking all facts into consideration, i.e, the correctness of the
answer given, the tone of the answer given, and what improvements can be made in the candidate's answer. All experts
will write down 1 step of their thinking, then share it with the group. They will each critique their response,
and the all the responses of others They will check their answer based on science and the laws of physics Then all
experts will go on to the next step and write down this step of their thinking. They will keep going through steps
until they reach their conclusion taking into account the thoughts of the other experts If at any time they realise
that there is a flaw in their logic they will backtrack to where that flaw occurred If any expert realises they're
wrong at any point then they acknowledges this and start another train of thought Each expert will assign a
likelihood of their current assertion being correct Continue until the experts agree on the single most likely
location The question is... *\n """

for idx, file_name in enumerate(file_list):
    print(file_name)
    st.title(f'Response {idx}')
    audio_file = open(f'response/{file_name}', 'rb')
    audio_bytes = audio_file.read()
    st.audio(audio_bytes, format='audio/mp3')
    if st.button(f"Was your response.{idx} correct?"):
        correctness_query = f"Was the response that the candidate gave for question.{idx} was correct, answer in yes, no, or partially correct."
        correctness_res = query_engine.query(correctness_query)
        st.text(str(correctness_res))
    if st.button(f"What could you have done better in your response.{idx}?"):
        improvement_query = f"In the response that the candidate gave for the question.{idx}, what could they have done better. Be specific to the kind of improvements needed."
        improvement_res = query_engine.query(improvement_query)
        st.text(str(improvement_res))