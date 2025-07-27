# 🧠 Adobe Hackathon - Round 1A: PDF Heading Extractor

## 📌 Objective

Extract a structured JSON outline from PDF documents, including:
- **Document Title**
- **Headings** with levels (H1, H2, H3)
- **Page numbers** for each heading

---

## 🔧 How It Works

This solution uses **PyMuPDF** to:
- [cite_start]Parse PDF layout and extract text spans from each page[cite: 5].
- [cite_start]Dynamically determine the body text font size to establish relative font size thresholds for H1, H2, and H3[cite: 5].
- [cite_start]Score candidate text spans using a combination of heuristics like font size, boldness, alignment, capitalization, and pattern matching[cite: 5].
- [cite_start]Filter out non-heading text such as paragraph content, common headers/footers, and other noise[cite: 5].
- [cite_start]Classify identified headings into hierarchical levels (H1, H2, H3)[cite: 5].
- [cite_start]Return a clean, deduplicated heading outline in the specified JSON format[cite: 21].

[cite_start]This approach is entirely heuristic-based and does **not** rely on any external machine learning models, ensuring a small footprint and offline capability.

---

## 🧠 Heuristics Used

| Feature           | Description                                                                     |
|-------------------|---------------------------------------------------------------------------------|
| **Font Size** | Compares text span font sizes to the document's estimated body text size to classify H1, H2, H3. [cite_start]H1 is largest, H2 medium, H3 smaller. [cite: 5]             |
| **Boldness** | [cite_start]Checks for bold font styling using PyMuPDF's span flags. [cite: 5]                             |
| **Alignment** | [cite_start]Assigns a higher score to text that appears centered on the page, typical for main headings. [cite: 5]          |
| **Capitalization**| [cite_start]Boosts scores for text that is entirely in uppercase, often indicating a heading. [cite: 5]        |
| **Position Filter**| [cite_start]Ignores text found too close to the top or bottom margins of pages (e.g., page numbers, headers/footers). [cite: 5] |
| **Repetition Filter**| [cite_start]Avoids adding duplicate headings on the same page or extremely similar consecutive headings. [cite: 5]    |
| **Regex Pattern** | [cite_start]Identifies specific patterns like "Chapter 1", "Section 2.1", "Appendix A", etc., common in structured documents. [cite: 5] |
| **Sentence Filter**| [cite_start]Rejects text spans that appear to be long sentences, contain excessive punctuation, or start with common articles/prepositions, indicating non-heading content. [cite: 5] |
| **Keyword Boost** | [cite_start]Provides an additional score boost for text containing common heading keywords like "Introduction", "Summary", "Conclusion", etc. [cite: 5] |

---

�
� Technologies Used 
------------------------

• PyMuPDF (fitz): PDF parsing 

• regex (re): Heading pattern detection 

• unicodedata: Unicode normalization 

• os, json, time: File I/O and timing 

� Code Explanation (Round 1A) 
------------------------------

main.py 
------
This is the entry point of the Round 1A app. It: 
1. Scans all .pdf files in the /app/input directory. 
2. For each file: 
a. Calls extract_title_and_headings(pdf_path) from utils.py. 
b. Stores result in a dictionary with title and outline. 
c. Writes a corresponding .json file to /app/output. 
3. Times the total processing duration. 

utils.py – Core Logic 
-----------------------
Function: extract_title_and_headings(pdf_path) 

Step-by-step: 

1. Open PDF with PyMuPDF. 
2. Estimate Body Font Size: 
a. Loop through first 5 pages and count frequency of each font size. 
b. Largest frequency is considered as body_size. 
3. Extract Title: 
a. On the first page, scan all text spans. 
b. Choose the largest span (visually) that looks like a heading. 
4. Scan All Pages: 
a. Loop over every page and text span. 
b. Filter candidates using is_likely_heading() (length, punctuation, 
common starter words, etc.). 
c. Use get_heading_level() to classify as H1, H2, or H3 based on font size + 
boldness. 
5. Score Each Heading: 
a. Heuristic score components: 
i. Font size boost (H1 > H2 > H3) 
ii. Bold = +1 
iii. All caps = +0.8 
iv. Regex pattern match ("Chapter 1", etc) = +2 
v. Center-aligned = +0.7 
vi. Keyword match (e.g., "introduction") = +0.5 
b. Skip low-scoring candidates (< threshold). 
6. De-duplicate Similar Headings: 
a. Avoid near-identical headings on same page within close Y distance. 
7. Return Title + Cleaned Heading List 
Helper Functions 
• is_bold(span): Checks bold flag from span. 
• is_all_caps(text): All uppercase and short length. 
• is_likely_heading(text): Filters out long sentences, small strings, and non
informative phrases. 
• matches_heading_pattern(text): Detects known patterns like "Chapter 1.2", 
"Appendix A". 

## 🌍 Multilingual Support

This extractor is designed to work effectively with **Unicode-based multilingual PDFs**, including scripts such as:

-   Hindi (Devanagari) – शीर्षक 1
-   Japanese – 第1章
-   Arabic – العنوان 1
-   Russian – Глава 1
-   Chinese – 第一章

✅ All language content is preserved via PyMuPDF's robust Unicode support.  
✅ The heading detection logic is primarily layout-based (font size, position, style) and pattern-based, making it highly adaptable across different languages and character sets without requiring language-specific models.

� Docker Commands (Round 1A) 
----------------------------
Build Docker Image 
docker build --platform linux/amd64 -t connect-dots-app . 

Run Docker Container 
docker run --rm -v ${PWD}/input:/app/input -v ${PWD}/output:/app/output connect-dots
app

**Sample multilingual output:**
```json
{
  "title": "शीर्षक 1",
  "outline": [
    { "level": "H1", "text": "शीर्षक 1", "page": 1 },
    { "level": "H1", "text": "第1章", "page": 1 },
    { "level": "H1", "text": "العنوان 1", "page": 1 },
    { "level": "H1", "text": "Глава 1", "page": 1 },
    { "level": "H1", "text": "第一章", "page": 1 }
  ]
}
