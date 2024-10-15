import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

import streamlit as st
import pandas as pd

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

def initialiseSessionState():
    if 'data' not in st.session_state:
        st.session_state['data'] = None
    if 'scrapedURLs' not in st.session_state:
        st.session_state['scrapedURLs'] = pd.DataFrame()
    if 'conversation' not in st.session_state:
        st.session_state['conversation'] = None
    if 'url' not in st.session_state:
        st.session_state['url'] = None
    
    if st.session_state['data'] is not None and st.session_state['conversation'] is None:
        st.session_state['conversation'] = getConversationalAI(st.session_state['data'])

initialiseSessionState()

@st.cache_data
@handleErrors(default_return_value=(None, None))
def loadData(ingestionPath, maxURLs):
    return datapl.pipeline(ingestionPath, maxURLs)

@st.cache_resource
def getConversationalAI(data):
    return ConversationalAI(data)

url = st.text_input("Enter URL to scrape data from")
maxURLs = st.number_input("Enter the maximum number of URLs down to scrape? Set 1 for only the base URL.", min_value=1, max_value=200, value=1)

if st.button("Scrape Data from URL"):
    data, scrapedURLs = loadData(url, maxURLs)
    st.session_state['data'] = data
    st.session_state['scrapedURLs'] = scrapedURLs
    st.session_state['conversation'] = ConversationalAI(st.session_state['data'])
    st.session_state['url'] = url
    st.write("Data scraped successfully from source: ", url)
    st.balloons()

if not st.session_state['scrapedURLs'].empty:
    st.write("Scraped URLs:")
    st.table(st.session_state['scrapedURLs'])

if st.button("Clear Data"):
    td.clearTable()
    st.write("Data cleared successfully.")