# Adobe Hackathon 2025 – Round 1A: PDF Outline Extractor 🚀📄

## 🚀 Challenge Overview

The goal of Round 1A is to build an intelligent system that accepts a raw PDF and outputs a structured JSON outline. This includes extracting the document **title**, and **headings (H1, H2, H3)** with their respective page numbers, enabling smarter document understanding and experiences.

---

## 📂 Folder Structure

```
.
├── Dockerfile
├── main.py
├── ml_classifier.py
├── utils.py
├── model/
│   └── heading_classifier_model.pkl
├── data/
│   └── heading_training_data_final_corrected.csv
├── requirements.txt
├── input/
│   └── *.pdf
├── output/
│   └── *.json
```

---

## ⚙️ How It Works

The solution uses a **machine learning classifier** (RandomForestClassifier) trained on layout features such as font size, boldness, word count, position, and punctuation to predict whether a text line is a title, H1, H2, H3, or not a heading.

### 🧫 Model Details

- Model: RandomForestClassifier
- Framework: Scikit-learn
- Size: \~200MB
- Runs entirely offline (No network dependency)
- Model is trained using `heading_training_data_final_corrected.csv`

### 📌 Features Used:

- font\_size
- is\_bold
- y\_position
- word\_count
- char\_count
- ends\_colon
- all\_upper

---

## 🔪 Sample Output

```json
{
  "title": "Understanding AI",
  "outline": [
    { "level": "H1", "text": "Introduction", "page": 1 },
    { "level": "H2", "text": "What is AI?", "page": 2 },
    { "level": "H3", "text": "History of AI", "page": 3 }
  ]
}
```

---

## 🛠️ How to Build & Run the Solution (Locally)

### 🧱 Step 1: Build Docker Image

```bash
docker build --platform linux/amd64 -t pdf-processor .
```

### 🚦 Step 2: Run the Container

```bash
docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output --network none pdf-processor
```

> Note: Make sure to place PDF files inside the `input/` folder before running the above command.

---

## 📌 Docker Compatibility

- ✅ Compatible with `linux/amd64`
- ✅ No GPU required
- ✅ No internet required
- ✅ Model size < 200MB
- ✅ Runs within 10s for 50-page PDF

---

## 📙 Key Files

| File               | Purpose                                            |
| ------------------ | -------------------------------------------------- |
| `main.py`          | Entrypoint for processing all PDFs in input folder |
| `ml_classifier.py` | Core logic for ML-based heading extraction         |
| `utils.py`         | Helper functions (text cleaning, etc.)             |
| `Dockerfile`       | Defines the Docker environment                     |
| `requirements.txt` | Lists all required Python dependencies             |

---

## 🔍 Additional Notes

- The system merges nearby text lines (with similar y-position and same level) to form coherent headings.
- Title lines are intelligently extracted and grouped into a single string.
- The solution generalizes well across various PDF styles and layouts.

---

## 💾 Requirements (from `requirements.txt`)

```
PyMuPDF==1.24.0
jsonschema==4.20.0
scikit-learn==1.1.3
pandas==2.2.0
numpy==1.26.0
joblib==1.3.2
```

---

## 🧠 Team Info

Built with 💡 by [Your Name(s)], as part of Adobe India Hackathon 2025

---

## 🏑 Round 1A Complete!

This solution satisfies all Round 1A requirements including:

- Title + Heading (H1, H2, H3) detection
- Structured JSON output
- Dockerized AMD64-compatible build
- Offline execution and performance compliant

🎉 Ready for Round 1B!

