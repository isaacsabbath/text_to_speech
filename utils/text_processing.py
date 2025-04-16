import re

def clean_text(text):
    """
    Clean and prepare text for text-to-speech conversion
    """
    # Remove excess whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Replace common abbreviations
    abbreviations = {
        'Dr.': 'Doctor',
        'Mr.': 'Mister',
        'Mrs.': 'Misses',
        'Ms.': 'Miss',
        'Prof.': 'Professor',
        'e.g.': 'for example',
        'i.e.': 'that is',
        'etc.': 'etcetera',
    }
    
    for abbr, full in abbreviations.items():
        text = text.replace(abbr, full)
    
    # Handle number formatting
    text = re.sub(r'(\d+)\.(\d+)', r'\1 point \2', text)  # Convert decimal points
    
    # Handle common symbols
    symbols = {
        '&': 'and',
        '@': 'at',
        '%': 'percent',
        '+': 'plus',
        '=': 'equals',
        '#': 'number',
    }
    
    for symbol, word in symbols.items():
        text = text.replace(symbol, f' {word} ')
    
    # Clean up any resulting double spaces
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def chunk_text(text, max_chars=5000):
    """
    Split long text into manageable chunks for TTS processing.
    Try to split at sentence boundaries when possible.
    """
    # If text is short enough, return it as is
    if len(text) <= max_chars:
        return [text]
    
    chunks = []
    sentences = re.split(r'(?<=[.!?])\s+', text)
    current_chunk = ""
    
    for sentence in sentences:
        # If a single sentence is too long, split it by comma
        if len(sentence) > max_chars:
            comma_parts = sentence.split(', ')
            temp_chunk = ""
            
            for part in comma_parts:
                if len(temp_chunk) + len(part) + 2 <= max_chars:
                    if temp_chunk:
                        temp_chunk += ", " + part
                    else:
                        temp_chunk = part
                else:
                    if temp_chunk:
                        chunks.append(temp_chunk)
                    
                    # If a comma part is still too long, just split it arbitrarily
                    if len(part) > max_chars:
                        for i in range(0, len(part), max_chars):
                            chunks.append(part[i:i+max_chars])
                    else:
                        temp_chunk = part
            
            if temp_chunk:
                chunks.append(temp_chunk)
        
        # Normal case: sentence can fit in current chunk
        elif len(current_chunk) + len(sentence) + 1 <= max_chars:
            if current_chunk:
                current_chunk += " " + sentence
            else:
                current_chunk = sentence
        
        # Start a new chunk if adding this sentence would exceed max_chars
        else:
            chunks.append(current_chunk)
            current_chunk = sentence
    
    # Add the last chunk if it's not empty
    if current_chunk:
        chunks.append(current_chunk)
    
    return chunks