
import fitz  # PyMuPDF
import joblib
import pandas as pd
import os
from utils import clean_text

class MLHeadingClassifier:
    def __init__(self, model_path="attached_assets/heading_classifier_model_1753555744519.pkl"):
        """Initialize the ML classifier with the trained model."""
        if os.path.exists(model_path):
            self.clf, self.le, self.feature_cols = joblib.load(model_path)
            self.model_loaded = True
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
    
    def classify_text(self, text, font_size, is_bold, y_position):
        """Classify a single text segment using the ML model."""
        if not self.model_loaded:
            return "O"  # Non-heading
        
        try:
            feat = self.extract_features(text, font_size, is_bold, y_position)
            df = pd.DataFrame([feat])
            df_encoded = pd.get_dummies(df).reindex(columns=self.feature_cols, fill_value=0)
            label = self.le.inverse_transform(self.clf.predict(df_encoded))[0]
            return label
        except Exception as e:
            print(f"Error in ML classification: {e}")
            return "O"
    
    def extract_outline_from_pdf(self, pdf_path):
        """Extract outline from PDF using ML classification."""
        doc = fitz.open(pdf_path)
        headings = []
        
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
                    if len(full_text) < 5:  # Skip very short text
                        continue
                    
                    max_font_size = max(font_sizes) if font_sizes else 12
                    is_bold = any(bold_flags)
                    y_pos = line["bbox"][1]
                    
                    # Classify the text
                    label = self.classify_text(full_text, max_font_size, is_bold, y_pos)
                    
                    if label != "O":  # If it's a heading
                        headings.append({
                            "level": label,
                            "text": clean_text(full_text),
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
                if len(text) >= 5 and len(text) <= 150:
                    return text
        
        # If no good H1, take the first meaningful heading
        for heading in headings:
            text = heading.get("text", "").strip()
            if len(text) >= 5:
                return text
        
        return ""
