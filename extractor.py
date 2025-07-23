import os
import re
import json
from typing import List, Dict
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar
from pytesseract import image_to_string
from pdf2image import convert_from_path
from PIL import Image

# Heuristic heading detection thresholds
MIN_HEADING_FONT_SIZE = 12

IGNORED_PATTERNS = [
    r"^\d{4}-\d{2}-\d{1,2}$",  # Dates like 2000-01-01
    r"^[-\w]+\.(pdf|dat|bmk|mdf|ifd)$",  # File extensions
    r"^-abmk.*",  # Command-like patterns
    r"^[A-Z0-9_=,]+$",  # Technical config strings like trans_date=1,A
]


def extract_text_from_pdf(pdf_path: str) -> List[Dict]:
    headings = []

    for page_layout in extract_pages(pdf_path):
        page_number = page_layout.pageid
        for element in page_layout:
            if isinstance(element, LTTextContainer):
                for text_line in element:
                    text = text_line.get_text().strip()
                    if not text or len(text) > 200:
                        continue

                    # Skip ignored patterns
                    if any(re.match(pattern, text) for pattern in IGNORED_PATTERNS):
                        continue

                    font_sizes = [char.size for char in text_line if isinstance(char, LTChar)]
                    avg_font_size = sum(font_sizes) / len(font_sizes) if font_sizes else 0

                    if avg_font_size >= 18:
                        level = "H1"
                    elif avg_font_size >= 14:
                        level = "H2"
                    elif avg_font_size >= MIN_HEADING_FONT_SIZE:
                        level = "H3"
                    else:
                        continue

                    headings.append({
                        "level": level,
                        "text": text,
                        "page": page_number
                    })
    return headings


def extract_from_images(pdf_path: str) -> List[Dict]:
    headings = []
    images = convert_from_path(pdf_path)

    for page_num, image in enumerate(images, start=1):
        text = image_to_string(image)
        lines = text.split("\n")
        for line in lines:
            clean_line = line.strip()
            if not clean_line or len(clean_line) > 200:
                continue

            # Skip ignored patterns
            if any(re.match(pattern, clean_line) for pattern in IGNORED_PATTERNS):
                continue

            if re.match(r"^[A-Z][A-Za-z0-9 ,:\[\]()/-]{3,}$", clean_line):
                level = "H2" if len(clean_line.split()) > 3 else "H3"
                headings.append({
                    "level": level,
                    "text": clean_line,
                    "page": page_num
                })
    return headings


def extract_outline(pdf_path: str) -> Dict:
    text_headings = extract_text_from_pdf(pdf_path)
    if len(text_headings) < 5:
        img_headings = extract_from_images(pdf_path)
        combined = text_headings + img_headings
    else:
        combined = text_headings

    return {
        "title": os.path.splitext(os.path.basename(pdf_path))[0].replace("_", " "),
        "outline": sorted(combined, key=lambda x: x["page"])
    }


def save_json(output: Dict, output_path: str):
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)


def main():
    input_dir = "input"
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    for file in os.listdir(input_dir):
        if file.endswith(".pdf"):
            pdf_path = os.path.join(input_dir, file)
            result = extract_outline(pdf_path)
            output_path = os.path.join(output_dir, os.path.splitext(file)[0] + ".json")
            save_json(result, output_path)
            print(f"Extracted: {file} -> {output_path}")


if __name__ == "__main__":
    main()