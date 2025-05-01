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

# Add to backend/services/speech_service.py

def add_speaker_labels(transcription):
    """Add speaker labels to transcription using a lightweight LLM"""
    try:
        api_key = os.environ.get('OPENROUTER_API_KEY')
        model = "qwen/qwen3-4b:free"  # Smaller, faster model for this task
        
        print(f"Adding speaker labels using {model}...")
        
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": """You are a medical transcription specialist. 
                    Your task is to add 'Doctor:' and 'Patient:' labels to the beginning of each statement in a medical conversation.
                    Use contextual clues to determine who is speaking.
                    - Doctors typically introduce themselves as doctors, discuss treatments, give medical advice, and ask about symptoms
                    - Patients typically describe symptoms, answer questions, and respond to recommendations
                    Format the conversation with a new line for each speaker change."""
                },
                {
                    "role": "user",
                    "content": f"Add 'Doctor:' and 'Patient:' labels to this medical conversation transcript: {transcription}"
                }
            ],
            "temperature": 0.1,
            "max_tokens": 1000
        }
        
        headers = {
            'Authorization': f"Bearer {api_key}",
            'Content-Type': 'application/json'
        }
        
        response = requests.post(
            'https://openrouter.ai/api/v1/chat/completions',
            json=payload,
            headers=headers
        )
        
        if response.status_code != 200:
            print(f"Speaker labeling API error: {response.status_code} - {response.text}")
            return transcription
            
        labeled_text = response.json()['choices'][0]['message']['content']
        return labeled_text
        
    except Exception as e:
        print(f"Speaker labeling error: {str(e)}")
        return transcription  # Return original transcription if there's an error