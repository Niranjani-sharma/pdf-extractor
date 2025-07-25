
#!/usr/bin/env python3

from extract_outline import extract_outline_from_pdf
import os
import json

def main():
    input_dir = "input"
    output_dir = "output"
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Process all PDF files in the input directory
    pdf_files = [f for f in os.listdir(input_dir) if f.endswith('.pdf')]
    
    if not pdf_files:
        print("No PDF files found in the input directory.")
        return
    
    for filename in pdf_files:
        print(f"Processing {filename}...")
        pdf_path = os.path.join(input_dir, filename)
        
        try:
            result = extract_outline_from_pdf(pdf_path)
            
            output_filename = filename.replace(".pdf", ".json")
            output_path = os.path.join(output_dir, output_filename)
            
            with open(output_path, "w", encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            print(f"✅ {filename} -> {output_filename}")
            
        except Exception as e:
            print(f"❌ Error processing {filename}: {str(e)}")
    
    print(f"\n🎉 Processing complete! Check the '{output_dir}' directory for results.")

if __name__ == "__main__":
    main()
