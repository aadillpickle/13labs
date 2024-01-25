from openai import OpenAI
from moviepy.editor import VideoFileClip
import requests
import os
import pathlib
from dotenv import load_dotenv
from upload import upload_to_aws, upload_link_file_to_aws

load_dotenv()

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def get_translated_video(media_url, language="hindi"):
    video_text = transcribe_video(media_url)
    translated_text = openai_translation(video_text, language)
    translated_audio = get_translated_audio(translated_text)
    sync_vid_to_audio(media_url, translated_audio)
    print("syncing queued")
    
    
def transcribe_video(media_url):
    print('hit transcribe video')
    video = VideoFileClip(media_url)
    audio = video.audio
    
    audio_file = "audio.mp3"
    audio.write_audiofile(audio_file)
    print(audio_file)
    audio_pathlike = pathlib.Path(audio_file)
    transcription = client.audio.transcriptions.create(model='whisper-1', file=audio_pathlike)
    print(transcription.text)
    return transcription.text

def get_translated_audio(translated_text):
    print('hit eleven labs function')
    print(translated_text)
    voice_id = "I6bbZwH7U4GilF6VIPzQ"
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}" #?optimize_streaming_latency=2

    headers = {
        "Content-Type": "application/json",
        "xi-api-key": os.environ.get("XI_API_KEY")
    }

    data = {
        "text": translated_text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75,
            "style": 0.13,
            "use_speaker_boost": True
        }
    }

    response = requests.post(url, json=data, headers=headers)
    audio_path = "generated_audio.mp3"

    with open(audio_path, 'wb') as f:
        f.write(response.content)
    
    print('got eleven labs response')
    return audio_path
    

def openai_translation(msg, language):
    print('hit openai translation')
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": f"You are an expert translator who speaks all languages witht he proficiency and tone of a native. You will receive a message in a language you do not understand. Your job is to translate the message into {language}."},
            {"role": "user", "content": f"Translate this into {language}: {msg}"}
        ]
    )
    resp = completion.choices[0].message.content
    print('got openai response')
    print(resp)
    return resp

def sync_vid_to_audio(original_video_url, generated_audio):
    api_url = "https://api.synclabs.so/video"
    
    audio_url = upload_to_aws(generated_audio, 'generated_audio.mp3')

    vid_url = upload_link_file_to_aws(original_video_url, 'generated_video.mp4')
    print('hit sync labs fxn')
    print(audio_url)
    print(vid_url)
    payload = {
        "audioUrl": audio_url,
        "videoUrl": vid_url,
        "synergize": False, #false if 10x speedup but lower quality
        "maxCredits": None,
        "webhookUrl": os.environ.get('NGROK_URL') + '/callback'
    }
    
    headers = {
        "Content-Type": "application/json",
        "x-api-key": os.environ.get('SYNC_LABS_API_KEY')
    }
    response = requests.post(api_url, json=payload, headers=headers)
    print(response.text)
    return response.text