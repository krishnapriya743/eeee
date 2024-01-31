import os
import streamlit as st
from Interview_Bot import nav_page
from llama_index import VectorStoreIndex, SimpleDirectoryReader

documents = SimpleDirectoryReader("data").load_data()
index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine()

static_query = """Imagine three different experts are evaluating this interview question. They will brainstorm the answers given by the
candidate step by step reasoning carefully and taking all facts into consideration, i.e, the correctness of the
answer given (i.e, correct, or incorrect), and what improvements can be made in the candidate's answer. All experts
will write down 1 step of their thinking, then share it with the group. They will each critique their response,
and the all the responses of others They will check their answer based on science and the laws of physics Then all
experts will go on to the next step and write down this step of their thinking. They will keep going through steps
until they reach their conclusion taking into account the thoughts of the other experts If at any time they realise
that there is a flaw in their logic they will backtrack to where that flaw occurred If any expert realises they're
wrong at any point then they acknowledges this and start another train of thought Each expert will assign a
likelihood of their current assertion being correct Continue until the experts agree on the single most likely
location The question is... *\n """


def read_questions():
    # os.chdir('../')
    # print(os.getcwd())

    # Print the new current working directory
    print()
    # Adding question-response
    with open(f'{os.getcwd()}/data/nonverbal_questions.txt', 'r') as file:
        # Read the entire content of the file
        questions = file.read()
    question_list_temp = questions.split(",")
    return question_list_temp


question_list = read_questions()

st.header("Let's try and solve these problems")
question_answer_confidence = list(list())

with open('nonverbal_question_answer.txt', 'w') as f:
    f.write(f"A technical interview was conducted and the question asked, along with the candidate's confidence in succesfully answering the problem, and the actual response is recorded down below:\n")


for idx, question in enumerate(question_list):
    st.title(
        f"Rate your confidence for successfully solving the following problem, only answer in C (for confident), P(Partially confident) and I(For not confident):")
    st.text(question)
    confidence = st.radio(f'Select confidence level for question {idx}:', ['C', 'P', 'I'])
    print(confidence)
    st.text("Try and solve the problem now")
    user_solution = st.text_area(f'Solve here for question {idx}')
    if st.button(f'Submit solution {idx}'):
        correctness_query = f"Was the response that the candidate gave for question: {question} was correct, answer in yes, no, or partially correct. If the candidate has not answered it,then call it not attempted. The candidate's given answer was: {user_solution}"
        correctness_res = query_engine.query(correctness_query)
        print("yaha")
        print(correctness_res)
        st.title("Correctness of your response:")
        st.text(str(correctness_res))
        improvement_query = f"In the response that the candidate gave for the question.{question}, what could they have done better. Be specific to the kind of improvements needed. Here is what the candidate's response looked like: {user_solution}"
        improvement_res = query_engine.query(improvement_query)
        st.title("Improvement tip(s):")
        st.text(str(improvement_res))
        question_answer_confidence.append([question, user_solution, confidence])
        print("Submitted")
        print(question_answer_confidence)

if st.button('Submit'):
    with st.spinner("Processing"):
        st.title("Thank you for taking the test!")
