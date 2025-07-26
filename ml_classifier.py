
import fitz  # PyMuPDF
import joblib
import pandas as pd
import os
import re
from collections import Counter
from utils import clean_text

class MLHeadingClassifier:
    def __init__(self, model_path="attached_assets/heading_classifier_model_1753555744519.pkl"):
        """Initialize the ML classifier with the trained model."""
        if os.path.exists(model_path):
            try:
                self.clf, self.le, self.feature_cols = joblib.load(model_path)
                self.model_loaded = True
            except Exception as e:
                print(f"Warning: Could not load model {model_path}: {e}. Using fallback classification.")
                self.model_loaded = False
        else:
            print(f"Warning: Model file {model_path} not found. Using fallback classification.")
            self.model_loaded = False
    
    def extract_features(self, text, font_size, is_bold, y_position):
        """Extract features for ML classification."""
        return {
            "text": text,
            "font_size": font_size,
            "is_bold": is_bold,
            "y_position": y_position,
            "word_count": len(text.split()),
            "char_count": len(text),
            "ends_colon": text.strip().endswith(":"),
            "all_upper": text.isupper(),
        }
    
    def fallback_classify(self, text, font_size, is_bold, avg_font_size):
        """Fallback classification when ML model is not available."""
        text = text.strip()
        
        # Skip very short text or numbers only
        if len(text) < 3 or text.isdigit():
            return "O"
        
        # Skip common non-heading patterns
        if re.match(r'^[•\-\*\+\s]+$', text) or text.lower() in ['page', 'of', 'the', 'and']:
            return "O"
        
        # Determine heading level based on font size and formatting
        if font_size >= avg_font_size + 4 or (is_bold and font_size >= avg_font_size + 2):
            return "H1"
        elif font_size >= avg_font_size + 2 or (is_bold and font_size >= avg_font_size + 1):
            return "H2"
        elif font_size >= avg_font_size + 1 or is_bold:
            return "H3"
        elif font_size >= avg_font_size:
            return "H4"
        
        return "O"
    
    def classify_text(self, text, font_size, is_bold, y_position, avg_font_size=12):
        """Classify a single text segment using the ML model or fallback."""
        if self.model_loaded:
            try:
                feat = self.extract_features(text, font_size, is_bold, y_position)
                df = pd.DataFrame([feat])
                df_encoded = pd.get_dummies(df).reindex(columns=self.feature_cols, fill_value=0)
                label = self.le.inverse_transform(self.clf.predict(df_encoded))[0]
                return label
            except Exception as e:
                print(f"Error in ML classification: {e}")
                return self.fallback_classify(text, font_size, is_bold, avg_font_size)
        else:
            return self.fallback_classify(text, font_size, is_bold, avg_font_size)
    
    def extract_outline_from_pdf(self, pdf_path):
        """Extract outline from PDF using ML classification or fallback."""
        doc = fitz.open(pdf_path)
        headings = []
        all_font_sizes = []
        
        # First pass: collect all font sizes to determine average
        for page_num in range(len(doc)):
            page = doc[page_num]
            blocks = page.get_text("dict")["blocks"]
            
            for block in blocks:
                if "lines" not in block:
                    continue
                    
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        span_text = span["text"].strip()
                        if span_text and len(span_text) > 2:
                            all_font_sizes.append(span["size"])
        
        avg_font_size = sum(all_font_sizes) / len(all_font_sizes) if all_font_sizes else 12
        
        # Second pass: extract headings
        for page_num in range(len(doc)):
            page = doc[page_num]
            blocks = page.get_text("dict")["blocks"]
            
            for block in blocks:
                if "lines" not in block:
                    continue
                    
                for line in block.get("lines", []):
                    # Combine all spans in the line
                    text_parts = []
                    font_sizes = []
                    bold_flags = []
                    
                    for span in line.get("spans", []):
                        span_text = span["text"].strip()
                        if span_text:
                            text_parts.append(span_text)
                            font_sizes.append(span["size"])
                            bold_flags.append("bold" in span.get("font", "").lower())
                    
                    if not text_parts:
                        continue
                    
                    # Combine text and get max font size
                    full_text = " ".join(text_parts).strip()
                    if len(full_text) < 3:  # Skip very short text
                        continue
                    
                    # Skip obvious non-headings
                    if re.match(r'^\d+$', full_text) or full_text.lower() in ['page', 'of']:
                        continue
                    
                    max_font_size = max(font_sizes) if font_sizes else 12
                    is_bold = any(bold_flags)
                    y_pos = line["bbox"][1]
                    
                    # Classify the text
                    label = self.classify_text(full_text, max_font_size, is_bold, y_pos, avg_font_size)
                    
                    if label != "O":  # If it's a heading
                        cleaned_text = clean_text(full_text)
                        if cleaned_text and len(cleaned_text) >= 3:
                            headings.append({
                                "level": label,
                                "text": cleaned_text,
                                "page": page_num + 1  # 1-indexed page numbers
                            })
        
        doc.close()
        
        # Remove duplicates while preserving order
        unique_headings = []
        seen = set()
        
        for heading in headings:
            key = (heading["text"].lower().strip(), heading["page"])
            if key not in seen:
                seen.add(key)
                unique_headings.append(heading)
        
        # Extract title (first H1 or first meaningful heading)
        title = self._extract_title(unique_headings)
        
        return {
            "title": title,
            "outline": unique_headings
        }
    
    def _extract_title(self, headings):
        """Extract title from headings list."""
        if not headings:
            return ""
        
        # Look for the first H1
        for heading in headings:
            if heading.get("level") == "H1":
                text = heading.get("text", "").strip()
                if len(text) >= 3 and len(text) <= 200:
                    return text
        
        # If no good H1, take the first meaningful heading
        for heading in headings:
            text = heading.get("text", "").strip()
            if len(text) >= 3:
                return text
        
        return ""
