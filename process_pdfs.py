import json
import os
from utils.parser import extract_text_from_pdf

def load_json_config(config_path):
    """Load JSON configuration from a file."""
    with open(config_path, "r", encoding="utf-8") as file:
        return json.load(file)

def colored_terminal_text(text, color_code):
    """Return colored text for terminal output."""
    return f"\033[{color_code}m{text}\033[0m"

def get_pdf_file_path(collection_dir, pdf_filename):
    """Construct the full path to a PDF file."""
    return os.path.join(collection_dir, "PDFs", pdf_filename)

def extract_sample_pages(pdf_path, num_pages=3):
    """Extract text from the first few pages of a PDF."""
    all_pages = extract_text_from_pdf(pdf_path)
    return all_pages[:num_pages]

def append_metadata(metadata, document_name):
    """Append document name to metadata."""
    metadata["input_documents"].append(document_name)

def add_extracted_section(sections, doc_name, section_title, rank, page_num):
    """Add extracted section details."""
    sections.append({
        "document": doc_name,
        "section_title": section_title,
        "importance_rank": rank,
        "page_number": page_num
    })

def add_subsection_analysis(analysis, doc_name, text, page_num):
    """Add subsection analysis details."""
    analysis.append({
        "document": doc_name,
        "refined_text": text[:300],
        "page_number": page_num
    })

def process_single_document(doc_config, collection_dir, output_data):
    """Process a single document and update output data."""
    pdf_filename = doc_config["filename"]
    section_title = doc_config["title"]
    pdf_path = get_pdf_file_path(collection_dir, pdf_filename)

    if not os.path.exists(pdf_path):
        print(colored_terminal_text(f"File not found: {pdf_path}", "31"))
        return

    sample_pages = extract_sample_pages(pdf_path)
    append_metadata(output_data["metadata"], pdf_filename)

    for idx, page in enumerate(sample_pages):
        add_extracted_section(
            output_data["extracted_sections"],
            pdf_filename,
            section_title,
            idx + 1,
            page["page_number"]
        )
        add_subsection_analysis(
            output_data["subsection_analysis"],
            pdf_filename,
            page["text"],
            page["page_number"]
        )

def process_collection_documents(config, collection_dir):
    """Process all documents in a collection."""
    output_json_path = os.path.join(collection_dir, "challenge1b_output.json")
    output_data = {
        "metadata": {
            "input_documents": [],
            "persona": config["persona"]["role"],
            "job_to_be_done": config["job_to_be_done"]["task"]
        },
        "extracted_sections": [],
        "subsection_analysis": []
    }

    for document in config["documents"]:
        process_single_document(document, collection_dir, output_data)

    with open(output_json_path, "w", encoding="utf-8") as file:
        json.dump(output_data, file, indent=2)

    print(colored_terminal_text(f"Output written to {output_json_path}", "32"))

def process_all_collections(collection_names):
    """Process all collections listed."""
    for collection_name in collection_names:
        input_json_path = os.path.join(collection_name, "challenge1b_input.json")
        if os.path.exists(input_json_path):
            print(colored_terminal_text(f"\nProcessing {collection_name}", "34"))
            config = load_json_config(input_json_path)
            process_collection_documents(config, collection_name)
        else:
            print(colored_terminal_text(f"Skipping {collection_name}: No input JSON found.", "33"))

def main():
    collections = ["Collection 1", "Collection 2", "Collection 3"]
    process_all_collections(collections)

if __name__ == "__main__":
    main()