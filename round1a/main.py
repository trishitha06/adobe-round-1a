import os
import json
import time
from utils import extract_title_and_headings

INPUT_DIR = "/app/input"
OUTPUT_DIR = "/app/output"


def main():
    total_start = time.perf_counter()
    file_count = 0

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for filename in os.listdir(INPUT_DIR):
        if filename.endswith(".pdf"):
            file_count += 1
            start = time.perf_counter()

            pdf_path = os.path.join(INPUT_DIR, filename)
            title, headings = extract_title_and_headings(pdf_path)

            result = {
                "title": title,
                "outline": headings
            }

            output_filename = os.path.splitext(filename)[0] + ".json"
            output_path = os.path.join(OUTPUT_DIR, output_filename)

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

            duration = time.perf_counter() - start
            print(f"✅ Processed: {filename} in {duration:.2f} seconds")
            print(f"📄 Output: {output_path}\n")

    total_duration = time.perf_counter() - total_start
    print(f"🚀 Completed processing {file_count} file(s) in {total_duration:.2f} seconds")


if __name__ == "__main__":
    main()