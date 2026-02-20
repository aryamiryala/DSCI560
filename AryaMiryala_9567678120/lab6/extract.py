import os
import re
import json
import subprocess
from pathlib import Path
from pdf2image import convert_from_path
import pytesseract
import pdfplumber
import pandas as pd
from normalize import normalize_api

#data and extraction paths
pdf_folder = Path("data/pdf_data")
ocr_folder= Path("data/ocr_pdfs")
extracted_folder = Path("extracted_data") / "extracted.jsonl"
ocr_folder.mkdir(parents=True, exist_ok=True)
extracted_folder.parent.mkdir(parents=True, exist_ok=True)

api_match = re.compile(r'\bAPI(?:\s*#|\:)?\s*[:\-\s]*([0-9\-]{6,20})', re.I)
latitude_match = re.compile(r'(Latitude|Lat)[:\s]*([-+]?\d{1,3}\.\d+)', re.I)
longitude_match = re.compile(r'(Longitude|Long)[:\s]*([-+]?\d{1,3}\.\d+)', re.I)

coordinate_match = re.compile(r'(\d{1,3}°\s*\d{1,2}\'\s*\d{1,2}(?:\.\d+)?\")')

#coverts the pdf into readable pdf to allow search
def ocrpdf(input_pdf: Path, output_pdf: Path):

    #shellcommand
    cmd = ["ocrmypdf", "--deskew", "--skip-text", str(input_pdf), str(output_pdf)]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        print(f"ocrmypdf failed for {input_pdf}: {e}. Trying without --skip-text.")
        cmd = ["ocrmypdf", "--deskew", str(input_pdf), str(output_pdf)]
        subprocess.run(cmd, check=False)


#extract text
def pdf_text(pdf_path: Path):
    #empty string in case no text is extracted
    text = ""
    try:
        #open pdf and extract text into a big string
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                text += "\n" + page_text
    except Exception as e:
        print("pdfplumber failed with:", e)
    return text

#incase plumber fails, convert to image and run tesseract
def tesseract_from_pdf(pdf_path: Path):
    # convert pages to images and run pytesseract
    text = ""
    images = convert_from_path(str(pdf_path), dpi=300)
    for i, img in enumerate(images):
        page_text = pytesseract.image_to_string(img, lang='eng')
        text += "\n" + page_text
    return text


#turns data into structured text
def parse_fields(text: str):
    out = {}
    #captures api number
    api_found = api_match.search(text)
    if api_found:
        raw_api = api_found.group(1).strip()
        out['api'] = normalize_api(raw_api)
    # lat/lon patterns
    lat_match = latitude_match.search(text)
    lon_match = longitude_match.search(text)
    if lat_match:
        out['latitude'] = float(lat_match.group(1))
    if lon_match:
        out['longitude'] = float(lon_match.group(1))

    #name of the well
    well = None
    m = re.search(r'Well\s+Name[:\s\-]*(.+)', text, re.I)
    if m:
        well = m.group(1).splitlines()[0].strip()
    else:
        # fallback: first 3 words in document in uppercase style
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        if lines:
            candidate = lines[0]
            if len(candidate.split()) <= 6:
                well = candidate
    if well:
        #split name and number
        out['well_name'] = well
    # address
    addr = None
    m = re.search(r'Address[:\s\-]*(.+)', text, re.I)
    if m:
        addr = m.group(1).splitlines()[0].strip()
        out['address'] = addr
    # look for  "Stimulation" or "Stage"
    stim_block = None
    stim_start = re.search(r'(Stimul|Stimulation|Frac|Stage\s*1)', text, re.I)
    if stim_start:
        #take the next 2000 characters
        idx = stim_start.start()
        stim_block = text[idx: idx+2000]
        out['stimulation_text'] = stim_block
    # return raw
    out['raw'] = text
    return out

def main():
    results = []
    pdf_files = sorted(pdf_folder.glob("*.pdf"))[:10] #start testing with 10 first
    #temp for testing
    if extracted_folder.exists():
        extracted_folder.unlink()
    #for pdf_file in sorted(pdf_folder.glob("*.pdf")):
    for pdf_file in pdf_files:
        print("Processing", pdf_file)
        ocr_pdf_path = ocr_folder / pdf_file.name
        ocrpdf(pdf_file, ocr_pdf_path)
        text = pdf_text(ocr_pdf_path)
        if (not text) or len(text) < 50:
            # if it doesnt work, run tesseract on images
            print("Fallback: running pdf2image + pytesseract")
            text = tesseract_from_pdf(ocr_pdf_path)
        parsed = parse_fields(text)
        parsed['source_pdf'] = str(pdf_file)
        results.append(parsed)


        # append to jsonl
        with open(extracted_folder, "a", encoding="utf-8") as f:
            f.write(json.dumps(parsed) + "\n")

        print("Extracted:", {
            "api": parsed.get("api"),
            "well_name": parsed.get("well_name"),
            "latitude": parsed.get("latitude"),
            "longitude": parsed.get("longitude")
        })
    print("Done")

if __name__ == "__main__":
    main()