import re

def format_soap_note(raw_text):
    """Format the raw LLM output into a structured SOAP note"""
    # For the prototype, we'll do minimal formatting
    # In a production system, this would be more sophisticated
    
    # Try to identify SOAP sections
    sections = {
        'subjective': extract_section(raw_text, 'Subjective', 'Objective'),
        'objective': extract_section(raw_text, 'Objective', 'Assessment'),
        'assessment': extract_section(raw_text, 'Assessment', 'Plan'),
        'plan': extract_section(raw_text, 'Plan', None)
    }
    
    return {
        'formatted': True,
        'sections': sections
    }

def extract_section(text, section_name, next_section_name):
    """Helper to extract sections from the raw text"""
    start_pattern = re.compile(f"{section_name}[\\s\\n:]*", re.IGNORECASE)
    end_pattern = re.compile(f"{next_section_name}[\\s\\n:]*", re.IGNORECASE) if next_section_name else None
    
    start_match = start_pattern.search(text)
    if not start_match:
        return ''
    
    start_idx = start_match.end()
    end_idx = len(text)
    
    if end_pattern:
        end_match = end_pattern.search(text[start_idx:])
        if end_match:
            end_idx = start_idx + end_match.start()
    
    return text[start_idx:end_idx].strip()