import streamlit as st
import requests

st.title("Video Transcription and Summarization")

uploaded_file = st.file_uploader("Upload a Video", type=["mp4", "avi", "mov"])

if uploaded_file is not None:
    video_path = "uploaded_video.mp4"
    with open(video_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    files = {'video': open(video_path, 'rb')}
    response = requests.post("http://localhost:5000/transcribe_and_summarize", files=files)
    
    if response.status_code == 200:
        result = response.json()
        st.write("Transcription:")
        st.text(result['transcription'])
        st.write("Summary:")
        st.text(result['summary'])
    else:
        st.error("Error in processing the video.")
