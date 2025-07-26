import fitz  # PyMuPDF
import re
import unicodedata

HEADING_KEYWORDS = {
    "introduction", "summary", "deliverables", "appendix",
    "references", "case study", "test case", "limitations",
    "conclusion", "methodology", "results", "discussion",
    "acknowledgments", "abstract"
}

def is_bold(span):
    return bool(span.get("flags", 0) & 2)

def is_all_caps(text):
    return text.isupper() and 1 < len(text.split()) <= 8

def is_likely_heading(text):
    if not text:
        return False
    text = text.strip()
    if len(text) < 3 or len(text) > 150:
        return False
    if text.count(" ") > 20:
        return False
    if re.search(r"^(the|a|an|it|this|that|which|is|are|was|were)\\b", text.lower()):
        return False
    if text.count('.') > 1 or text.count(',') > 1:
        return False
    if not re.search(r"[\w\u00C0-\u017F]", text):  # includes Latin accents
        return False
    return True

def matches_heading_pattern(text):
    return bool(re.match(r"^(Chapter|Section|Part|Article|Appendix)\\s+(\\d+(\\.\\d+)*)([A-Za-z\-\\.]*)$", text.strip(), re.IGNORECASE))

def extract_title_and_headings(pdf_path):
    doc = fitz.open(pdf_path)
    font_sizes = {}
    candidate_headings = []
    pages_to_sample = min(doc.page_count, 5)

    for i in range(pages_to_sample):
        for block in doc[i].get_text("dict")["blocks"]:
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    text = span.get("text", "").strip()
                    if text:
                        size = round(span["size"], 1)
                        font_sizes[size] = font_sizes.get(size, 0) + 1

    if not font_sizes:
        return "Untitled", []

    common_sizes = sorted(font_sizes.items(), key=lambda x: x[1], reverse=True)
    body_size = common_sizes[0][0]
    h1_threshold_diff = 4
    h2_threshold_diff = 1.5

    def get_heading_level(size, span):
        if size >= body_size + h1_threshold_diff:
            return "H1"
        elif size >= body_size + h2_threshold_diff:
            return "H2"
        elif size >= body_size:
            if is_bold(span):
                return "H3"
        if is_bold(span) and is_all_caps(span.get("text", "")):
            return "H3"
        return None

    title = "Untitled"
    max_sz_for_title = 0
    for block in doc[0].get_text("dict")["blocks"]:
        for line in block.get("lines", []):
            for span in line["spans"]:
                t = span.get("text", "").strip()
                if len(t) > 5 and span["size"] > max_sz_for_title and is_likely_heading(t):
                    title = t
                    max_sz_for_title = span["size"]
                if max_sz_for_title > body_size + 8:
                    break

    score_threshold = 1.5
    for page_num, page in enumerate(doc, start=1):
        seen = set()
        for block in page.get_text("dict")["blocks"]:
            for line in block.get("lines", []):
                for span in line["spans"]:
                    text = span.get("text", "").strip()
                    if not text or not is_likely_heading(text):
                        continue
                    size = round(span["size"], 1)
                    level = get_heading_level(size, span)
                    if not level:
                        continue
                    y_pos = span["origin"][1]
                    if y_pos < 50 or y_pos > (page.rect.height - 50):
                        continue
                    score = 2.5 if level == "H1" else 2 if level == "H2" else 1.5
                    if is_bold(span): score += 1
                    if is_all_caps(text): score += 0.8
                    if matches_heading_pattern(text): score += 2
                    page_width = page.rect.width
                    x_pos = span["origin"][0]
                    text_width = span["bbox"][2] - span["bbox"][0]
                    if abs(x_pos - (page_width - text_width) / 2) < 50:
                        score += 0.7
                    if any(kw in text.lower() for kw in HEADING_KEYWORDS):
                        score += 0.5
                    if score < score_threshold:
                        continue
                    key = (text.lower(), round(y_pos))
                    if key in seen:
                        continue
                    seen.add(key)
                    candidate_headings.append({
                        "level": level,
                        "text": text,
                        "page": page_num,
                        "score": score,
                        "y_pos": y_pos
                    })

    final = []
    processed = set()
    last = None
    for h in sorted(candidate_headings, key=lambda x: (x["page"], x["y_pos"], -x["score"])):
        key = (h["text"].lower(), h["page"], h["level"])
        if last and last["page"] == h["page"] and last["level"] == h["level"] and \
           last["text"].lower() == h["text"].lower() and abs(last["y_pos"] - h["y_pos"]) < 10:
            continue
        if key not in processed:
            processed.add(key)
            final.append({k: h[k] for k in ("level", "text", "page")})
            last = h

    return title, final