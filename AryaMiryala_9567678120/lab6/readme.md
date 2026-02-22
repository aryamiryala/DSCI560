Oil Well Data Extraction & Visualization Pipeline
Overview
This project is an end-to-end data pipeline that extracts, normalizes, enriches, and visualizes oil well data from multiple sources. It processes unstructured, scanned PDF documents (Completion Reports) using Optical Character Recognition (OCR), merges that data with live geographic and production metadata scraped from the web, and stores the integrated dataset in a normalized MySQL database. Finally, it serves this data to an interactive, frontend Leaflet map.

Project Structure & File Overview
The codebase is modularized to separate heavy processing (OCR) from network-dependent tasks (Scraping) and database operations.

Data Extraction & Processing
extract.py: The heavy-lifter. It loops through all scanned PDFs in data/pdf_data/, applies deskewing and OCR using ocrmypdf and pdfplumber (with a pytesseract fallback), and extracts the Universal API Number and Stimulation Volumes. It outputs raw checkpoints to extracted_data/extracted.jsonl.

normalize.py: A utility module containing the normalize_api() function. It ensures that regardless of OCR noise or formatting, all API numbers are strictly cleaned into the standard 10-digit North Dakota format (33-XXX-XXXXX).

web_scrape.py: The Selenium web-scraping module. It utilizes a headless Chrome WebDriver to search drillingedge.com by API number and extracts DOM-based metadata (Latitude, Longitude, Well Status, Well Type, Closest City, and Production Stats).

process_all.py: The orchestrator script. It reads the extracted.jsonl file, normalizes the APIs, manages a single persistent Selenium browser session (via web_scrape.py) to fetch web data, and merges both sources into a final "Golden Dataset" saved as extracted_data/final_cleaned_data.json.

Database Management
schema.sql: The SQL script that initializes the dsci560_wells database and creates the relational wells and stimulation tables.

insertsql.py: The database loader. It parses the final cleaned JSON file and performs an "UPSERT" (Insert or Update on Duplicate Key) into the MySQL database to prevent duplicate entries while capturing 1-to-many stimulation stages.

Web Application & Visualization
app.py: The Python Flask backend server. It connects to the MySQL database, joins the wells and stimulation tables, and serves the data as a JSON REST API endpoint (/api/wells). It also serves the frontend UI.

index.html: The frontend user interface. It utilizes Leaflet.js and MarkerCluster to render an interactive map. It dynamically plots well markers, color-codes them by well type, handles popup generation for detailed data inspection, and includes filtering/CSV export controls.

wellvisualization.php: (Alternative Backend) A PHP script that serves the exact same purpose as the Flask /api/wells route. Can be used if deploying to a traditional LAMP stack instead of Python/Flask.

Setup & Installation
1. Install System Dependencies (macOS)
These system-level tools are required for OCR and PDF processing. You will also need Google Chrome installed for the web scraper.

Bash
brew install ocrmypdf
brew install tesseract
brew install poppler
brew install ghostscript
2. Create and Activate Virtual Environment
Ensure all Python dependencies are installed in an isolated environment to prevent version conflicts.

Bash
python3 -m venv venv
source venv/bin/activate
3. Install Python Requirements
Bash
pip install -r requirements.txt
Database Setup
Create the SQL Database schema before running the pipeline.

Bash
mysql -u root -p < schema.sql
(If using an Ubuntu VM with socket authentication, you may need to run sudo mysql < schema.sql)

This creates the dsci560_wells database containing the wells and stimulation tables.

Execution Pipeline
Follow these steps in order to process the data from raw PDFs to the final web map.

Step 1: Extract Data from PDFs
This step takes the longest as it performs image-to-text OCR on all PDFs.

Bash
python3 extract.py
Output: Generates extracted_data/extracted.jsonl.

Step 2: Web Scraping & Data Merging
This script reads the JSONL, fires up a headless browser, scrapes missing metadata, and merges everything.

Bash
python3 process_all.py
Output: Generates extracted_data/final_cleaned_data.json.

Step 3: Insert Data into MySQL
Populate your database with the cleaned, merged dataset.

Bash
python3 insertsql.py \
  --file extracted_data/final_cleaned_data.json \
  --user root \
  --password yourpassword \
  --commit
(Omit --password if your local root user does not require one).

Step 4: Start the Web Application
Launch the Flask server to serve the frontend.

Bash
python3 app.py
The terminal will output: Running on http://127.0.0.1:5000

Using the Application
Open your browser and navigate to http://127.0.0.1:5000/.

Features Include:

Interactive Mapping: View all oil wells clustered dynamically by region.

Detailed Popups: Click on any marker to view technical data, including API, location, production stats, and stimulation/frac stages.

Raw Data Inspector: Expand the "Raw JSON" toggle inside any popup to view the raw scraped data structure.

Filtering: Use the control panel (top right) to filter wells by Status (Active/Plugged), minimum oil production, or search by API/Name.

CSV Export: Click the green "Export CSV" button to download a spreadsheet of the currently visible (filtered) wells on your map.