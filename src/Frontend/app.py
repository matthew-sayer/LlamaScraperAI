import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import streamlit as st
from src.Data import pipeline as datapl
from src.AI.ConversationalAI import ConversationalAI
from src.Misc.error_handling import handleErrors


st.title("QnAScraperAI - Webscraper and Conversational AI Tool")
st.write("Select a URL to ingest data from, and then begin your Question and Answer session.")


@st.cache_data
@handleErrors(default_return_value=None)
def loadData(ingestionPath, maxURLs):
    data = datapl.pipeline(ingestionPath, maxURLs)
    return data

@handleErrors()
def main():

    url = st.text_input("Enter URL to scrape data from")
    maxURLs = st.number_input("Enter the maximum number of URLs down to scrape? Set 1 for only the base URL.", min_value=1, max_value=200, value=1)

    if st.button("Scrape Data from URL"):
        st.session_state['data'] = loadData(url, maxURLs)
        st.session_state['conversation'] = ConversationalAI(st.session_state['data'])
        st.session_state['url'] = url
        st.write("Data scraped successfully from source: ", url)

    if 'url' in st.session_state:
        st.write("Your data is ready for use, you may begin asking questions when you are ready.")
    
    if 'data' in st.session_state:
            st.write("Extracted Data:")
            st.dataframe(st.session_state['data'])
            
            searchInput = st.text_input("Search within scraped data: ")
            if searchInput:
                filteredData = st.session_state['data'][st.session_state['data']['scrapedText'].str.contains(searchInput, case=False)] #Removes case sensitivity.
                st.dataframe(filteredData, width=1000)
    
    if 'conversation' in st.session_state:
        question = st.text_input("Enter your question here: ")
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