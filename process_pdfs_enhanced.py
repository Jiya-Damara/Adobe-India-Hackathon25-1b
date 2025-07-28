"""
Enhanced Persona-Driven Document Intelligence Processor

This enhanced version includes:
- Intelligent content ranking based on persona and job requirements
- Section detection and meaningful title extraction
- TF-IDF based semantic similarity scoring
- Keyword-based relevance analysis
- Processing timestamps and improved metadata
"""

import json
import os
import time
from datetime import datetime
from utils.parser import extract_text_from_pdf
from utils.text_extractor import EnhancedTextExtractor
from utils.ranker import ContentRanker

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

def process_single_document_enhanced(doc_config, collection_dir, ranker, extractor):
    """
    Enhanced document processing with intelligent section extraction and ranking
    
    Returns:
        List of document sections with relevance scores and rankings
    """
    pdf_filename = doc_config["filename"]
    pdf_path = get_pdf_file_path(collection_dir, pdf_filename)

    if not os.path.exists(pdf_path):
        print(colored_terminal_text(f"File not found: {pdf_path}", "31"))
        return []

    print(colored_terminal_text(f"  Processing: {pdf_filename}", "36"))
    
    try:
        # Extract sections with intelligent detection
        sections = extractor.get_page_sections_for_ranking(pdf_path)
        
        # Add document name to each section
        for section in sections:
            section['document'] = pdf_filename
            
        return sections
        
    except Exception as e:
        print(colored_terminal_text(f"  Error processing {pdf_filename}: {str(e)}", "31"))
        return []

def create_enhanced_output(config, all_sections, ranker):
    """Create enhanced output with intelligent ranking and metadata"""
    
    # Rank all sections across all documents
    print(colored_terminal_text("  Ranking sections by relevance...", "33"))
    ranked_sections = ranker.rank_sections(all_sections)
    
    # Create metadata with timestamp
    metadata = {
        "input_documents": list(set(section['document'] for section in ranked_sections)),
        "persona": config["persona"]["role"],
        "job_to_be_done": config["job_to_be_done"]["task"],
        "processing_timestamp": datetime.now().isoformat(),
        "total_sections_analyzed": len(ranked_sections)
    }
    
    # Create extracted sections (top ranked sections)
    extracted_sections = []
    for section in ranked_sections:
        extracted_sections.append({
            "document": section['document'],
            "section_title": section.get('section_title', 'Content Section'),
            "importance_rank": section['importance_rank'],
            "page_number": section['page_number']
        })
    
    # Create subsection analysis with refined text
    subsection_analysis = []
    for section in ranked_sections:
        refined_text = ranker.extract_refined_subsection(section['text'])
        subsection_analysis.append({
            "document": section['document'],
            "refined_text": refined_text,
            "page_number": section['page_number']
        })
    
    return {
        "metadata": metadata,
        "extracted_sections": extracted_sections,
        "subsection_analysis": subsection_analysis
    }

def process_collection_documents_enhanced(config, collection_dir):
    """Enhanced processing with intelligent ranking and section detection"""
    start_time = time.time()
    
    print(colored_terminal_text(f"Initializing enhanced processing...", "34"))
    
    # Initialize components
    persona_role = config["persona"]["role"]
    job_task = config["job_to_be_done"]["task"]
    
    ranker = ContentRanker(persona_role, job_task)
    extractor = EnhancedTextExtractor()
    
    print(colored_terminal_text(f"Persona: {persona_role}", "35"))
    print(colored_terminal_text(f"Job: {job_task}", "35"))
    
    # Process all documents
    all_sections = []
    for document in config["documents"]:
        sections = process_single_document_enhanced(document, collection_dir, ranker, extractor)
        all_sections.extend(sections)
    
    if not all_sections:
        print(colored_terminal_text("No sections extracted from any documents!", "31"))
        return
    
    # Create enhanced output
    output_data = create_enhanced_output(config, all_sections, ranker)
    
    # Write output
    output_json_path = os.path.join(collection_dir, "challenge1b_output.json")
    with open(output_json_path, "w", encoding="utf-8") as file:
        json.dump(output_data, file, indent=2)
    
    processing_time = time.time() - start_time
    print(colored_terminal_text(f"Enhanced output written to {output_json_path}", "32"))
    print(colored_terminal_text(f"Processing time: {processing_time:.2f} seconds", "36"))
    print(colored_terminal_text(f"Sections analyzed: {len(all_sections)}", "36"))

