import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import streamlit as st
from src.Data import pipeline as datapl
from src.AI.ConversationalAI import ConversationalAI
from src.Orchestration.error_handling import handleErrors


st.title("WebQnA Conversational AI Tool")
st.write("Select a URL to ingest data from, and then begin your Question and Answer session.")


@st.cache_data
@handleErrors(default_return_value=None)
def load_data(ingestionPath):
    data = datapl.pipeline(ingestionPath)
    return data

@handleErrors()
def main():

    url = st.text_input("Enter URL to scrape data from")
    if st.button("Scrape Data from URL"):
        st.session_state['data'] = load_data(url)
        st.session_state['conversation'] = ConversationalAI(st.session_state['data'])
        st.session_state['url'] = url
        st.write("Data scraped successfully from source: ", url)

    if 'url' in st.session_state:
        st.write("Your data is ready for use, you may begin asking questions when you are ready.")
    
    if 'conversation' in st.session_state:
        question = st.text_input("Enter your question here: ")
        # aadd enter ky to submit question
        if st.button("Ask Question"):
            if question:
                response = st.session_state['conversation'].generateResponse(question)
                st.write("Question: ", question)
                st.write("Answer: ", response)
            else:
                st.write("Please enter a question before submitting.")
    if st.button("Clear Data"):
        st.session_state.clear()
        st.write("Data cleared successfully. Please enter a new URL to scrape data from.")


if __name__ == "__main__":
    main() 