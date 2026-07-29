# Customer Financial Summary

## Overview

Customer Financial Summary is an AI-powered application that analyzes customer financial documents and generates a chronological financial journey.

The application extracts information from multiple supporting documents such as employment records, salary slips, business documents, inheritance records, and property documents to generate:

- Customer Financial Timeline
- Financial Summary
- Estimated Net Worth
- AI-generated Customer Financial Report

---

## Problem Statement

Given multiple customer financial documents, the application should:

- Identify document types
- Extract important financial information
- Build the customer's financial timeline
- Calculate financial summary
- Generate a comprehensive customer financial report

---

## Tech Stack

### Backend
- Python
- FastAPI

### Frontend
- Streamlit

### AI
- LangGraph
- LangChain
- Gemini LLM (or other supported LLM)

---

## High-Level Architecture

```

User
↓
Streamlit
↓
FastAPI
↓
LangGraph Workflow
↓
File Validation
↓
Document Splitting
↓
Document Classification
↓
OCR (if required)
↓
Entity Extraction
↓
Structured JSON
↓
Timeline Builder
↓
Validation
↓
Financial Analysis
↓
Report Generation
↓
Streamlit

```

---

## Service Output Schemas

### 1. File Validation (`file_validation.py`) Output Schema

```json
{
  "status": "SUCCESS | PARTIAL_SUCCESS | FAILED",
  "valid_files": [
    {
      "file_path": "uploaded_documents/salary_jan.pdf",
      "file_name": "salary_jan.pdf",
      "extension": ".pdf",
      "size_bytes": 1048576,
      "mime_type": "application/pdf",
      "is_valid": true
    }
  ],
  "invalid_files": [
    {
      "file_path": "uploaded_documents/corrupted_doc.xyz",
      "reason": "Unsupported format or file corrupted",
      "error_code": "INVALID_FORMAT"
    }
  ]
}
```

### 2. Document Classifier (`classifier.py`) Output Schema

```json
{
  "classified_documents": [
    {
      "file_path": "uploaded_documents/salary_jan.pdf",
      "document_type": "SALARY_SLIP",
      "confidence_score": 0.96,
      "page_count": 2,
      "metadata": {
        "is_scanned_pdf": false,
        "requires_ocr": false
      }
    }
  ]
}
```

**Supported Document Types**: `SALARY_SLIP`, `BANK_STATEMENT`, `TAX_RETURN`, `PROPERTY_DOCUMENT`, `BUSINESS_RECORD`, `INHERITANCE_RECORD`, `OTHER`

---

## Project Structure

```

customer-financial-summary/

├── app/
├── streamlit/
├── requirements.txt
├── README.md
└── .gitignore

```

---

## Setup

### Clone Repository

```bash
git clone <repository-url>
cd customer-financial-summary
```

### Create Virtual Environment

Mac/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Run FastAPI

```bash
uvicorn app.main:app --reload
```

Swagger UI:

```
http://127.0.0.1:8000/docs
```

---

## Run Streamlit

```bash
streamlit run streamlit/app.py
```

---

## Team

| Module | Owner |
|---------|-------|
| Architecture & Integration | TBD |
| Streamlit UI | TBD |
| Document Processing | TBD |
| Entity Extraction | TBD |
| Financial Analysis | TBD |
| Report Generation | TBD |

---

## Status

- [x] Project Setup
- [x] FastAPI Initialized
- [x] Streamlit Initialized
- [ ] LangGraph Workflow
- [ ] Document Processing
- [ ] Entity Extraction
- [ ] Financial Analysis
- [ ] Report Generation

## Development Guidelines

- Do not commit directly to the `main` branch.
- Create a feature branch for every task.
- Raise a Pull Request before merging.
- Follow the agreed project architecture.
- Keep modules independent and reusable.