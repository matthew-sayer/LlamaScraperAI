import streamlit as st

st.set_page_config(
    page_title="Search Extracted Data",
    page_icon="🔍"
)

st.title("Search through your Extracted Data")

if 'data' in st.session_state:
    searchInput = st.text_input("Search within collected data: ")
    if searchInput:
        filteredData = st.session_state['data'][st.session_state['data']['scrapedText'].str.contains(searchInput, case=False)]
        st.dataframe(filteredData, width=1000)
    else:
        st.dataframe(st.session_state['data'], width=1000)
else:
    st.write("Please go to the Ingest Data page to scrape data first.")