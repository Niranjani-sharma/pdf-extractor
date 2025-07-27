
import fitz
import pandas as pd
import joblib
from utils import clean_text, extract_title_from_outline

class MLHeadingClassifier:
    def __init__(self, model_path="heading_classifier_model.pkl"):
        self.model, self.label_encoder, self.feature_cols = joblib.load(model_path)

    def extract_features(self, text, font_size, is_bold, y_position):
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


    def extract_outline_from_pdf(self, filepath):
        doc = fitz.open(filepath)
        outline = []
        heading_candidates = []
    
        for i, page in enumerate(doc, start=1):
            lines_by_y = {}
    
            blocks = page.get_text("dict")["blocks"]
            for block in blocks:
                for line in block.get("lines", []):
                    y_pos = round(line["bbox"][1], 1)  # Round to group similar positions
                    text = " ".join([span["text"] for span in line["spans"]]).strip()
                    if not text or len(text) < 5:
                        continue
                    if y_pos not in lines_by_y:
                        lines_by_y[y_pos] = []
                    lines_by_y[y_pos].append(line)
    
            for y, lines in lines_by_y.items():
                all_spans = [span for line in lines for span in line["spans"]]
                if not all_spans:
                    continue
    
                text = " ".join([span["text"] for span in all_spans]).strip()
                font_size = max(span["size"] for span in all_spans)
                is_bold = any("bold" in span.get("font", "").lower() for span in all_spans)
                y_position = y
    
                features = self.extract_features(text, font_size, is_bold, y_position)
                df = pd.DataFrame([features])
                df_encoded = pd.get_dummies(df).reindex(columns=self.feature_cols, fill_value=0)
                pred = self.model.predict(df_encoded)
                label = self.label_encoder.inverse_transform(pred)[0]
    
                if label != "O":
                    heading_candidates.append({
                        "level": label,
                        "text": clean_text(text),
                        "page": i,
                        "y": y_position,
                        "score": font_size + int(is_bold) * 2
                    })
    
        # --- Merge lines with same level and close y-positions on same page ---
        merged = []
        if heading_candidates:
            heading_candidates.sort(key=lambda h: (h["page"], h["level"], h["y"]))
            buffer = [heading_candidates[0]]
    
            for h in heading_candidates[1:]:
                prev = buffer[-1]
                same_page = h["page"] == prev["page"]
                same_level = h["level"] == prev["level"]
                close_y = abs(h["y"] - prev["y"]) < 3  # tighter threshold
    
                if same_page and same_level and close_y:
                    buffer.append(h)
                else:
                    merged_text = " ".join(b["text"] for b in buffer)
                    merged.append({
                        "level": buffer[0]["level"],
                        "text": merged_text,
                        "page": buffer[0]["page"],
                        "y": buffer[0]["y"],
                        "score": buffer[0]["score"]
                    })
                    buffer = [h]
    
            if buffer:
                merged_text = " ".join(b["text"] for b in buffer)
                merged.append({
                    "level": buffer[0]["level"],
                    "text": merged_text,
                    "page": buffer[0]["page"],
                    "y": buffer[0]["y"],
                    "score": buffer[0]["score"]
                })
    
        # --- Title logic ---
        title_items = [h for h in merged if h["level"].lower() == "title"]
        title_items.sort(key=lambda x: x["y"])
        title = ", ".join(h["text"] for h in title_items).strip()

    
        # --- Final outline: remove title from outline ---
        outline = [h for h in merged if h["level"].lower() != "title"]
        for h in outline:
            h.pop("score", None)
            h.pop("y", None)
    
        return {
            "title": title,
            "outline": outline
        }
    