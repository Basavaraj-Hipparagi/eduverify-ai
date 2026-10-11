# EduVerify AI

> **AI-Powered Educational Document Data Extraction & Authenticity Verification System**  
> *Tagline: Verify with Confidence.*

---

## 1. Project Overview & Problem Statement

Academic credential fraud, inflated marksheets, and forged certificates present major risks to universities, credential evaluators, and employers worldwide. Traditional manual verification is slow, prone to oversight, and heavily dependent on human review.

**EduVerify AI** is an automated, evidence-based verification system built for a final-year engineering project. It streamlines document processing by combining **dual-engine text extraction** (PyMuPDF for digital PDFs and Tesseract OCR with image preprocessing for scanned documents), **mathematical consistency checks**, **QR-code cryptographic inspection with SSRF protection**, **PDF digital signature analysis**, and **institutional database comparison**.

---

## 2. Key Features

- **Document Ingestion**: Drag-and-drop file upload supporting PDF, PNG, JPG, JPEG, and TIFF (10 MB configurable size limit).
- **Document Categories**: Specialized parsing schemas for:
  1. Academic Marksheets
  2. Degree Certificates
  3. Provisional Certificates
  4. School Certificates (10th/12th Boards)
  5. Academic Transcripts
  6. Other Educational Documents
- **Dual-Engine Extraction**: Native high-fidelity PyMuPDF vector text extraction for digital PDFs, paired with Tesseract OCR (auto-contrast and thresholding) for scanned certificates.
- **Academic Consistency Checks**:
  - **Check A (Required Fields)**: Identifies missing mandatory fields based on document category schema.
  - **Check B (Marks Math)**: Computes subject sums, validates aggregate percentage calculations, checks range bounds (`marks <= maximum`), and evaluates grading thresholds.
  - **Check C (Date Consistency)**: Chronological ordering (`exam_date <= issue_date`) and academic year sanity.
  - **Check D (Identifier Formats)**: Regular expression pattern validation for roll numbers, registration numbers, and certificate serials.
  - **Check E (Cross-Field & QR Alignment)**: Cross-compares printed student names and roll numbers against decoded QR payloads to catch header tampering.
- **QR-Code Analysis**: Decodes QR payloads, validates URLs against an institutional allowlist, and protects against Server-Side Request Forgery (SSRF) and private RFC1918 loopback addresses.
- **Digital Signature Inspection**: Inspects embedded PDF cryptographic signature dictionaries (`/Type /Sig`), byte range integrity, signer certificates, and flags post-signature alterations.
- **Synthetic Demonstration Provider**: Built-in test provider loaded with fictional student records (Rohan Sharma, Ananya Verma) supporting Match, Partial Match, Mismatch, Record Not Found, and Service Unavailable scenarios (prominently labeled: `DEMO MODE — SYNTHETIC TEST DATA`).
- **Interactive Two-Column Dashboard**:
  - **Left**: Document stage with page switcher, zoom in/out, and fit-page controls.
  - **Right**: Overall status card, experimental risk score bar, editable fields form, and tabbed check breakdowns.
- **Editable Extraction Form**: Allows human reviewers to correct OCR misreadings and re-evaluate consistency checks and risk scores with one click.
- **Downloadable PDF Verification Report**: Uses ReportLab to generate an official verification certificate including check findings, metadata, and legal disclaimers.
- **Session History & Privacy**: SQLite database logs verification metadata with options to view reports, delete entries, or clear all history.

---

## 3. Technology Stack

- **Frontend**: HTML5, Vanilla CSS3 (custom SaaS theme, dark navy/indigo accents, glassmorphism), Vanilla JavaScript, Lucide Icons.
- **Backend**: Python 3.10+, Flask 3.x.
- **PDF Processing**: PyMuPDF (`pymupdf`).
- **OCR Engine**: Tesseract OCR (`pytesseract`, Pillow).
- **Computer Vision & QR**: OpenCV (`opencv-python-headless`), ReportLab QR barcode engine.
- **Database**: SQLite 3 (local file-based storage).
- **Report Generation**: ReportLab 4.x.
- **Testing**: pytest.

---

## 4. System Architecture

```
EduVerify AI Architecture
┌────────────────────────────────────────────────────────┐
│                   Web Browser UI                       │
│    (HTML5 + Vanilla CSS + Vanilla JS + Lucide Icons)   │
└───────────────────────────┬────────────────────────────┘
                            │ REST API (JSON / FormData)
┌───────────────────────────▼────────────────────────────┐
│                  Flask Application                     │
│                       (app.py)                         │
└───────┬──────────────┬──────────────┬───────────┬──────┘
        │              │              │           │
┌───────▼──────┐┌──────▼──────┐┌──────▼────┐┌─────▼──────┐
│  PDF / Image ││   Academic   ││    QR    ││  Database  │
│  Extraction  ││ Consistency ││ & Digital ││  (SQLite)  │
│  (PyMuPDF &  ││    Engine    ││ Signature ││  (db.py)   │
│  Tesseract)  ││ (Check A-E) ││  (OpenCV) │└────────────┘
└───────┬──────┘└──────┬──────┘└──────┬────┘
        │              │              │
┌───────▼──────────────▼──────────────▼──────────────────┐
│             Master Verification Engine                 │
│              (verification_service.py)                 │
└───────────────────────────┬────────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────┐
│            Official PDF Report Generator               │
│                 (ReportLab PDF Engine)                 │
└────────────────────────────────────────────────────────┘
```

