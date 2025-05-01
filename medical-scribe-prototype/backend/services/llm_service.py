import requests
import os
from backend.services.format_service import format_soap_note, generate_formatted_notes_fallback

def generate_formatted_notes(transcription):
    """Generate formatted medical notes using OpenRouter with a specialized medical LLM"""
    try:
        api_key = os.environ.get('OPENROUTER_API_KEY')
        # Use OpenBioLLM model for better medical knowledge
        model = "saamaai/openbiollm-llama3-8b"  # 8B parameter version
        # Alternatively use: "saamaai/openbiollm-llama3-70b" for the larger model
        
        print(f"Generating SOAP notes using {model}...")
        
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": """You are an experienced medical scribe with years of training in clinical documentation.
                    
                    Your task is to convert this doctor-patient conversation into a comprehensive SOAP note.
                    
                    For proper SOAP format, include:
                    
                    Subjective:
                    - Begin with patient's chief complaint in quotes
                    - Document the history of present illness (onset, duration, severity, etc.)
                    - Note relevant past medical history, family history, and social history
                    - Include reported symptoms and patient experiences
                    
                    Objective: 
                    - Document vital signs if provided
                    - Include physical examination findings described by the doctor
                    - List any test results mentioned
                    - Note any observable measurements or clinical findings
                    
                    Assessment:
                    - Provide the doctor's diagnosis or differential diagnoses
                    - Explain clinical reasoning for diagnosis
                    - Note severity and stage of condition if mentioned
                    - Include any risk factors identified
                    
                    Plan:
                    - List all treatment recommendations including medications with specific dosages
                    - Include follow-up instructions
                    - Note any referrals to specialists
                    - Document patient education provided
                    - Include any lifestyle modifications recommended
                    
                    Use proper medical terminology, standard abbreviations, and be thorough but concise.
                    Format your response with clear section headers and bullet points where appropriate.
                    """
                },
                {
                    "role": "user",
                    "content": f"Please create a comprehensive SOAP note based on this doctor-patient conversation: {transcription}"
                }
            ],
            "temperature": 0.1,  # Low temperature for more consistent, factual output
            "max_tokens": 1500   # Allow longer responses for comprehensive notes
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
        
        # Enhanced error handling
        if response.status_code != 200:
            print(f"Notes API error: {response.status_code} - {response.text}")
            raise Exception(f"API returned error: {response.status_code}")
            
        response_data = response.json()
        
        if 'choices' not in response_data or len(response_data['choices']) == 0:
            print(f"Unexpected API response format: {response_data}")
            raise Exception("API response missing expected content")
            
        generated_text = response_data['choices'][0]['message']['content']
        return format_soap_note(generated_text)
        
    except Exception as e:
        print(f"LLM API error: {str(e)}")
        # Use fallback method if API fails
        return generate_formatted_notes_fallback(transcription)