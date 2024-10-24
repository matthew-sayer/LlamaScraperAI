import streamlit as st
from src.Data.analyticsService import AnalyticsService

st.header("Performance and Transaction Analytics")

columnsInput = st.text_input("Optional: Enter custom columns to query.", value="*")
filtersInput = st.text_input("Optional: Enter custom SQL filters (such as WHERE clauses). Leave blank for no filters.")

if st.button('Query Data'):
    if 'analyticsService' in st.session_state:
        try:
            performanceData = st.session_state['analyticsService'].retrievePerformanceData(columnsInput, filtersInput)
            st.table(performanceData)
        except Exception as e:
            st.write(f"Failed to retrieve data: {e}")
    else:
        st.write("Analytics service not initialised.")

if st.button('See Transaction Scores'):
    if 'analyticsService' in st.session_state:
        try:
            autoEvaluatedData = st.session_state['analyticsService'].retrieveAutoEvaluationData(columnsInput, filtersInput)
            manualEvaluatedData = st.session_state['analyticsService'].retrieveManualEvaluationData(columnsInput, filtersInput)
            st.table(autoEvaluatedData)
            st.table(manualEvaluatedData)
        except Exception as e:
            st.write(f"Failed to retrieve data: {e}")



if not columnsInput:
    columnsInput = "*" #Default to all columns if input is empty

if 'analyticsService' not in st.session_state:
    st.session_state['analyticsService'] = AnalyticsService()