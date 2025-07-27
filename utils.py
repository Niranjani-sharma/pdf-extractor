import re
from collections import Counter

def clean_text(text):
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text.strip())
    text = re.sub(r'^[-\s]+$', '', text)
    text = re.sub(r'^[\u2022\-\*\+]+\s*', '', text)
    text = re.sub(r'[:\.\s]+$', '', text)
    text = text.strip('.,;:!?-_')
    return text.strip()

def classify_heading_level(font_sizes):
    if not font_sizes:
        return {}
    unique_sizes = sorted(set(font_sizes), reverse=True)
    size_counts = Counter(font_sizes)
    potential_heading_sizes = [s for s in unique_sizes if 1 <= size_counts[s] <= 20]
    if len(potential_heading_sizes) < 2:
        potential_heading_sizes = unique_sizes[:4]
    return {size: f"H{i+1}" for i, size in enumerate(potential_heading_sizes[:4])}

def extract_title_from_outline(outline):
    if not outline:
        return ""
    for item in outline:
        text = item.get("text", "").strip()
        level = item.get("level", "")
        if not text or len(text) < 3:
            continue
        if re.match(r'^[-\s\u2022\*\+]+$', text):
            continue
        if text.lower() in ['table of contents', 'contents', 'index', 'page']:
            continue
        if level == "H1" and 3 <= len(text) <= 200:
            return text
    for item in outline:
        if len(item.get("text", "")) >= 3:
            return item["text"]
    return ""

def is_likely_heading(text, size, avg_font_size):
    text = text.strip()
    if len(text) < 3:
        return False
    alpha_ratio = len(re.findall(r"[A-Za-z]", text)) / len(text) if text else 0
    if alpha_ratio < 0.3:
        return False
    words = text.lower().split()
    if len(words) > 0:
        unique_ratio = len(set(words)) / len(words)
        if unique_ratio < 0.4:
            return False
    if re.search(r"(.)\1{4,}", text):
        return False
    return size >= avg_font_size + 1
