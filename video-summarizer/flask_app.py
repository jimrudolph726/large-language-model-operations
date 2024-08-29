import os
import ctypes
import platform

# Manually set the libc_name for Windows
if platform.system() == "Windows":
    libc_name = "msvcrt.dll"  # This is the standard C library on Windows
else:
    # Original logic for other platforms
    libc_name = ctypes.util.find_library("c")

libc = ctypes.CDLL(libc_name)

# Now import whisper and other necessary libraries
import whisper
from flask import Flask, request, jsonify
from moviepy.editor import VideoFileClip
import openai
from openai import OpenAI

os.environ["OPENAI_API_KEY"] = ""
openai.api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI()

system_prompt = "You are a proficient AI with a specialty in distilling information into key points. Based on the following text, identify and list the main points that were discussed or brought up. These should be the most important ideas, findings, or topics that are crucial to the essence of the discussion. Your goal is to provide a list that someone could read to quickly understand what was talked about."

app = Flask(__name__)

def extract_audio(video_path, audio_path):
    video = VideoFileClip(video_path)
    video.audio.write_audiofile(audio_path, codec='mp3')

def transcribe_audio(audio_file):
    transcription = client.audio.transcriptions.create(
    model = 'whisper-1',
    file = audio_file,
    )
    return transcription

def generate_summary(transcription,system_prompt):
    response = client.chat.completions.create(
        model="gpt-4",
        temperature=0.5,
        messages=[
                    {"role": "system","content": system_prompt},
                    {"role": "user","content": transcription.text}
                ]
        )

    return response

@app.route('/transcribe_and_summarize', methods=['POST'])
def transcribe_and_summarize():
    video_file = request.files['video']
    video_path = 'uploaded_video.mp4'
    audio_path = 'extracted_audio.wav'
    video_file.save(video_path)
    
    extract_audio(video_path, audio_path)
    audio_file =  open(audio_path, 'rb')
    transcription = transcribe_audio(audio_file)
    response = generate_summary(transcription, system_prompt)
    
    with open('transcription.txt', 'w') as f:
        f.write(transcription.text)
        
    return jsonify({'transcription': transcription.text[:500], 'summary': response.choices[0].message.content})

if __name__ == '__main__':
    app.run(debug=True)
