#!/usr/bin/env python

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

import flask
from flask import Flask, request, render_template, jsonify, send_from_directory
from werkzeug.utils import secure_filename

# Add the current directory to the path so imports work correctly
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from src.document_processor.extractor import DocumentExtractor
from src.entity_mapper.mapper import EntityMapper, EntityDatabase
from src.entity_mapper.schema import Entity, MappingResult

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'default-dev-key')
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'png', 'jpg', 'jpeg'}

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize components
extractor = None
mapper = None
database = None

def allowed_file(filename):
    """Check if the file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def init_components():
    """Initialize document extractor and entity mapper components."""
    global extractor, mapper, database
    
    # Only initialize if not already done
    if extractor is None:
        logger.info("Initializing components...")
        model = os.environ.get("DEFAULT_MODEL", "gpt-4o")
        db_path = os.environ.get("DB_PATH")
        
        # Initialize entity database
        database = EntityDatabase(Path(db_path) if db_path else None)
        
        # Initialize document extractor
        extractor = DocumentExtractor(
            model=model,
            detail_level="high"
        )
        
        # Initialize entity mapper
        mapper = EntityMapper(
            database=database,
            match_threshold=float(os.environ.get("MATCH_THRESHOLD", "0.85"))
        )
        
        logger.info("Components initialized successfully")

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and process document."""
    # Check if a file was uploaded
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    # If the user did not select a file
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        # Secure the filename to prevent directory traversal attacks
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Save the file
        file.save(file_path)
        
        try:
            # Initialize components if not already done
            init_components()
            
            # Process the document
            result = process_document(Path(file_path))
            
            # Return the result as JSON
            return jsonify(result)
        except Exception as e:
            logger.exception(f"Error processing document: {e}")
            return jsonify({'error': str(e)}), 500
    
    return jsonify({'error': 'File type not allowed'}), 400

@app.route('/results/<filename>')
def results(filename):
    """Display the results page for a specific document."""
    return render_template('results.html', filename=filename)

@app.route('/static/<path:path>')
def serve_static(path):
    """Serve static files."""
    return send_from_directory('static', path)

def process_document(document_path: Path) -> Dict[str, Any]:
    """Process a document and return extraction and mapping results."""
    # Extract entities
    logger.info(f"Extracting entities from {document_path}")
    
    if document_path.suffix.lower() == '.pdf':
        entities = extractor.extract_from_pdf(document_path)
    else:
        entities = extractor.extract_from_image(document_path)
    
    # Map entities
    logger.info(f"Mapping {len(entities)} entities to database")
    mapping_results = mapper.map_entities(entities)
    
    # Create structured result
    filename = document_path.name
    result_dir = Path('results') / document_path.stem
    result_dir.mkdir(parents=True, exist_ok=True)
    
    # Save extracted entities
    entities_file = result_dir / "extracted_entities.json"
    entities_data = [entity.dict() for entity in entities]
    with open(entities_file, "w") as f:
        json.dump(entities_data, f, indent=2)
    
    # Save mapping results
    mapping_file = result_dir / "mapping_results.json"
    mapping_data = [result.dict() for result in mapping_results]
    with open(mapping_file, "w") as f:
        json.dump(mapping_data, f, indent=2)
    
    # Count mapped entities
    mapped_count = sum(1 for result in mapping_results if result.mapped_entity_id is not None)
    
    # Count name changes detected
    name_changes = sum(1 for result in mapping_results if result.name_change_detected)
    
    result = {
        'filename': filename,
        'total_entities': len(entities),
        'mapped_entities': mapped_count,
        'name_changes_detected': name_changes,
        'entities': entities_data,
        'mapping_results': mapping_data
    }
    
    return result

if __name__ == '__main__':
    # Get port from environment or use default
    port = int(os.environ.get('PORT', 5000))
    
    # Run the application
    app.run(host='0.0.0.0', port=port, debug=True) 