
import statistics
from collections import Counter

def classify_heading_level(font_sizes):
    """
    Classify font sizes into heading levels (H1, H2, H3) based on frequency and size.
    Returns a mapping of font_size -> level
    """
    if not font_sizes:
        return {}
    
    # Remove duplicates and sort
    unique_sizes = sorted(set(font_sizes), reverse=True)
    
    # Count frequencies
    size_counts = Counter(font_sizes)
    
    # If we have very few unique sizes, handle specially
    if len(unique_sizes) <= 3:
        levels = {}
        level_names = ["H1", "H2", "H3"]
        for i, size in enumerate(unique_sizes):
            if i < len(level_names):
                levels[size] = level_names[i]
        return levels
    
    # For more sizes, use statistical approach
    # Sort by size (largest first) and frequency
    sorted_sizes = sorted(unique_sizes, key=lambda x: (-x, size_counts[x]), reverse=False)
    
    # Assign levels based on size hierarchy
    levels = {}
    level_names = ["H1", "H2", "H3"]
    
    # Take top 3 sizes as headings
    for i, size in enumerate(sorted_sizes[:3]):
        levels[size] = level_names[i]
    
    return levels

def clean_text(text):
    """Clean and normalize text content"""
    if not text:
        return ""
    
    # Remove extra whitespace and normalize
    cleaned = " ".join(text.split())
    return cleaned.strip()

def extract_title_from_outline(outline):
    """Extract a clean title from the outline"""
    if not outline:
        return ""
    
    # Look for the first meaningful H1
    for item in outline:
        if item.get("level") == "H1":
            text = clean_text(item.get("text", ""))
            # Skip very short or generic titles
            if len(text) > 3 and not text.lower() in ["overview", "introduction", "contents"]:
                return text
    
    # Fallback to first H1 if found
    for item in outline:
        if item.get("level") == "H1":
            return clean_text(item.get("text", ""))
    
    return ""
