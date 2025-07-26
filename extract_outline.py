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
from ml_classifier import MLHeadingClassifier

def extract_outline_from_pdf(filepath):
    """Extract outline from PDF using ML classification."""
    classifier = MLHeadingClassifier()
    return classifier.extract_outline_from_pdf(filepath)

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