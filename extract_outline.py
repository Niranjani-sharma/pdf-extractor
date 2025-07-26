import fitz  # PyMuPDF
import os
import json
from collections import defaultdict
from utils import (
    classify_heading_level,
    clean_text,
    extract_title_from_outline,
    is_likely_heading
)

def group_spans_into_lines(page, y_tolerance=1.5):
    """
    Groups spans by Y-position (same line) and sorts by X (left to right).
    Returns a list of dicts: [{ text, size }]
    """
    line_map = defaultdict(list)

    for block in page.get_text("dict")["blocks"]:
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                text = span["text"].strip()
                if not text:
                    continue
                y = round(span["bbox"][1] / y_tolerance) * y_tolerance
                line_map[y].append({
                    "text": text,
                    "x0": span["bbox"][0],
                    "size": round(span["size"], 2)
                })

    lines = []
    for y, spans in line_map.items():
        spans.sort(key=lambda s: s["x0"])  # Left to right
        merged_text = " ".join(s["text"] for s in spans).strip()
        max_size = max(s["size"] for s in spans)
        lines.append({
            "text": merged_text,
            "size": max_size
        })

    return lines

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

    avg_font_size = sum(all_font_sizes) / len(all_font_sizes) if all_font_sizes else 12

    # Second pass: group spans into lines and extract headings
    for page_index in range(len(doc)):
        page = doc[page_index]
        page_number = page_index

        lines = group_spans_into_lines(page)

        for line in lines:
            text = line["text"]
            size = line["size"]

            if not text:
                continue

            if is_likely_heading(text, size, avg_font_size):
                headings.append({
                    "text": clean_text(text),
                    "size": size,
                    "page": page_number
                })

    # De-duplicate
    unique_headings = []
    seen = set()

    for h in headings:
        key = (h["text"].lower().strip(), h["page"])
        if key not in seen:
            seen.add(key)
            unique_headings.append(h)

    # Classify heading levels
    font_sizes = [h["size"] for h in unique_headings]
    levels = classify_heading_level(font_sizes)

    outline = []
    for h in unique_headings:
        level = levels.get(h["size"])
        if level:
            outline.append({
                "level": level,
                "text": h["text"],
                "page": h["page"]
            })

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

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

    print("✅ All PDFs processed.")
