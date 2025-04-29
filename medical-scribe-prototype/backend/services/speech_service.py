import requests
import os
import subprocess
import tempfile

def transcribe_audio(audio_path):
    """Transcribe audio using OpenAI's Transcription API"""
    try:
        print(f"Attempting to transcribe audio from: {audio_path}")
        
        # Convert to mp3 (more widely supported)
        temp_mp3 = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False).name
        try:
            # Using ffmpeg to convert to mp3
            subprocess.run(['ffmpeg', '-i', audio_path, '-vn', '-ar', '44100', 
                          '-ac', '2', '-b:a', '192k', temp_mp3], check=True)
            audio_path = temp_mp3
        except Exception as e:
            print(f"Conversion error: {str(e)}")
            # Continue with original file if conversion fails
        
        with open(audio_path, 'rb') as audio_file:
            headers = {
                'Authorization': f"Bearer {os.environ.get('OPENAI_API_KEY')}"
            }
            
            files = {
                'file': ('audio.mp3', audio_file, 'audio/mpeg'),
                'model': (None, 'gpt-4o-mini-transcribe')
            }
            
            print("Sending request to OpenAI API...")
            response = requests.post(
                'https://api.openai.com/v1/audio/transcriptions',
                headers=headers,
                files=files
            )
            
            if response.status_code != 200:
                print(f"API Error: {response.status_code} - {response.text}")
                raise Exception(f"API Error: {response.status_code} - {response.text}")
            
            return response.json().get('text', '')
            
    except Exception as e:
        print(f"Transcription API error: {str(e)}")
        raise Exception("Failed to transcribe audio")
    finally:
        # Clean up temp files
        if 'temp_mp3' in locals() and os.path.exists(temp_mp3):
            os.remove(temp_mp3)