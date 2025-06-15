# Boon AI Hackathon: Document Processing & Entity Mapping

A solution for extracting structured data from shipping and logistics documents and mapping entities to a database, with advanced handling of renamed or acquired entities.

## Project Overview

This project provides an AI-powered system that:
1. Extracts structured data from transportation and logistics documents (invoices, bills of lading, etc.)
2. Maps extracted entities to a database using advanced fuzzy matching techniques
3. Detects company name changes and corporate relationships
4. Provides both a command-line interface and a web-based visualization tool

## Prerequisites

- Python 3.9+ 
- [Poppler](https://poppler.freedesktop.org/) for PDF processing:
  - Mac: `brew install poppler`
  - Ubuntu/Debian: `apt-get install poppler-utils`
  - Windows: Download from [poppler-windows](https://github.com/oschwartz10612/poppler-windows/releases/)

## Quick Setup

1. Clone the repository:
```bash
git clone https://github.com/bennysun1/boon-hackathon-entity-mapping.git
cd boon-hackathon-entity-mapping
```

2. Create and activate a virtual environment:
```bash
# On Linux/Mac:
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# On Windows:
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Alternatively, use the setup scripts:
# Linux/Mac:
bash setup.sh

# Windows:
setup.bat
```

3. Configure your API keys in the `.env` file:
```
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
```

4. Ensure proper file types for example documents:
```bash
# Check your PDF files to ensure they are actually PDFs and not images with .pdf extensions
# If using image files, ensure they have the correct file extension (.jpg, .png)
```

## Running the Web Interface

The web interface provides an easy way to upload and process documents:

```bash
# On Linux/Mac:
./run_demo_web.sh

# On Windows:
run_demo_web.bat
```

This will start a web server at http://localhost:8080 where you can:
1. Upload documents (PDF, JPG, PNG)
2. View extracted entities and mapping results in real-time
3. See summary statistics and visualizations

### Troubleshooting Web Demo Issues

- **Port conflict:** If port 8080 is already in use, edit the `PORT` variable in `run_demo_web.sh` or `run_demo_web.bat`
- **PDF processing errors:** Ensure Poppler is correctly installed and in your PATH
- **File type issues:** Make sure your PDFs are genuine PDF files, not images with .pdf extensions

## Command-Line Interface

For batch processing or automation, use the command-line interface:

```bash
python src/main.py process data/examples --output results
```

Command-line options:
```
--output-dir TEXT            Directory to save results
--model TEXT                 LLM model to use for extraction [default: gpt-4o]
--detail-level TEXT          Detail level for vision models (high, medium, low) [default: high]
--db-path TEXT               Path to entity database JSON file
--match-threshold FLOAT      Threshold for entity matching confidence [default: 0.85]
-v, --verbose                Enable verbose output
```

## Demo Documents

The project includes example documents in `data/examples/`:

1. **Bill of Lading (bol_example.pdf)** - Contains shipper, carrier, and consignee information
2. **Invoice (invoice.png)** - Shows shipping transaction with customer details and rates
3. **Rate Confirmation (rate_confirmation.png)** - Displays carrier details and load information

These documents demonstrate entity mapping challenges, including company name variations, abbreviations, and corporate relationships.

## Project Structure

```
boon-hackathon-entity-mapping/
├── data/
│   ├── db/                # Mock entity database
│   ├── examples/          # Example documents
│   └── uploads/           # Storage for web uploads
├── src/
│   ├── document_processor/ # Document extraction modules
│   │   ├── extractor.py    # Main document processing
│   │   └── prompt_templates.py # LLM prompts for extraction
│   ├── entity_mapper/     # Entity mapping modules
│   │   ├── mapper.py      # Core entity mapping logic
│   │   ├── schema.py      # Data models and schemas
│   │   └── enhanced_matching.py # Advanced matching algorithms
│   ├── templates/         # Web interface HTML templates
│   ├── static/            # CSS and JavaScript for web interface
│   ├── app.py             # Web application entry point
│   └── main.py            # CLI application entry point
├── results/               # Output directory for processed results
├── requirements.txt       # Python dependencies
├── run_demo_web.sh/.bat   # Web interface startup scripts
├── setup.sh/.bat          # Environment setup scripts
└── README.md              # This documentation
```

## Implementation Details

The solution uses a multi-stage approach:

1. **Document Processing:**
   - Uses vision-enabled LLMs (GPT-4o by default) to extract entities from documents
   - Specialized prompts for different document types improve extraction quality

2. **Entity Mapping:**
   - Advanced fuzzy matching algorithms using multiple similarity metrics
   - Name change detection for company rebranding and acquisitions
   - Confidence scores for each mapping

3. **Web Interface:**
   - Flask-based web application for easy document uploading
   - Real-time visualization of extraction and mapping results

## Future Implementations

Future enhancements to this project could include:

1. **Database Integration:**
   - Connect to a real database instead of the mock database
   - Support for SQL, MongoDB, or other database systems

2. **Enhanced Visualization:**
   - Interactive network graphs showing entity relationships
   - Timeline view for tracking entity changes over time

3. **Batch Processing:**
   - Support for processing folders of documents
   - Automated workflow for regular document ingestion

4. **API Improvements:**
   - REST API for integration with other systems
   - Streaming responses for large document batches

5. **Model Optimization:**
   - Fine-tuning LLMs for specific document types
   - Implementing local models for lower latency and cost

6. **Security Enhancements:**
   - User authentication and access control
   - Document encryption for sensitive information

7. **Feedback Loop:**
   - User correction of mapping errors
   - Learning from corrections to improve future mappings

## License

[MIT License]

## Acknowledgments

Developed for the Boon AI Hackathon.
