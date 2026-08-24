# 🔍 Forensic Lens

### A Comprehensive Digital Forensics & Evidence Analysis Framework

**Forensic Lens** is a Python-based digital forensics application designed to assist investigators, cybersecurity researchers, and security professionals in analyzing and validating digital evidence through a centralized graphical interface.

The platform combines **file analysis, metadata extraction, cryptographic hash verification, tamper detection, deleted-file recovery, USB forensics, and automated reporting** into a unified forensic workflow.

---

## ✨ Features

### 🖼️ Image Forensics

* Extract image metadata and EXIF information
* Analyze image properties and embedded information
* Calculate cryptographic hashes
* Verify evidence integrity
* Perform tamper/manipulation analysis
* Generate forensic findings

### 📄 Document Forensics

Supports forensic analysis of common document formats.

* PDF metadata extraction
* DOCX metadata analysis
* Document property inspection
* Suspicious artifact identification
* Evidence integrity verification

### 🦠 Executable Analysis

* Executable file inspection
* YARA-based pattern matching
* Suspicious artifact detection
* Hash generation and verification
* Support for malware-oriented forensic investigation

### 💾 File Recovery

Recover potentially deleted files from supported evidence sources.

* Deleted-file detection
* File carving
* Recovery using forensic utilities
* Separate recovered-evidence storage
* Recovery result documentation

### 🔌 USB Forensics

Analyze USB storage devices and their forensic artifacts.

* USB device scanning
* USB artifact collection
* Deleted-file recovery
* USB activity timeline
* Device-related forensic information

### 🔐 Hash Verification

Forensic Lens supports multiple cryptographic hashing algorithms:

* **MD5**
* **SHA-1**
* **SHA-256**

Hash values can be used to establish and verify the integrity of digital evidence.

### 🕵️ Tamper Detection

The application helps identify possible modifications to digital evidence by comparing cryptographic hash values and analyzing relevant file characteristics.

### 📊 Automated Forensic Reporting

Generate structured forensic reports containing:

* Case information
* Examiner information
* Evidence details
* File metadata
* Hash values
* Analysis results
* Recovery information
* Forensic findings

---

# 🏗️ System Architecture

```text
                         ┌──────────────────────┐
                         │      Forensic Lens   │
                         │      PyQt5 GUI       │
                         └──────────┬───────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              │                     │                     │
              ▼                     ▼                     ▼
       ┌─────────────┐       ┌─────────────┐       ┌─────────────┐
       │    Image    │       │  Documents  │       │ Executables │
       │   Forensics │       │  Forensics  │       │   Analysis  │
       └──────┬──────┘       └──────┬──────┘       └──────┬──────┘
              │                     │                     │
              └─────────────────────┼─────────────────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │ Metadata Extraction  │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │  Hash Verification   │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │   Tamper Detection   │
                         └──────────┬───────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    ▼                               ▼
           ┌─────────────────┐             ┌─────────────────┐
           │  File Recovery  │             │  USB Forensics  │
           └────────┬────────┘             └────────┬────────┘
                    │                               │
                    └───────────────┬───────────────┘
                                    ▼
                         ┌──────────────────────┐
                         │  Report Generation   │
                         └──────────────────────┘
```

---

# 📂 Project Structure

```text
Forensic-Lens/
│
├── main.py
├── requirements.txt
├── README.md
│
├── modules/
│   ├── metadata_extraction.py
│   ├── hash_verification.py
│   ├── tamper_detection.py
│   ├── reporting.py
│   ├── file_recovery.py
│   ├── social_fingerprint.py
│   │
│   └── usb/
│       ├── usb_scanner.py
│       ├── usb_deleted_recovery.py
│       └── usb_timeline.py
│
├── cases/
│   └── <case_number>/
│       ├── evidence/
│       ├── recovered/
│       ├── reports/
│       └── logs/
│
└── ...
```

> **Note:** The project structure may evolve as additional forensic modules are added.

---

# 🛠️ Technology Stack

| Category              | Technology         |
| --------------------- | ------------------ |
| Programming Language  | Python             |
| GUI Framework         | PyQt5              |
| Database              | SQLite             |
| Image Metadata        | ExifRead           |
| PDF Analysis          | PyPDF2             |
| DOCX Analysis         | python-docx        |
| File System Forensics | pytsk3             |
| File Recovery         | Foremost           |
| Pattern Detection     | YARA / yara-python |
| Cryptographic Hashing | hashlib            |
| Report Generation     | ReportLab / HTML   |
| Operating System      | Linux              |

---

# 🔬 Forensic Workflow

Forensic Lens follows a structured evidence-analysis workflow:

```text
        Evidence Collection
                │
                ▼
       Evidence Identification
                │
                ▼
        Metadata Extraction
                │
                ▼
        Hash Calculation
                │
                ▼
       Integrity Verification
                │
                ▼
         Forensic Analysis
                │
       ┌────────┼─────────┐
       ▼        ▼         ▼
     Image   Document  Executable
    Analysis  Analysis   Analysis
       │        │         │
       └────────┼─────────┘
                ▼
        Tamper Detection
                │
                ▼
          File Recovery
                │
                ▼
         Report Generation
```

---

# 🔐 Evidence Integrity

Maintaining the integrity of digital evidence is a fundamental requirement in digital forensics.

Forensic Lens uses cryptographic hashing to establish and verify evidence integrity.

Supported algorithms:

```text
MD5
SHA-1
SHA-256
```

A hash can be generated when evidence is acquired and later recalculated to determine whether the evidence has changed.

