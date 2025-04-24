import requests
import os
from backend.services.format_service import format_soap_note

def generate_formatted_notes(transcription):
    """Generate formatted medical notes using OpenRouter"""
    try:
        api_key = os.environ.get('OPENROUTER_API_KEY')
        model = os.environ.get('LLM_MODEL', 'anthropic/claude-3-opus-20240229')
        
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": """You are an AI medical scribe assistant. 
                    Your job is to convert doctor-patient conversation transcripts into properly formatted medical notes.
                    Focus on extracting clinical information and organizing it into standard SOAP format.
                    Be precise with medical terminology and include all relevant patient information."""
                },
                {
                    "role": "user",
                    "content": f"""Please convert the following doctor-patient conversation into a properly formatted SOAP note.
                    Extract all relevant medical information. Conversation transcript: {transcription}"""
                }
            ],
            "temperature": 0.2,
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
        
        response.raise_for_status()
        generated_text = response.json()['choices'][0]['message']['content']
        return format_soap_note(generated_text)
        
    except Exception as e:
        print(f"LLM API error: {str(e)}")
        raise Exception("Failed to generate medical notes")