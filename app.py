import streamlit as st
from TubeSummarizer import TubeSummarizer
import streamlit_scrollable_textbox as stx
from streamlit_chat import message

st.set_page_config(page_title="TubeSummarizer") # page_icon=":smiley:", 

if "questions" not in st.session_state:
    st.session_state.questions = []
    
if "answers" not in st.session_state:
    st.session_state.answers = []
    
@st.cache_resource
def initailize_summarizer(video_link):
    tube_summarizer = TubeSummarizer()
    st.session_state.questions = []
    st.session_state.answers = []
    return tube_summarizer
    
@st.cache_resource
def load_subtitles(video_link):
    subtitles = tube_summarizer.load_video_subtitles(video_link=video_link)
    return subtitles

@st.cache_resource
def generate_summary(video_link):
    summary = tube_summarizer.summarize_video()
    return summary


@st.cache_resource
def embed_script(video_link):
    tube_summarizer.embed_video_script()
     
st.header("TubeSummarizer")
st.markdown('#') 

st.markdown('#### I : YouTube Video URL')
video_link = st.text_input("URL :", placeholder="https://www.youtube.com/watch?v=************")

tube_summarizer = initailize_summarizer(video_link)

if tube_summarizer.is_valid_youtube_link(video_link):
    st.video(video_link)

    # with st.spinner("Extracting subtitles..."):
    subtitles = load_subtitles(video_link)

    if subtitles and len(subtitles) <= 20000:

        st.markdown('#### II. Subtitles')
        stx.scrollableTextbox(subtitles, height=200)

        st.markdown('#### III. Summarization / Q&A')
        choice = st.selectbox("Please choose an option :", ('Summarization', 'Q&A'))

        if choice == "Summarization":
            if st.button("Generate Summary"):

                # with st.spinner("Generating summary..."):
                summary = generate_summary(subtitles)

                stx.scrollableTextbox(summary, height=200)
        else:
            question = st.text_input("Question: ", placeholder="Type your question here")
            if st.button("Generate Answer"):
                embed_script(subtitles)
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
        st.error("Your video is too long, It's gonna cost too much :)")
else:
    if video_link != "":
        st.error("Please provide a valid YouTube video URL")