def process_collection_documents_simple(config, collection_dir):
    """Fallback to simple processing if enhanced fails"""
    print(colored_terminal_text("Falling back to simple processing...", "33"))
    
    output_json_path = os.path.join(collection_dir, "challenge1b_output.json")
    output_data = {
        "metadata": {
            "input_documents": [doc["filename"] for doc in config["documents"]],
            "persona": config["persona"]["role"],
            "job_to_be_done": config["job_to_be_done"]["task"],
            "processing_timestamp": datetime.now().isoformat()
        },
        "extracted_sections": [],
        "subsection_analysis": []
    }

    for document in config["documents"]:
        pdf_filename = document["filename"]
        section_title = document["title"]
        pdf_path = get_pdf_file_path(collection_dir, pdf_filename)

        if not os.path.exists(pdf_path):
            continue

        try:
            # Extract first few pages
            pages = extract_text_from_pdf(pdf_path)[:3]
            
            for idx, page in enumerate(pages):
                output_data["extracted_sections"].append({
                    "document": pdf_filename,
                    "section_title": section_title,
                    "importance_rank": idx + 1,
                    "page_number": page["page_number"]
                })
                
                output_data["subsection_analysis"].append({
                    "document": pdf_filename,
                    "refined_text": page["text"][:300],
                    "page_number": page["page_number"]
                })
        except Exception as e:
            print(colored_terminal_text(f"Error processing {pdf_filename}: {e}", "31"))

    with open(output_json_path, "w", encoding="utf-8") as file:
        json.dump(output_data, file, indent=2)
    
    print(colored_terminal_text(f"Simple output written to {output_json_path}", "32"))

def process_all_collections(collection_names):
    """Process all collections with enhanced intelligence"""
    total_start_time = time.time()
    
    for collection_name in collection_names:
        input_json_path = os.path.join(collection_name, "challenge1b_input.json")
        if os.path.exists(input_json_path):
            print(colored_terminal_text(f"\n{'='*60}", "34"))
            print(colored_terminal_text(f"Processing {collection_name}", "34"))
            print(colored_terminal_text(f"{'='*60}", "34"))
            
            config = load_json_config(input_json_path)
            
            try:
                # Try enhanced processing first
                process_collection_documents_enhanced(config, collection_name)
            except ImportError as e:
                print(colored_terminal_text(f"Enhanced processing unavailable: {e}", "33"))
                print(colored_terminal_text("Using simple processing mode", "33"))
                process_collection_documents_simple(config, collection_name)
            except Exception as e:
                print(colored_terminal_text(f"Enhanced processing failed: {e}", "31"))
                print(colored_terminal_text("Falling back to simple processing", "33"))
                process_collection_documents_simple(config, collection_name)
        else:
            print(colored_terminal_text(f"Skipping {collection_name}: No input JSON found.", "33"))
    
    total_time = time.time() - total_start_time
    print(colored_terminal_text(f"\n{'='*60}", "32"))
    print(colored_terminal_text(f"All collections processed in {total_time:.2f} seconds", "32"))
    print(colored_terminal_text(f"{'='*60}", "32"))

def main():
    """Main entry point"""
    collections = ["Collection 1", "Collection 2", "Collection 3"]
    
    print(colored_terminal_text("🚀 Enhanced Persona-Driven Document Intelligence", "35"))
    print(colored_terminal_text("=" * 60, "35"))
    
    process_all_collections(collections)

if __name__ == "__main__":
    main()
