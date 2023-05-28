import streamlit as st
from TubeSummarizer import TubeSummarizer
import streamlit_scrollable_textbox as stx
from streamlit_chat import message
import socket
import pandas as pd

st.set_page_config(page_title="TubeSummarizer") # page_icon=":smiley:", 

if "questions" not in st.session_state:
    st.session_state.questions = []
    
if "answers" not in st.session_state:
    st.session_state.answers = []
    
    
def get_ip_address():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    return ip_address
    
    
@st.cache_resource
def initailize_summarizer(video_link):
    tube_summarizer = TubeSummarizer()
    st.session_state.questions = []
    st.session_state.answers = []
    
    file = open('./ips.csv', 'a')
    file.write(get_ip_address()+"\n")
    file.close()
    
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
     
st.header("TubeSummarizer")
st.markdown('#### I : YouTube Video URL')
video_link = st.text_input("URL :", placeholder="https://www.youtube.com/watch?v=************")

tube_summarizer = initailize_summarizer(video_link)

if tube_summarizer.is_valid_youtube_link(video_link):
    st.video(video_link)

    script = load_script(video_link)

    if script and len(script) > 0 and len(script) <= 20000:

        df_ips = pd.read_csv('./ips.csv')
        count_ips = df_ips.iloc[:,0].to_list().count(get_ip_address())

        if (count_ips <= 5):
            st.markdown('#### II. Video script')
            stx.scrollableTextbox(script, height=200)

            st.markdown('#### III. Summarization / Q&A')
            choice = st.selectbox("Please choose an option :", ('Summarization', 'Q&A'))

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
                    
                if st.button("Clear chat"):
                    st.session_state.questions = []
                    st.session_state.answers = []
                
                
                for i in reversed(list(range(len(st.session_state.questions)))) :
                    try:
                        message(st.session_state.answers[i]) 
                        message(st.session_state.questions[i], is_user=True)  # align's the message to the right
                    except:
                        pass
        else:
            st.error("Maximum number of attempts reached, try again later :)")
    elif len(script) > 20000 :
        st.error("Your video is too long, It's gonna cost too much :)")
    else:
        st.error("Your video doesn't have subtitles :(")
else:
    if video_link != "":
        st.error("Please provide a valid YouTube video URL")