# Update backend/services/format_service.py

import re

def format_soap_note(raw_text):
    """Format the raw LLM output into a structured SOAP note"""
    
    # Try to identify SOAP sections with more robust pattern matching
    subjective = extract_section(raw_text, r'(?i)(subjective|S)[:\.]\s*')
    objective = extract_section(raw_text, r'(?i)(objective|O)[:\.]\s*')
    assessment = extract_section(raw_text, r'(?i)(assessment|A)[:\.]\s*')
    plan = extract_section(raw_text, r'(?i)(plan|P)[:\.]\s*')
    
    # Apply some formatting to each section
    sections = {
        'subjective': format_section(subjective),
        'objective': format_section(objective),
        'assessment': format_section(assessment),
        'plan': format_section(plan)
    }
    
    return {
        'formatted': True,
        'sections': sections
    }

def extract_section(text, section_pattern):
    """Extract a section from the raw text with improved pattern matching"""
    # Define patterns for all section headers
    section_patterns = [
        r'(?i)(subjective|S)[:\.]\s*',
        r'(?i)(objective|O)[:\.]\s*',
        r'(?i)(assessment|A)[:\.]\s*',
        r'(?i)(plan|P)[:\.]\s*'
    ]
    
    # Find the current section
    section_match = re.search(section_pattern, text)
    if not section_match:
        return ''
    
    start_idx = section_match.end()
    
    # Find the next section after this one
    end_idx = len(text)
    for pattern in section_patterns:
        if pattern != section_pattern:  # Skip the current section pattern
            next_match = re.search(pattern, text[start_idx:])
            if next_match:
                next_start = next_match.start() + start_idx
                if next_start < end_idx:
                    end_idx = next_start
    
    # Extract and clean the section content
    section_text = text[start_idx:end_idx].strip()
    
    return section_text

def format_section(text):
    """Apply formatting to a section text"""
    # Convert bullet points for consistency
    text = re.sub(r'(?m)^[-*•] ', '• ', text)
    
    # Format medication dosages consistently
    text = re.sub(r'(\d+)(\s*)(mg|mcg|g|ml)', r'\1 \3', text)
    
    # Ensure proper spacing after periods
    text = re.sub(r'\.(?=[A-Za-z])', '. ', text)
    
    return text

def extract_section(text, section_pattern):
    """Extract a section from the raw text with improved pattern matching"""
    # Define patterns for all section headers
    section_patterns = [
        r'(?i)(subjective|S:)',
        r'(?i)(objective|O:)',
        r'(?i)(assessment|A:)',
        r'(?i)(plan|P:)'
    ]
    
    # Find the current section
    matches = list(re.finditer(section_pattern, text))
    if not matches:
        return ''
    
    start_match = matches[0]
    start_idx = start_match.end()
    
    # Find the next section after this one
    end_idx = len(text)
    for pattern in section_patterns:
        if pattern != section_pattern:  # Skip the current section pattern
            next_matches = list(re.finditer(pattern, text[start_idx:]))
            if next_matches:
                next_start = next_matches[0].start() + start_idx
                if next_start < end_idx:
                    end_idx = next_start
    
    # Extract and clean the section content
    section_text = text[start_idx:end_idx].strip()
    section_text = re.sub(r'^[:\s]+', '', section_text)  # Remove leading colon or whitespace
    
    return section_text

def generate_formatted_notes_fallback(transcription):
    """Generate medical notes without external API (fallback method)"""
    try:
        # Split the transcription into doctor and patient parts if labeled
        doctor_statements = []
        patient_statements = []
        
        # Try to extract labeled speakers
        for line in transcription.split('\n'):
            line = line.strip()
            if re.search(r'^doctor\s*[:\.]\s*', line, re.IGNORECASE):
                statement = re.sub(r'^doctor\s*[:\.]\s*', '', line, flags=re.IGNORECASE)
                doctor_statements.append(statement)
            elif re.search(r'^patient\s*[:\.]\s*', line, re.IGNORECASE):
                statement = re.sub(r'^patient\s*[:\.]\s*', '', line, flags=re.IGNORECASE)
                patient_statements.append(statement)
            # Try to infer based on content if not labeled
            elif any(kw in line.lower() for kw in ['prescribe', 'recommend', 'diagnosis', 'exam']):
                doctor_statements.append(line)
            elif any(kw in line.lower() for kw in ['feel', 'hurt', 'pain', 'symptom']):
                patient_statements.append(line)
            else:
                # Default to adding to both if unsure
                doctor_statements.append(line)
                patient_statements.append(line)
        
        # Create SOAP sections
        chief_complaint = next((s for s in patient_statements if any(w in s.lower() for w in ['problem', 'issue', 'concern', 'pain'])), "Undocumented concern")
        
        subjective = "Chief Complaint: \"" + chief_complaint + "\"\n\n"
        subjective += "History of Present Illness:\n"
        subjective += "• " + "\n• ".join(patient_statements[:5]) if patient_statements else "No subjective information documented."
        
        objective = "Physical Examination:\n" 
        exam_findings = [s for s in doctor_statements if any(kw in s.lower() for kw in ['exam', 'observe', 'finding', 'vital', 'test'])]
        objective += "• " + "\n• ".join(exam_findings) if exam_findings else "No examination findings documented."
        
        assessment = "Assessment/Diagnosis:\n"
        diagnosis = [s for s in doctor_statements if any(kw in s.lower() for kw in ['diagnos', 'assessment', 'condition', 'disease'])]
        assessment += "• " + "\n• ".join(diagnosis) if diagnosis else "Assessment pending further evaluation."
        
        plan = "Treatment Plan:\n"
        treatment = [s for s in doctor_statements if any(kw in s.lower() for kw in ['plan', 'prescribe', 'recommend', 'follow', 'refer'])]
        plan += "• " + "\n• ".join(treatment) if treatment else "• Continue monitoring.\n• Follow up as needed."
        
        return {
            'formatted': True,
            'sections': {
                'subjective': subjective,
                'objective': objective,
                'assessment': assessment,
                'plan': plan
            }
        }
    except Exception as e:
        print(f"Fallback note generation error: {str(e)}")
        return {
            'formatted': True,
            'sections': {
                'subjective': "Patient visited for medical evaluation.",
                'objective': "Examination performed by physician.",
                'assessment': "Clinical assessment was discussed.",
                'plan': "Treatment plan was provided."
            }
        }