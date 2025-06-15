#!/usr/bin/env python

import os
import sys
import json
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any, Union

import typer
from rich.console import Console
from rich.logging import RichHandler
from rich.table import Table
from dotenv import load_dotenv

# Add the current directory to the path so imports work correctly
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from src.document_processor.extractor import DocumentExtractor
from src.entity_mapper.mapper import EntityMapper, EntityDatabase
from src.entity_mapper.schema import Entity, MappingResult
from src.utils.visualization import generate_html_visualization

# Set up logging
console = Console()
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True, console=console)],
)
log = logging.getLogger("rich")

# Load environment variables
load_dotenv()

# Create Typer app
app = typer.Typer(help="Boon Entity Mapper - Extract and map entities from documents")


@app.command()
def process(
    input_path: str = typer.Argument(..., help="Path to input document or directory"),
    output_dir: str = typer.Option(
        os.getenv("OUTPUT_DIR", "./results"), help="Directory to save results"
    ),
    model: str = typer.Option(
        os.getenv("DEFAULT_MODEL", "gpt-4o"), help="LLM model to use for extraction"
    ),
    detail_level: str = typer.Option(
        os.getenv("DETAIL_LEVEL", "high"), 
        help="Detail level for vision models (high, medium, low)"
    ),
    db_path: str = typer.Option(
        None, help="Path to entity database JSON file"
    ),
    match_threshold: float = typer.Option(
        float(os.getenv("MATCH_THRESHOLD", "0.85")),
        help="Threshold for entity matching confidence"
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
) -> None:
    """Process documents and map entities to the database."""
    # Set log level based on verbose flag
    if verbose:
        logging.getLogger("rich").setLevel(logging.DEBUG)
    
    # Validate input path
    input_path = Path(input_path)
    if not input_path.exists():
        log.error(f"Input path does not exist: {input_path}")
        raise typer.Exit(code=1)
    
    # Create output directory if it doesn't exist
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize components
    log.info("Initializing document extractor...")
    extractor = DocumentExtractor(
        model=model,
        detail_level=detail_level,
    )
    
    log.info("Initializing entity database and mapper...")
    db_path = Path(db_path) if db_path else None
    database = EntityDatabase(db_path)
    mapper = EntityMapper(
        database=database,
        match_threshold=match_threshold,
    )
    
    # Process documents
    try:
        # Process single document or directory
        if input_path.is_file():
            process_single_document(input_path, output_dir, extractor, mapper)
        elif input_path.is_dir():
            process_document_directory(input_path, output_dir, extractor, mapper)
        else:
            log.error(f"Input path is neither a file nor a directory: {input_path}")
            raise typer.Exit(code=1)
        
        log.info("✅ Processing completed successfully")
    except Exception as e:
        log.exception(f"Error during processing: {e}")
        raise typer.Exit(code=1)


def process_single_document(
    document_path: Path,
    output_dir: Path,
    extractor: DocumentExtractor,
    mapper: EntityMapper
) -> None:
    """Process a single document file."""
    log.info(f"Processing document: {document_path}")
    
    # Extract entities
    log.info("Extracting entities...")
    if document_path.suffix.lower() == '.pdf':
        entities = extractor.extract_from_pdf(document_path)
    else:
        entities = extractor.extract_from_image(document_path)
    
    log.info(f"Extracted {len(entities)} entities")
    
    # Map entities
    log.info("Mapping entities to database...")
    mapping_results = mapper.map_entities(entities)
    
    # Count mapped entities
    mapped_count = sum(1 for result in mapping_results if result.mapped_entity_id is not None)
    log.info(f"Successfully mapped {mapped_count} out of {len(mapping_results)} entities")
    
    # Count name changes detected
    name_changes = sum(1 for result in mapping_results if result.name_change_detected)
    if name_changes > 0:
        log.info(f"Detected {name_changes} entity name changes")
    
    # Save results
    save_results(document_path, output_dir, entities, mapping_results)
    
    # Display summary
    display_mapping_summary(mapping_results)


def process_document_directory(
    directory_path: Path,
    output_dir: Path,
    extractor: DocumentExtractor,
    mapper: EntityMapper
) -> None:
    """Process all documents in a directory."""
    log.info(f"Processing documents in directory: {directory_path}")
    
    # Get document files
    document_files = []
    for ext in ['*.pdf', '*.jpg', '*.jpeg', '*.png']:
        document_files.extend(directory_path.glob(ext))
    
    if not document_files:
        log.warning(f"No document files found in {directory_path}")
        return
    
    log.info(f"Found {len(document_files)} document files")
    
    # Process each document
    for document_path in document_files:
        process_single_document(document_path, output_dir, extractor, mapper)


def save_results(
    document_path: Path,
    output_dir: Path,
    entities: List[Entity],
    mapping_results: List[MappingResult]
) -> None:
    """Save extraction and mapping results to files."""
    # Create document-specific output directory
    doc_output_dir = output_dir / document_path.stem
    doc_output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save extracted entities
    entities_file = doc_output_dir / "extracted_entities.json"
    with open(entities_file, "w") as f:
        entities_data = [entity.dict() for entity in entities]
        json.dump(entities_data, f, indent=2)
    
    # Save mapping results
    mapping_file = doc_output_dir / "mapping_results.json"
    with open(mapping_file, "w") as f:
        mapping_data = [result.dict() for result in mapping_results]
        json.dump(mapping_data, f, indent=2)
    
    # Generate HTML visualization
    html_file = doc_output_dir / "visualization.html"
    generate_html_visualization(mapping_results, html_file)
    
    log.info(f"Results saved to {doc_output_dir}")


def display_mapping_summary(mapping_results: List[MappingResult]) -> None:
    """Display a summary table of mapping results."""
    table = Table(title="Entity Mapping Summary")
    
    table.add_column("Original Entity", style="cyan")
    table.add_column("Mapped To", style="green")
    table.add_column("Confidence", style="yellow")
    table.add_column("Name Change", style="magenta")
    
    for result in mapping_results:
        original_name = result.original_entity.name
        mapped_name = result.mapped_entity_name or "Not Mapped"
        confidence = f"{result.confidence:.2f}" if result.confidence > 0 else "N/A"
        
        name_change = "No"
        if result.name_change_detected and result.name_change:
            name_change = f"{result.name_change.previous_name} → {result.name_change.current_name}"
        
        table.add_row(original_name, mapped_name, confidence, name_change)
    
    console.print(table)


@app.command()
def version():
    """Display the current version of the tool."""
    console.print("Boon Entity Mapper v0.1.0")


if __name__ == "__main__":
    app()
