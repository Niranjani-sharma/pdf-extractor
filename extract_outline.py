import fitz  # PyMuPDF
import os
import json
from utils import classify_heading_level

def extract_outline_from_pdf(filepath):
    doc = fitz.open(filepath)
    headings = []
    font_sizes = []

    for page_index in range(len(doc)):
        page = doc[page_index]
        page_number = page_index + 1  # To ensure pages are 1-indexed

        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    text = span["text"].strip()
                    if not text:
                        continue

                    size = round(span["size"], 2)
                    font_sizes.append(size)
                    headings.append({
                        "text": text,
                        "size": size,
                        "page": page_number
                    })

    # Map font sizes to heading levels
    levels = classify_heading_level(font_sizes)

    outline = []
    for item in headings:
        level = levels.get(item["size"])
        if level:
            outline.append({
                "level": level,
                "text": item["text"],
                "page": item["page"]
            })

    # Title is the first H1 found, or empty
    title = next((h["text"] for h in outline if h["level"] == "H1"), "")

    return {
        "title": title,
        "outline": outline
    }

# Optional: standalone test (commented out for Docker use)
# if __name__ == "__main__":
#     output = extract_outline_from_pdf("sample.pdf")
#     with open("output.json", "w") as f:
#         json.dump(output, f, indent=2)
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
