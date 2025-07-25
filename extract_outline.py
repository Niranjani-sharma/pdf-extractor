
import fitz  # PyMuPDF
import os
import json
from utils import classify_heading_level, clean_text, extract_title_from_outline, is_likely_heading

def extract_outline_from_pdf(filepath):
    doc = fitz.open(filepath)
    headings = []
    all_font_sizes = []

    # First pass: collect all font sizes to calculate average
    for page_index in range(len(doc)):
        page = doc[page_index]
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if "lines" not in block:
                continue
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    text = span["text"].strip()
                    if text:
                        size = round(span["size"], 2)
                        all_font_sizes.append(size)

    # Calculate average font size
    avg_font_size = sum(all_font_sizes) / len(all_font_sizes) if all_font_sizes else 12

    # Second pass: collect headings by consolidating text on same lines
    for page_index in range(len(doc)):
        page = doc[page_index]
        page_number = page_index

        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if "lines" not in block:
                continue

            for line in block.get("lines", []):
                # Consolidate all spans in a line that have similar font sizes
                line_texts = []
                line_sizes = []
                
                for span in line.get("spans", []):
                    text = span["text"].strip()
                    if text:
                        size = round(span["size"], 2)
                        line_texts.append(text)
                        line_sizes.append(size)
                
                if not line_texts:
                    continue
                
                # Use the most common or largest font size in the line
                if line_sizes:
                    # Use the largest font size in the line (headings are typically larger)
                    max_size = max(line_sizes)
                    # Combine all text in the line
                    combined_text = " ".join(line_texts).strip()
                    
                    # Check if this line could be a heading
                    if is_likely_heading(combined_text, max_size, avg_font_size):
                        headings.append({
                            "text": clean_text(combined_text),
                            "size": max_size,
                            "page": page_number
                        })

    # Remove duplicate headings that might appear from overlapping text
    unique_headings = []
    seen_texts = set()
    
    for heading in headings:
        text_key = (heading["text"].lower().strip(), heading["page"])
        if text_key not in seen_texts and heading["text"]:
            seen_texts.add(text_key)
            unique_headings.append(heading)

    # Map font sizes to heading levels
    font_sizes = [h["size"] for h in unique_headings]
    levels = classify_heading_level(font_sizes)

    outline = []
    for item in unique_headings:
        level = levels.get(item["size"])
        if level and item["text"]:
            outline.append({
                "level": level,
                "text": item["text"],
                "page": item["page"]
            })

    # Extract title using improved logic
    title = extract_title_from_outline(outline)

    return {
        "title": title,
        "outline": outline
    }

if __name__ == "__main__":
    input_dir = "input"
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(input_dir):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(input_dir, filename)
            result = extract_outline_from_pdf(pdf_path)

            output_filename = filename.replace(".pdf", ".json")
            output_path = os.path.join(output_dir, output_filename)
            with open(output_path, "w", encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

    print("✅ All PDFs processed.")
