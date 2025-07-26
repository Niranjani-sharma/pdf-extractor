
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
    
    # Remove trailing dots and colons that might be artifacts
    text = re.sub(r'[:\.\s]+$', '', text)
    
    # Remove leading/trailing punctuation
    text = text.strip('.,;:!?-_')

    return text.strip()

def classify_heading_level(font_sizes):
    """Classify font sizes into heading levels"""
    if not font_sizes:
        return {}

    # Get unique font sizes and sort them
    unique_sizes = sorted(set(font_sizes), reverse=True)

    # Count occurrences of each size
    size_counts = Counter(font_sizes)

    # Filter out sizes that appear too frequently (likely body text)
    # Keep sizes that appear 1-20 times (typical for headings)
    potential_heading_sizes = []
    for size in unique_sizes:
        count = size_counts[size]
        if 1 <= count <= 20:
            potential_heading_sizes.append(size)

    # If we have too few potential heading sizes, relax the criteria
    if len(potential_heading_sizes) < 2:
        potential_heading_sizes = unique_sizes[:4]  # Take top 4 sizes

    # Map sizes to heading levels (H1, H2, H3, H4)
    level_mapping = {}
    for i, size in enumerate(potential_heading_sizes[:4]):
        level_mapping[size] = f"H{i + 1}"

    return level_mapping

def extract_title_from_outline(outline):
    """Extract title from outline - prioritize actual document content"""
    if not outline:
        return ""

    # Look for the first meaningful H1 heading, or the largest text
    best_title = ""

    for item in outline:
        text = item.get("text", "").strip()
        level = item.get("level", "")

        # Skip obvious non-titles
        if not text or len(text) < 3:
            continue
        if re.match(r'^[-\s•\*\+]+$', text):
            continue
        if text.lower() in ['table of contents', 'contents', 'index', 'page']:
            continue

        # Prioritize H1 headings that look like titles
        if level == "H1":
            # If it's a reasonable length and not obviously a section header
            if 3 <= len(text) <= 200:
                return text

        # Keep track of the first reasonable heading if no good H1 found
        if not best_title and len(text) >= 3:
            best_title = text

    return best_title

def is_likely_heading(text, size, avg_font_size):
    """
    Returns True if a line is likely to be a heading.
    Combines font size + text length + structure.
    """
    text = text.strip()

    # Must be longer than a few characters
    if len(text) < 3:
        return False

    # Must not be mostly numbers or special characters
    alpha_ratio = len(re.findall(r"[A-Za-z]", text)) / len(text) if text else 0
    if alpha_ratio < 0.3:
        return False

    # Avoid lines with excessive repetition
    words = text.lower().split()
    if len(words) > 0:
        unique_ratio = len(set(words)) / len(words)
        if unique_ratio < 0.4:
            return False

    # Filter obvious junk (repeated chars)
    if re.search(r"(.)\1{4,}", text):  # e.g., "aaaaa", "ppppp"
        return False

    # Must be reasonably larger than average font
    if size < avg_font_size + 1:
        return False

    return True
