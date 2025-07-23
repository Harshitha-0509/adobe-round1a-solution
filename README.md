# Adobe Hackathon 2025 - Round 1A Submission

## 🚀 Challenge: Connecting the Dots - Document Structure Extractor

This solution extracts a **structured outline** from raw PDF files, identifying:
- **Title**
- **Headings** (`H1`, `H2`, `H3`) along with their **page numbers**

It meets all constraints outlined in Round 1A of the Adobe India Hackathon 2025.

---

## 🧠 Approach

1. **Text Extraction**:
   - Uses `PyMuPDF` (fitz) to extract text and layout metadata from PDF pages.

2. **Heading Detection**:
   - Headings are detected using a hybrid logic combining:
     - Font size and boldness (for relative importance)
     - Text position (top of page, alignment)
     - Heuristics like line breaks, capital case, and uniqueness
   - A scoring system determines heading **levels** (H1 > H2 > H3)

3. **Title Identification**:
   - First large, centered text on page 1 is considered the document title.

4. **Outline Structuring**:
   - Each heading is appended to a list with its level and page number.
   - The entire structure is serialized into JSON format.

---

## 🐳 Docker Instructions

### 🔧 Build Docker Image

```bash
docker build --platform linux/amd64 -t pdf-extractor .
