import streamlit as st
from VidSum import VidSum
import streamlit_scrollable_textbox as stx
from streamlit_chat import message
import socket
import pandas as pd

st.set_page_config(page_title="VidSum") 

if "questions" not in st.session_state:
    st.session_state.questions = []
    
if "answers" not in st.session_state:
    st.session_state.answers = []
    
    
@st.cache_resource
def initailize_summarizer(video_link):
    tube_summarizer = VidSum()
    st.session_state.questions = []
    st.session_state.answers = []
    return tube_summarizer
    
@st.cache_resource
def load_script(video_link):
    script = tube_summarizer.load_video_script(video_link=video_link)
    return script

@st.cache_resource
def generate_summary(video_link):
    summary = tube_summarizer.summarize_video()
    return summary


@st.cache_resource
def embed_script(video_link):
    tube_summarizer.embed_video_script()
    
     
st.markdown("<h1 style='text-align: center; color: #FFF;'>VidSum</h1>", unsafe_allow_html=True)
st.markdown('#### I. YouTube Video URL')
video_link = st.text_input("URL :", placeholder="YouTube Video URL")

tube_summarizer = initailize_summarizer(video_link)

if tube_summarizer.is_valid_youtube_link(video_link):
    st.markdown('#### II. YouTube Video Player')
    st.video(video_link)

    script = load_script(video_link)

    if script and len(script) > 0 and len(script) <= 20000:

        st.markdown('#### III. Video Script')
        stx.scrollableTextbox(script, height=200)

        st.markdown('#### IV. Summarization / Chat')
        choice = st.selectbox("Choose an option :", ('Summarization', 'Chat'))

        if choice == "Summarization":
            if st.button("Generate Summary"):
                summary = generate_summary(script)
                stx.scrollableTextbox(summary, height=200)
        else:
            question = st.text_input("Question: ", placeholder="Type your question here")
            if st.button("Generate Answer"):
                embed_script(script)
                st.session_state.questions.append(question)
                
                with st.spinner("Answering..."):
                    answer = tube_summarizer.chat_video(question)
                    
                st.session_state.answers.append(answer)
                
            if st.button("Clear Chat"):
                st.session_state.questions = []
                st.session_state.answers = []
            
            for i in reversed(list(range(len(st.session_state.questions)))) :
                try:
                    message(st.session_state.answers[i]) 
                    message(st.session_state.questions[i], is_user=True)  # align's the message to the right
                except:
                    pass
                    
    elif len(script) > 20000 :
        st.error("Your video is too long, It's gonna cost too much :)")
    else:
        st.error("Your video doesn't have subtitles :(")
else:
    if video_link != "":
        st.error("Please provide a valid YouTube video URL")