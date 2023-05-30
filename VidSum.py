
from youtube_transcript_api import YouTubeTranscriptApi
from pytube import extract, YouTube
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chat_models import ChatOpenAI
import os
from dotenv import load_dotenv
from langchain.chains.summarize import load_summarize_chain
from langchain.callbacks import get_openai_callback
from langchain.vectorstores.faiss import FAISS
from langchain.chains import RetrievalQA
from langchain.embeddings import OpenAIEmbeddings
import requests

class VidSum:
    
    def __init__(self) :
        load_dotenv()
       
    def is_valid_youtube_link(self, video_link):
        try:
            request = requests.get(video_link, allow_redirects=False)
        except:
            return False
        return request.status_code == 200
    
    
    def load_video_script(self, video_link):
        try:
            id = extract.video_id(video_link)
            transcript = YouTubeTranscriptApi.get_transcript(id, languages=('en','fr'))
            
            video_script = ""

            for text in transcript:
                t = text["text"]
                if t != '[Music]':
                    video_script += t + " "
                
            self.video_script = video_script   
        except:
            self.video_script = ""
            
        return self.video_script 
    
    
    def summarize_video(self):
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=2048, chunk_overlap=50)
        self.summarization_docs = text_splitter.create_documents([self.video_script])
        
        llm = ChatOpenAI(
            temperature=0,
            model_name="gpt-3.5-turbo",
            openai_organization=os.environ.get("OPENAI_API_ORGANIZATION"),
            openai_api_key=os.environ.get("OPENAI_API_KEY")
            )
        
        chain = load_summarize_chain(llm=llm, chain_type="map_reduce")
        
        with get_openai_callback() as cb:
            self.video_summarization = chain.run(self.summarization_docs)
            print("Price: ", cb)
            
        return self.video_summarization
                
                
    def embed_video_script(self):
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=50)
        self.chat_docs = text_splitter.create_documents([self.video_script])
        
        embedding_model = OpenAIEmbeddings(
                                            openai_organization=os.environ.get("OPENAI_API_ORGANIZATION"),
                                            openai_api_key=os.environ.get("OPENAI_API_KEY")
                                        )
        
        vector_store = FAISS.from_documents(self.chat_docs, embedding_model)
        
        llm = ChatOpenAI(
            temperature=0,
            model_name="gpt-3.5-turbo",
            openai_organization=os.environ.get("OPENAI_API_ORGANIZATION"),
            openai_api_key=os.environ.get("OPENAI_API_KEY")
            )
        
        self.chain = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=vector_store.as_retriever())
        
        
    def chat_video(self, question):
        answer = self.chain.run(question)  
        return answer