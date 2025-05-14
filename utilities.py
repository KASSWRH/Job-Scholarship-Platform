import os
import re
from datetime import datetime
from flask import current_app

def allowed_file(filename):
    """Check if a file has an allowed extension."""
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt', 'rtf'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_unique_filename(original_filename, user_id=None):
    """Generate a unique filename by adding timestamp and user_id if provided."""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    
    # Get file extension
    _, ext = os.path.splitext(original_filename)
    
    # Generate a clean base name (remove special chars)
    base_name = re.sub(r'[^\w\s-]', '', original_filename.rsplit('.', 1)[0])
    base_name = re.sub(r'[-\s]+', '-', base_name).strip('-_')
    
    # Create unique filename
    if user_id:
        unique_name = f"{user_id}_{timestamp}_{base_name}{ext}"
    else:
        unique_name = f"{timestamp}_{base_name}{ext}"
        
    return unique_name

def get_file_size_human_readable(file_path):
    """Convert file size to human readable format (KB, MB, etc.)."""
    size_bytes = os.path.getsize(file_path)
    
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024 or unit == 'GB':
            break
        size_bytes /= 1024
        
    return f"{size_bytes:.2f} {unit}"

def parse_date(date_str):
    """Parse date string into a datetime object."""
    date_formats = [
        '%Y-%m-%d',
        '%d/%m/%Y',
        '%m/%d/%Y',
        '%d-%m-%Y',
        '%m-%d-%Y'
    ]
    
    for fmt in date_formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
            
    # If no format matches, return None
    return None

def clean_html(text):
    """Remove HTML tags from text."""
    if not text:
        return ''
    return re.sub(r'<[^>]*>', '', text)

def extract_keywords(text, max_keywords=5):
    """Extract important keywords from text."""
    if not text:
        return []
        
    # Remove common words
    common_words = {
        'the', 'and', 'a', 'to', 'of', 'in', 'is', 'are', 'for', 'with', 'on', 'at',
        'an', 'by', 'this', 'that', 'from', 'as', 'be', 'or', 'not', 'we', 'you', 'it',
        'have', 'has', 'had', 'our', 'their', 'your', 'will', 'would', 'can', 'could'
    }
    
    # Tokenize text
    words = re.findall(r'\b\w+\b', text.lower())
    
    # Remove common words and count frequency
    word_counts = {}
    for word in words:
        if word not in common_words and len(word) > 2:
            word_counts[word] = word_counts.get(word, 0) + 1
            
    # Sort by frequency
    sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
    
    # Return top keywords
    return [word for word, _ in sorted_words[:max_keywords]]

def validate_arabic_text(text):
    """Check if text contains Arabic characters."""
    arabic_pattern = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]+')
    return bool(arabic_pattern.search(text))

def detect_text_direction(text):
    """Detect text direction (RTL or LTR) based on content."""
    if validate_arabic_text(text):
        return 'rtl'
    return 'ltr'