---

# 💾 USB Forensics

The USB forensic module provides capabilities for analyzing removable storage devices.

```text
USB Device
    │
    ▼
Device Detection
    │
    ▼
USB Scanning
    │
    ▼
Artifact Collection
    │
    ├───────────────┐
    ▼               ▼
Deleted Files    Timeline
    │               │
    └───────┬───────┘
            ▼
      Forensic Report
```

The module is designed to assist with:

* USB device identification
* Evidence scanning
* Deleted-file recovery
* USB timeline generation
* Artifact analysis

---

# 🗂️ Case Management

Forensic investigations can be organized using case-specific directories.

Example:

```text
Case_001/
│
├── evidence/
│   ├── image.jpg
│   ├── document.pdf
│   └── sample.exe
│
├── recovered/
│
├── reports/
│
└── logs/
```

This separation helps maintain an organized investigation workflow and keeps original evidence separate from recovered artifacts and generated reports.

---

# 📊 Forensic Reports

Forensic Lens can generate structured reports containing investigation results.

A typical report may include:

```text
┌─────────────────────────────────────┐
│          FORENSIC REPORT            │
├─────────────────────────────────────┤
│ Case Number                         │
│ Examiner Information               │
│ Evidence Information               │
│ File Metadata                      │
│ MD5 / SHA-1 / SHA-256              │
│ Analysis Results                   │
│ Tamper Detection Results           │
│ Recovery Results                   │
│ Forensic Findings                  │
└─────────────────────────────────────┘
```

Reports provide a documented record of the performed forensic analysis.

---

# 🚀 Installation

## 1. Clone the Repository

```bash
git clone https://github.com/amaanwaris/Forensic-Lenstm.git
```

## 2. Navigate to the Project

```bash
cd Forensic-Lenstm
```

## 3. Create a Virtual Environment

```bash
python3 -m venv venv
```

## 4. Activate the Virtual Environment

### Linux / macOS

```bash
source venv/bin/activate
```

### Windows

```powershell
venv\Scripts\activate
```

## 5. Install Python Dependencies

```bash
pip install -r requirements.txt
```

---

# ▶️ Running the Application

Start the application using:

```bash
python3 main.py
```

The PyQt5 graphical interface will launch and provide access to the available forensic modules.

---

# 🧪 Example Investigation

A typical investigation can follow this workflow:

### Step 1 — Create a Case

Provide:

```text
Case Number
Examiner Name
Investigation Details
```

### Step 2 — Add Evidence

Select the file or forensic evidence that needs to be analyzed.

### Step 3 — Perform Analysis

Select the appropriate module:

```text
Image Forensics
Document Forensics
Executable Analysis
File Recovery
USB Forensics
```

### Step 4 — Verify Integrity

Calculate and record:

```text
MD5
SHA-1
SHA-256
```

### Step 5 — Analyze Results

Review:

* Metadata
* Hash values
* Suspicious artifacts
* Tamper indicators
* Recovered files
* USB activity

### Step 6 — Generate Report

Export the investigation findings into a structured forensic report.

---

# 📦 Dependencies

The project uses Python libraries and forensic tools such as:

```text
PyQt5
PyPDF2
python-docx
ExifRead
pytsk3
yara-python
hashlib
sqlite3
ReportLab
```

Depending on the forensic functionality being used, additional system packages may be required.

---

# 🎯 Project Objectives

The primary objectives of Forensic Lens are to:

* Automate common digital forensic tasks
* Provide a centralized forensic analysis interface
* Simplify evidence investigation
* Extract useful digital artifacts
* Verify evidence integrity
* Detect potential evidence manipulation
* Recover deleted files
* Analyze USB artifacts
* Generate structured forensic reports
* Provide a modular foundation for future forensic capabilities

---

# 🔮 Future Enhancements

Planned or potential improvements include:

* [ ] Memory forensics
* [ ] Browser artifact analysis
* [ ] Windows Registry analysis
* [ ] Email forensics
* [ ] Network forensics
* [ ] Advanced malware analysis
* [ ] Timeline visualization
* [ ] Chain-of-custody management
* [ ] PDF forensic report generation
* [ ] Evidence bookmarking
* [ ] Advanced YARA rule management
* [ ] AI-assisted forensic artifact classification
* [ ] Multi-case investigation dashboard

---

# ⚠️ Disclaimer

**Forensic Lens is intended for authorized digital forensic investigations, cybersecurity research, education, and security analysis.**

Do not use this software to access, analyze, recover, or investigate data or devices without proper authorization.

The developers are not responsible for misuse of the software.

---

# 🤝 Contributing

Contributions are welcome.

If you would like to improve Forensic Lens:

```bash
# Fork the repository

# Create a feature branch
git checkout -b feature/new-feature

# Commit your changes
git commit -m "Add new forensic feature"

# Push the branch
git push origin feature/new-feature
```

Then open a Pull Request.

---

# ⭐ Support

If you find **Forensic Lens** useful, consider giving the repository a ⭐ on GitHub.

Bug reports, feature requests, and contributions are welcome.

---

# 👨‍💻 Author

## Amaan Waris

**B.Tech — Computer Science & Information Technology**

### Areas of Interest

* 🔐 Digital Forensics
* 🛡️ Cybersecurity
* 🐍 Python
* 🐧 Linux
* 💻 System Programming
* 🔧 Embedded Systems
* 🌐 Network Security


# 📜 License

This project is currently intended for **educational and research purposes**.

If the project is released as open source, an appropriate license such as the **MIT License** can be added to the repository.


