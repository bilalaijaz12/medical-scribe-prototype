from flask import Blueprint, request, jsonify
import os
import tempfile
from backend.services.speech_service import transcribe_audio
from backend.services.llm_service import generate_formatted_notes

api_bp = Blueprint('api', __name__)

@api_bp.route('/transcribe', methods=['POST'])
def process_transcription():
    """Process audio for transcription"""
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        
        audio_file = request.files['audio']
        
        # Save to temporary file
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, 'temp_audio.webm')
        audio_file.save(temp_path)
        
        # Transcribe audio
        transcription = transcribe_audio(temp_path)
        
        # Clean up temporary file
        os.remove(temp_path)
        
        return jsonify({'transcription': transcription})
    
    except Exception as e:
        print(f"Transcription error: {str(e)}")
        return jsonify({'error': 'Failed to process transcription'}), 500


@api_bp.route('/generate-notes', methods=['POST'])
def generate_medical_notes():
    """Generate structured medical notes from transcription"""
    try:
        data = request.json
        transcription = data.get('transcription')
        
        if not transcription:
            return jsonify({'error': 'No transcription provided'}), 400
        
        formatted_notes = generate_formatted_notes(transcription)
        
        return jsonify({'notes': formatted_notes})
    
    except Exception as e:
        print(f"Note generation error: {str(e)}")
        return jsonify({'error': 'Failed to generate medical notes'}), 500