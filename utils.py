
import re
from collections import Counter

def clean_text(text):
    """Clean and normalize text"""
    if not text:
        return ""
    
    # Remove extra whitespace and normalize
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove common artifacts
    text = re.sub(r'^[-\s]+$', '', text)  # Lines with only dashes/spaces
    text = re.sub(r'^[•\-\*\+]+\s*', '', text)  # Bullet points
    
    return text

def classify_heading_level(font_sizes):
    """Classify font sizes into heading levels"""
    if not font_sizes:
        return {}
    
    # Get unique font sizes and sort them
    unique_sizes = sorted(set(font_sizes), reverse=True)
    
    # Only consider sizes that appear frequently enough to be headings
    size_counts = Counter(font_sizes)
    
    # Filter out sizes that appear too frequently (likely body text)
    # or too rarely (likely artifacts)
    potential_heading_sizes = []
    for size in unique_sizes:
        count = size_counts[size]
        # Headings typically appear 1-20 times, body text appears much more
        if 1 <= count <= 20:
            potential_heading_sizes.append(size)
    
    # Take top 3 sizes as H1, H2, H3
    level_mapping = {}
    for i, size in enumerate(potential_heading_sizes[:3]):
        level_mapping[size] = f"H{i + 1}"
    
    return level_mapping

def extract_title_from_outline(outline):
    """Extract title from outline - prioritize actual document content"""
    if not outline:
        return ""
    
    # Look for meaningful titles (not artifacts like dashes)
    for item in outline:
        text = item.get("text", "").strip()
        
        # Skip obvious non-titles
        if not text or len(text) < 3:
            continue
        if re.match(r'^[-\s•\*\+]+$', text):
            continue
        if text.upper() == text and len(text) < 50:  # All caps short text might be title
            return text
        if item.get("level") == "H1" and len(text) > 5:
            return text
    
    return ""

def is_likely_heading(text, font_size, avg_font_size):
    """Determine if text is likely a heading"""
    if not text or len(text.strip()) < 2:
        return False
    
    text = text.strip()
    
    # Skip obvious non-headings
    if len(text) < 3:
        return False
    if re.match(r'^[\d\.\s]+$', text):  # Just numbers/dots
        return False
    if re.match(r'^[-\s•\*\+]+$', text):  # Just punctuation
        return False
    if text in ['To', 'Y', 'ou', 'T', '!', 'Rs.']:  # Common artifacts
        return False
    
    # Check font size (headings are typically larger)
    if font_size <= avg_font_size:
        return False
    
    # Check length (headings are typically not too long)
    if len(text) > 200:
        return False
    
    return True
