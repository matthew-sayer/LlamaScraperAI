import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

import streamlit as st
import pandas as pd

from src.Data import pipeline as datapl
from src.Data.transformData import TransformData
from src.AI.conversationalAI import ConversationalAI
from src.Misc.error_handling import handleErrors
from src.Data.analyticsService import AnalyticsService


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
    if 'transform' not in st.session_state:
        st.session_state['transform'] = None
    if 'analyticsService' not in st.session_state:
        st.session_state['analyticsService'] = AnalyticsService()
    
    
    if st.session_state['data'] is not None and st.session_state['conversation'] is None:
        st.session_state['conversation'] = getConversationalAI(st.session_state['data'])

initialiseSessionState()

@st.cache_resource
@handleErrors(default_return_value=(None, None, None))
def loadData(ingestionPath, maxURLs):
    return datapl.pipeline(ingestionPath, maxURLs)

@st.cache_resource
def getConversationalAI(data, analyticsService):
    return ConversationalAI(data, analyticsService)

url = st.text_input("Enter URL to scrape data from")
maxURLs = st.number_input("Please enter the maximum number of URL levels down to scrape. Set 1 for only the base URL.", min_value=1, max_value=200, value=1)

if st.button("Scrape Data from URL"):
    data, scrapedURLs, extractTransformObject = loadData(url, maxURLs)
    st.session_state['data'] = data
    st.session_state['scrapedURLs'] = scrapedURLs
    st.session_state['conversation'] = ConversationalAI(st.session_state['data'])
    st.session_state['url'] = url
    st.session_state['transform'] = extractTransformObject
    st.write("Data scraped successfully from source: ", url)
    st.balloons()

if not st.session_state['scrapedURLs'].empty:
    st.write("Scraped URLs:")
    st.table(st.session_state['scrapedURLs'])

if st.button("Clear Data"):
    if 'transform' in st.session_state and st.session_state['transform'] is not None:
        st.session_state['transform'].clearTable()
        st.session_state['data'] = None
        st.write("Data cleared successfully.")
    else:
        st.write("No data to clear.")