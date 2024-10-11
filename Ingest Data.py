import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import streamlit as st
from src.Data import pipeline as datapl
from src.Data import transformData as td
from src.AI.conversationalAI import ConversationalAI
from src.Misc.error_handling import handleErrors

st.set_page_config(
    page_title="Ingest Data", 
    page_icon="💾",
    initial_sidebar_state="expanded"
)

st.title("Ingest your Data")
st.write("Select a URL to scrape data from.")

@st.cache_data
@handleErrors(default_return_value=None)
def loadData(ingestionPath, maxURLs):
    return datapl.pipeline(ingestionPath, maxURLs)

@st.cache_resource
def getConversationalAI(data):
    return ConversationalAI(data)

url = st.text_input("Enter URL to scrape data from")
maxURLs = st.number_input("Enter the maximum number of URLs down to scrape? Set 1 for only the base URL.", min_value=1, max_value=200, value=1)

if st.button("Scrape Data from URL"):
    st.session_state['data'] = loadData(url, maxURLs)
    st.session_state['conversation'] = ConversationalAI(st.session_state['data'])
    st.session_state['url'] = url
    st.write("Data scraped successfully from source: ", url)
    st.balloons()

if st.button("Clear Data"):
    td.clearTable()
    st.write("Data cleared successfully.")