---

## 5. Directory Structure

```
EduVerify-AI/
├── app.py                      # Main Flask application and REST routes
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation
├── .env.example                # Environment variable template
├── .gitignore                  # Git ignore rules
├── sample_generator.py         # Generates sample test marksheets & certificates
├── database/
│   ├── __init__.py
│   └── db.py                   # SQLite database helper & schema
├── services/
│   ├── __init__.py
│   ├── pdf_service.py          # PyMuPDF text & page extraction
│   ├── ocr_service.py          # Tesseract OCR & image preprocessing
│   ├── extraction_service.py   # Structured academic field regex & parser
│   ├── consistency_service.py  # Checks A through E (Math, Dates, Formats)
│   ├── qr_service.py           # QR detection, SSRF protection & allowlists
│   ├── signature_service.py    # PDF digital signature inspection
│   ├── demo_provider.py       # Fictional institutional database provider
│   ├── verification_service.py # Master verification coordinator
│   └── report_service.py       # ReportLab PDF certificate generator
├── templates/
│   └── index.html              # Frontend dashboard template
├── static/
│   ├── css/
│   │   └── style.css           # Premium SaaS dashboard styles
│   └── js/
│       └── script.js           # Client-side controller & document viewer
├── sample_documents/           # Generated test documents
├── tests/
│   ├── __init__.py
│   ├── test_app.py             # Endpoint integration tests
│   ├── test_extraction.py      # Field parser & PDF extraction tests
│   └── test_verification.py    # Consistency math, QR & report tests
├── uploads/                    # Temporary uploaded documents (auto-created)
├── instance/                   # SQLite database file (auto-created)
└── reports/                    # Generated PDF verification reports (auto-created)
```

---

## 6. Installation & Setup Instructions

### Prerequisites
- Python 3.10 or higher.
- (Optional for scanned image OCR) Tesseract OCR installed on your system.

### Step 1: Clone or Navigate to Project Directory
```powershell
cd "c:\Users\basav\OneDrive\Desktop\OCR PLAN"
```

### Step 2: Install Python Dependencies
```powershell
pip install -r requirements.txt
```
*(On macOS / Linux: `pip3 install -r requirements.txt`)*

### Step 3: Tesseract OCR Setup (Optional for scanned images)
EduVerify AI natively extracts text from digital PDFs without requiring Tesseract. To enable OCR on scanned images (PNG, JPG, TIFF) or scanned image PDFs:

- **Windows**:
  - Download and install Tesseract from: [UB-Mannheim Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki)
  - Or run: `winget install UB-Mannheim.TesseractOCR`
  - Ensure `tesseract.exe` is added to your PATH or located at `C:\Program Files\Tesseract-OCR\tesseract.exe`.
- **macOS**:
  - `brew install tesseract`
- **Linux (Ubuntu/Debian)**:
  - `sudo apt-get install tesseract-ocr`

### Step 4: Generate Sample Demonstration Documents
Run the built-in sample generator:
```powershell
python sample_generator.py
```
This produces three sample documents in `sample_documents/`:
1. `valid_marksheet.pdf`: Authentic marksheet for student Rohan Sharma with embedded QR code.
2. `tampered_marksheet.pdf`: Marksheet with forged total marks (560 instead of 480) for testing fraud detection.
3. `sample_certificate.pdf`: Degree certificate for student Ananya Verma.

---

## 7. Running the Application

### Start the Flask Server
```powershell
python app.py
```

Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 8. Mobile & Android Phone App Installation

EduVerify AI is built as a **Progressive Web App (PWA)** and is responsive across **Mobile Phones, Tablets, and Laptops**.

### How to Install on Your Android Phone:
1. **Ensure your Android phone is connected to the same Wi-Fi network** as this computer.
2. Find your computer's IP address (e.g. `10.184.34.130`).
3. Open **Google Chrome** on your Android phone and navigate to:
   ```
   http://10.184.34.130:5000
   ```
4. **Install the App**:
   - Tap the **Install Mobile App** button on the screen, or
   - Tap the three dots (**⋮**) in the top-right corner of Chrome and select **"Install app"** or **"Add to Home screen"**.
5. **Native Mobile App Features**:
   - Runs in standalone fullscreen mode without the browser URL bar.
   - Dedicated App Icon with Shield badge on your phone home screen.
   - **Bottom Navigation Bar** for one-tap switching between Home, Verify, History, and About.
   - **Direct Camera Capture**: Tap **"Scan with Camera"** in the upload section to take a photo of any physical certificate or marksheet directly using your phone's camera!

