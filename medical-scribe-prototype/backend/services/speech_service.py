import requests
import os
import base64

def transcribe_audio(audio_path):
    """Transcribe audio using OpenAI's Whisper API"""
    try:
        with open(audio_path, 'rb') as audio_file:
            headers = {
                'Authorization': f"Bearer {os.environ.get('OPENAI_API_KEY')}"
            }
            
            files = {
                'file': ('audio.webm', audio_file, 'audio/webm'),
                'model': (None, 'whisper-1')
            }
            
            response = requests.post(
                'https://api.openai.com/v1/audio/transcriptions',
                headers=headers,
                files=files
            )
            
            response.raise_for_status()
            return response.json().get('text', '')
            
    except Exception as e:
        print(f"Transcription API error: {str(e)}")
        raise Exception("Failed to transcribe audio")