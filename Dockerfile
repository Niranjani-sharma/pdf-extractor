FROM --platform=linux/amd64 python:3.10-slim

# Set work directory
WORKDIR /app

# Copy app files
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Entrypoint script to process all PDFs in /app/input and save JSONs to /app/output
ENTRYPOINT ["python", "extract_outline.py"]
