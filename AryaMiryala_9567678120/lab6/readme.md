# Setup & Run Instructions

## Create and Activate Virtual Environment

```bash
python3 -m venv venv
```

Activate the environment:

```bash
source venv/bin/activate
```

This ensures all dependencies are installed in an isolated environment.

---

## Install System Dependencies (macOS)

These tools are required for OCR and PDF processing:

```bash
brew install ocrmypdf
brew install tesseract
brew install poppler
brew install ghostscript
```

---

## Install Python Requirements

After activating the virtual environment:

```bash
pip install -r requirements.txt
```

---

# Database Setup

## Create the SQL Database

Run:

```bash
mysql < schema.sql
```

If using Ubuntu VM with socket authentication:

```bash
sudo mysql < schema.sql
```

This will create:

- `dsci560_wells` database
- `wells` table
- `stimulation` table

---

# Data Extraction Pipeline

## Extract Data from PDFs

```bash
python extract.py
python web_scrape.py
```

What these scripts do:

- `extract.py`
  - Loops through all PDF files
  - Converts scanned PDFs into readable text using OCR
  - Extracts structured well data

- `web_scrape.py`
  - Uses API information extracted from PDFs
  - Retrieves additional well data from external websites
  - Enhances the dataset with missing information

---

##  Process & Clean Data

```bash
python process_all.py
```

This script:

- Combines extracted PDF data
- Merges stimulation data
- Cleans and structures the dataset
- Outputs:

```
extracted_data/final_cleaned_data.json
```

---

#  Insert Data into MySQL

Populate the database with:

```bash
python insertsql.py \
  --file extracted_data/final_cleaned_data.json \
  --user yourusername \
  --password yourpassword \
  --commit
```

This script:

- Reads cleaned JSON
- Inserts well records into `wells`
- Inserts stimulation data into `stimulation`
- Prevents duplicate API entries

---

# Run the Web Application

## Start the Flask Server

```bash
python app.py
```

You should see:

```
Running on http://127.0.0.1:5000
```

---

## Open in Browser

Navigate to:

```
http://127.0.0.1:5000/
```

---

# Using the Application

Once loaded, you can:

- View all oil wells on an interactive map
- Hover or click markers for detailed well information
- Search wells by API number
- Filter wells based on production data
- View stimulation data in popups

---

# Complete Pipeline Overview

```
PDF Files
   ↓
extract.py (OCR + text extraction)
   ↓
web_scrape.py (additional data enrichment)
   ↓
process_all.py (clean & combine JSON)
   ↓
insertsql.py (populate MySQL)
   ↓
Flask API (app.py)
   ↓
Leaflet Web Map Visualization
```