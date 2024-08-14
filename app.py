import os
import streamlit as st
from streamlit_chat import message
from Chatbot_MongoDB_Groq.chatbot import ChatBot

st.subheader("Chat With DataBeez Platform")

file_path = os.getcwd() + '/data/fake_document_calendrier_LMS.txt'

try:
    chatbot = ChatBot(file_path)
except Exception as e:
    st.error(f"Failed to initialize chatbot: {e}")
    st.stop()

if 'responses' not in st.session_state:
    st.session_state['responses'] = ["How can I assist you?"]

if 'requests' not in st.session_state:
    st.session_state['requests'] = []

st.title("Langchain Chatbot")

response_container = st.container()
textcontainer = st.container()

with textcontainer:
    query = st.text_input("Query: ", key="input")

    if query:
        st.session_state['requests'].append(query)
        response = chatbot.chat(query)
        st.session_state['responses'].append(response)

with response_container:
    if st.session_state['responses']:
        for i in range(len(st.session_state['responses'])):
            message(st.session_state['responses'][i], key=str(i))
            if i < len(st.session_state['requests']):
                message(st.session_state["requests"][i], is_user=True, key=str(i) + '_user')