---

## 9. Demonstration & Testing Guide

### Test Scenario A: Authentic Marksheet
1. Open `http://127.0.0.1:5000` and click **Verify Document**.
2. Select **Academic Marksheet** as the document category.
3. Upload `sample_documents/valid_marksheet.pdf`.
4. Click **Analyze & Verify Document**.
5. **Expected Outcome**:
   - Status: `VERIFIED AGAINST AUTHORIZED SOURCE` (Green).
   - Risk Score: `0 / 100` (Low).
   - Checks: All mathematical sums (`480 == 480`), percentage (`80.0%`), and dates pass.
   - QR Code: Detected and matches student identity.
   - Institutional DB: Exact MATCH against synthetic record for Rohan Sharma.

### Test Scenario B: Tampered Marksheet Detection
1. Click **Verify Another Document**.
2. Upload `sample_documents/tampered_marksheet.pdf`.
3. Click **Analyze & Verify Document**.
4. **Expected Outcome**:
   - Status: `REVIEW RECOMMENDED` (Amber/Red).
   - Risk Score: `45 / 100` (Moderate/High Anomaly).
   - Check B Failure: `Subject Sum Total Consistency: FAILED` (`Calculated sum: 480.0, Stated total: 560.0`).
   - The system flags the discrepancy with evidence and recommended human action.

### Test Scenario C: Human Review & Field Editing
1. On the results page for any document, navigate to the **1. Extracted Data** tab.
2. Edit a field (e.g., student name or total marks).
3. Click **Save Edits & Re-check**.
4. The system updates the record, flags the field as `[User Edited]`, and recalculates all consistency checks and risk scores instantly.

### Test Scenario D: Official PDF Report Generation
1. Click **Download PDF Report** in the top right.
2. Open the downloaded PDF: It contains an executive summary, check breakdown table, QR/signature details, and institutional disclaimer.

---

## 9. Running Automated Tests

Run the full pytest suite:
```powershell
python -m pytest -v
```

All 12 automated unit and integration tests will execute and pass:
- API health and homepage endpoints
- File upload and invalid format rejection
- Text extraction and schema field parsing
- Subject sum match and mismatch detection
- SSRF prevention on QR URLs
- Synthetic demo provider test cases
- ReportLab PDF generation

---

## 10. Security & Privacy Architecture

- **Path Traversal Protection**: Uploaded files use sanitized filenames (`secure_filename`) and isolated UUIDs.
- **Server-Side File Validation**: Validates file MIME types, extensions, and enforces a strict 10 MB limit.
- **SSRF Prevention**: QR code URLs pointing to private IP addresses (RFC1918, `127.0.0.1`, `localhost`) are blocked from network requests.
- **Session Isolation**: History records and uploaded documents are isolated per user session.
- **Zero Third-Party Data Leakage**: Document processing is completely local. No student data is transmitted to external paid APIs.

---

## 11. Project Report Outline (Final-Year Submission)

### Chapter 1: Introduction
- 1.1 Background & Motivation
- 1.2 Problem Statement
- 1.3 Objectives & Scope
- 1.4 Organization of the Report

### Chapter 2: Literature Review & Existing Systems
- 2.1 Existing Academic Verification Portals
- 2.2 Shortcomings of Conventional Manual Audits
- 2.3 Role of OCR and Computer Vision in Document Analysis
- 2.4 Digital Signatures and QR Code Cryptography

### Chapter 3: System Requirements & Architecture
- 3.1 Functional Requirements
- 3.2 Non-Functional Requirements (Security, Performance, Privacy)
- 3.3 System Architecture & Component Diagram
- 3.4 Data Flow Diagrams (DFD Level 0, 1, 2)

### Chapter 4: Implementation Details
- 4.1 Document Ingestion & Image Preprocessing Pipeline
- 4.2 PyMuPDF Native Text Parser & Tesseract OCR Integration
- 4.3 Structured Academic Extraction Engine
- 4.4 Consistency Verification Engine (Checks A–E)
- 4.5 QR Code Detection & SSRF Security Barrier
- 4.6 Digital Signature Inspection
- 4.7 Synthetic Institutional Provider & SQLite Storage
- 4.8 ReportLab Automated Report Synthesis

### Chapter 5: Testing & Experimental Results
- 5.1 Test Plan & Methodology
- 5.2 Unit Testing & Integration Testing Results
- 5.3 Test Case Scenarios (Authentic, Tampered, Inconclusive)
- 5.4 Performance Metrics & Processing Durations

### Chapter 6: Conclusion & Future Enhancements
- 6.1 Summary of Contributions
- 6.2 Limitations
- 6.3 Future Work (Blockchain credential anchoring, mobile camera scanning)

---

## 12. Disclaimer

*This application provides automated document-processing and technical consistency verification. It is not a substitute for formal confirmation from the issuing educational institution. A document should not be classified as fraudulent solely because verification was unavailable or a technical anomaly was detected.*
