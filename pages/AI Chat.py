import streamlit as st
from src.AI.conversationalAI import ConversationalAI
from src.Misc.error_handling import handleErrors
from src.AI.speechToText import SpeechToText

st.set_page_config(
    page_title = "AI Chat",
    page_icon = "🤖",
    initial_sidebar_state="expanded"
)
st.title("Chat with **Meta's Llama 3**")

if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []


if st.session_state['data'] is not None:
    st.write("Ask a question and receive a response based on your data.")

    #Show chat history box
    if st.session_state['chat_history']:
        for message in st.session_state['chat_history']:
            with st.chat_message(message['role']):
                st.markdown(message['content'])
    
    if prompt := st.chat_input("Enter your question here..."):
        st.session_state['chat_history'].append({'role': 'user', 'content': prompt})
        with st.chat_message("user"):
            st.markdown(prompt) #Show user input in chat box, with 'user' role
        with st.spinner("Generating response, please wait as it's a slow and powerful model..."):
            response = st.session_state['conversation'].generateResponse(
                prompt,
                topKSetting=st.session_state.get('topKSetting', 5), #Get topKSetting from session state, or default to 5
                temperature=st.session_state.get('temperature', 0.7),
                topP=st.session_state.get('topP', 0.9),
                maxLlamaTokens=st.session_state.get('maxLlamaTokens', 40)
                )
        st.session_state['chat_history'].append({'role': 'bot', 'content': response})
        with st.chat_message("bot"):
            st.markdown(response)

    
    #audioRecording = st.experimental_audio_input("Record a question with your voice")
    #if audioRecording:
     #   st.audio(audioRecording)
      #  transcribedAudio = SpeechToText().convertAudioToText(audioRecording)
       # st.session_state['chat_history'].append({'role': 'user', 'content': transcribedAudio})

        #with st.chat_message("user"):
         #   st.markdown(transcribedAudio)
        
        #response = st.session_state['conversation'].generateResponse(transcribedAudio)
        #st.session_state['chat_history'].append({'role': 'bot', 'content': response})
        #with st.chat_message("bot"):
         #   st.markdown(response)

else:
    st.write("Please go to the Ingest Data page to scrape data first")
   

