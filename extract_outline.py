
import fitz  # PyMuPDF
import os
import json
from utils import classify_heading_level, clean_text, extract_title_from_outline

def extract_outline_from_pdf(filepath):
    doc = fitz.open(filepath)
    headings = []
    font_sizes = []

    for page_index in range(len(doc)):
        page = doc[page_index]
        page_number = page_index  # 0-indexed as expected in sample outputs

        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if "lines" not in block:
                continue
                
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    text = span["text"].strip()
                    if not text:
                        continue

                    # Skip very short texts that are likely not headings
                    if len(text) < 2:
                        continue

                    size = round(span["size"], 2)
                    font_sizes.append(size)
                    headings.append({
                        "text": clean_text(text),
                        "size": size,
                        "page": page_number
                    })

    # Map font sizes to heading levels
    levels = classify_heading_level(font_sizes)

    outline = []
    for item in headings:
        level = levels.get(item["size"])
        if level and item["text"]:  # Only add if we have a level and non-empty text
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
            with open(output_path, "w") as f:
                json.dump(result, f, indent=2)

    print("✅ All PDFs processed.")
