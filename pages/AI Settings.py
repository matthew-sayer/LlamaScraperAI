import streamlit as st

st.title("Configure your AI Settings")

if 'topKSetting' not in st.session_state:
    st.session_state['topKSetting'] = 5
if 'topP' not in st.session_state:
    st.session_state['topP'] = 0.9
if 'temperature' not in st.session_state:
    st.session_state['temperature'] = 0.7
if 'maxLlamaTokens' not in st.session_state:
    st.session_state['maxLlamaTokens'] = 40

topKSetting = st.slider("Select the top K value (how many close-matching data rows to consider)", 0, 50, st.session_state['topKSetting'], 1)
temperature = st.slider("Select the temperature (randomness) of responses", 0.0, 2.0, st.session_state['temperature'], 0.1)
topP = st.slider("Select the top P value of responses (how many words (tokens) are considered)", 0.0, 1.0, st.session_state['topP'], 0.1)
maxLlamaTokens = st.slider("Select the maximum tokens Llama should generate (max length of response)", 0, 100, st.session_state['maxLlamaTokens'], 1)

if st.button("Save AI Chat Settings"):
    st.session_state['topKSetting'] = topKSetting
    st.session_state['temperature'] = temperature
    st.session_state['topP'] = topP
    st.session_state['maxLlamaTokens'] = maxLlamaTokens
    st.write("Settings saved successfully.")
