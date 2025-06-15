"""
Advanced prompt templates for document extraction using chain-of-thought and few-shot learning.

This module provides specialized prompts for different document types to improve
entity extraction results from vision-enabled LLMs.
"""

import json
from typing import Dict, Any, List, Optional

# Base extraction prompt that uses chain-of-thought reasoning
BASE_EXTRACTION_PROMPT = """
I need to extract structured information from this document for entity mapping. 

Let's think step by step:
1. First, identify what type of document this is based on layout and content
2. Note all company names, including variations and abbreviations used within the document
3. For each company, extract all available information like address, contact details, roles
4. Pay special attention to any indications of company name changes, acquisitions, or parent/subsidiary relationships
5. Also extract named people with their titles and affiliated organizations
6. For shipping documents, identify locations, dates, and shipment details

IMPORTANT: Look carefully for any indications that a company might have changed names, been acquired, 
or have a parent-subsidiary relationship. These relationships might be indicated by phrases like:
- "formerly known as"
- "a division of"
- "a subsidiary of"
- "dba" (doing business as)
- Different names used for the same entity in different sections

Extract ALL entities as structured data in the exact format specified below.
"""

# Document-specific prompt additions
DOCUMENT_TYPE_PROMPTS = {
    "invoice": """
    This appears to be an invoice document. In addition to the standard company and person entities, look for:
    - Invoice number, date, and payment terms
    - Billing and shipping addresses (these may refer to different company locations)
    - Line items with descriptions, quantities, and prices
    - Total amount and currency
    - Reference numbers (PO numbers, BOL numbers, etc.)
    - Any notes or special instructions that might indicate business relationships
    """,
    
    "bill_of_lading": """
    This appears to be a Bill of Lading (BOL). In addition to standard entities, pay special attention to:
    - Shipper information (the company sending the shipment)
    - Carrier information (the transportation company)
    - Consignee information (the company receiving the shipment)
    - Origin and destination addresses
    - BOL number and date
    - Description of goods, weight, and package count
    - Special instructions or routing information
    """,
    
    "rate_confirmation": """
    This appears to be a Rate Confirmation Sheet. In addition to standard entities, focus on:
    - Broker/logistics company information
    - Carrier information (the transportation company)
    - Shipper and consignee information
    - Origin and destination addresses
    - Load details (weight, dimensions, number of pallets)
    - Rate information and additional charges
    - Special instructions or requirements
    """,
    
    "proof_of_delivery": """
    This appears to be a Proof of Delivery (POD). In addition to standard entities, look for:
    - Delivery confirmation details (date, time, signature)
    - Shipper and receiver information
    - Carrier information
    - Item details and quantities received
    - Any discrepancies or damages noted
    - Reference numbers connecting to other documents
    """
}

# Schema examples for different entity types
ENTITY_SCHEMA_EXAMPLES = {
    "company": {
        "name": "Bennett International Logistics, LLC",
        "type": "company",
        "industry": "logistics",
        "aliases": ["BIL", "Bennett Logistics"],
        "address": {
            "street": "PO Box 569",
            "city": "McDonough",
            "state": "GA",
            "postal_code": "30253"
        },
        "contact": {
            "phone": "770-957-1866",
            "fax": "877-251-8541",
            "email": "info@bennettintl.com"
        },
        "parent_company": "Bennett Truck Transport, LLC",
        "description": "Logistics provider specializing in freight management services"
    },
    
    "person": {
        "name": "John Smith",
        "type": "person",
        "title": "Driver",
        "organization": "GT Express Inc",
        "contact": {
            "phone": "555-123-4567",
            "email": "jsmith@gtexpress.com"
        }
    },
    
    "location": {
        "name": "Chicago Distribution Center",
        "type": "location",
        "location_type": "warehouse",
        "address": {
            "street": "123 Logistics Parkway",
            "city": "Chicago",
            "state": "IL",
            "postal_code": "60007"
        },
        "contact": {
            "phone": "312-555-9876"
        }
    },
    
    "shipment": {
        "type": "shipment",
        "reference_numbers": {
            "order_number": "PO-12345",
            "bol_number": "BOL9876543",
            "pro_number": "PRO123456"
        },
        "dates": {
            "pickup": "2023-04-15",
            "delivery": "2023-04-18"
        },
        "origin": "Bennett Manufacturing Plant",
        "destination": "Chicago Distribution Center",
        "carrier": "GT Express Inc",
        "shipper": "Bennett Truck Transport, LLC",
        "consignee": "XYZ Corp",
        "cargo": {
            "description": "Automotive parts",
            "quantity": "15 pallets",
            "weight": "12500 lbs",
            "hazardous": False
        },
        "financial": {
            "total_charges": "$1,875.00",
            "line_haul": "$1,550.00",
            "fuel_surcharge": "$325.00"
        }
    }
}

# Compilation of few-shot examples for different document types
FEW_SHOT_EXAMPLES = {
    "invoice": [
        {
            "document_description": "An invoice from Steve's Trucking to Customer Company with charges for freight transportation services",
            "entities": [
                {
                    "name": "Steve's Trucking",
                    "type": "company",
                    "industry": "trucking",
                    "aliases": ["STC"],
                    "address": {
                        "street": "PO Box 915654",
                        "city": "Kansas City",
                        "state": "MO",
                        "postal_code": "64111"
                    },
                    "contact": {
                        "phone": "888-564-6546"
                    }
                },
                {
                    "name": "Customer Company Inc.",
                    "type": "company",
                    "address": {
                        "street": "7834 18th St.",
                        "city": "Dallas",
                        "state": "TX",
                        "postal_code": "75391"
                    }
                },
                {
                    "type": "shipment",
                    "reference_numbers": {
                        "invoice_number": "INV-86753",
                        "order_number": "ORD-58471"
                    },
                    "dates": {
                        "invoice_date": "2023-03-15",
                        "due_date": "2023-04-15"
                    },
                    "origin": "Kansas City",
                    "destination": "Dallas",
                    "financial": {
                        "total_charges": "$1,250.00",
                        "payment_terms": "Net 30"
                    }
                }
            ]
        }
    ],
    
    "bill_of_lading": [
        {
            "document_description": "A bill of lading from Linbis Logistics Software showing a shipment from ABC Manufacturing to XYZ Distribution",
            "entities": [
                {
                    "name": "Linbis Logistics Software",
                    "type": "company",
                    "industry": "technology",
                    "address": {
                        "street": "5406 NW 72 AVE",
                        "city": "Miami",
                        "state": "FL",
                        "postal_code": "33166"
                    },
                    "contact": {
                        "phone": "305-513-8555",
                        "website": "www.linbis.com"
                    }
                },
                {
                    "name": "ABC Manufacturing",
                    "type": "company",
                    "industry": "manufacturing",
                    "address": {
                        "street": "100 Production Lane",
                        "city": "Detroit",
                        "state": "MI",
                        "postal_code": "48201"
                    }
                },
                {
                    "name": "XYZ Distribution",
                    "type": "company",
                    "industry": "distribution",
                    "address": {
                        "street": "500 Warehouse Blvd",
                        "city": "Cleveland",
                        "state": "OH",
                        "postal_code": "44113"
                    }
                },
                {
                    "type": "shipment",
                    "reference_numbers": {
                        "bol_number": "BOL-478965",
                        "po_number": "PO-7854231"
                    },
                    "dates": {
                        "pickup": "2023-02-10"
                    },
                    "origin": "Detroit, MI",
                    "destination": "Cleveland, OH",
                    "shipper": "ABC Manufacturing",
                    "consignee": "XYZ Distribution",
                    "cargo": {
                        "description": "Electronic components",
                        "quantity": "8 pallets",
                        "weight": "4800 lbs"
                    }
                }
            ]
        }
    ]
}

def generate_extraction_prompt(document_type: str = None, include_examples: bool = True) -> str:
    """
    Generate a specialized prompt for document extraction based on document type.
    
    Args:
        document_type: Type of document (invoice, bill_of_lading, rate_confirmation, proof_of_delivery)
        include_examples: Whether to include few-shot examples
        
    Returns:
        Complete extraction prompt
    """
    prompt = BASE_EXTRACTION_PROMPT
    
    # Add document-specific guidance if available
    if document_type and document_type in DOCUMENT_TYPE_PROMPTS:
        prompt += DOCUMENT_TYPE_PROMPTS[document_type]
    
    # Add schema information
    prompt += "\n\nExtract the data in the following JSON schema format:\n"
    prompt += json.dumps(ENTITY_SCHEMA_EXAMPLES, indent=2)
    
    # Add few-shot examples if requested
    if include_examples and document_type and document_type in FEW_SHOT_EXAMPLES:
        examples = FEW_SHOT_EXAMPLES[document_type]
        prompt += "\n\nHere are some examples of the expected output:\n"
        
        for example in examples:
            prompt += f"\nDocument description: {example['document_description']}\n"
            prompt += f"Extracted entities:\n{json.dumps(example['entities'], indent=2)}\n"
    
    # Add final instruction
    prompt += "\n\nNow, extract all entities from the provided document, following the format above."
    
    return prompt

def generate_document_classification_prompt() -> str:
    """
    Generate a prompt for document type classification.
    
    Returns:
        Document classification prompt
    """
    return """
    Analyze this document and classify it into one of the following categories:
    - invoice
    - bill_of_lading
    - rate_confirmation
    - proof_of_delivery
    - other
    
    Return ONLY the category name (lowercase) and nothing else.
    """

def generate_name_change_detection_prompt() -> str:
    """
    Generate a prompt specifically for detecting company name changes.
    
    Returns:
        Name change detection prompt
    """
    return """
    Analyze this document and identify any evidence of company name changes, acquisitions, 
    mergers, or parent-subsidiary relationships.
    
    Focus on phrases like:
    - "formerly known as"
    - "a division of"
    - "a subsidiary of"
    - "dba" (doing business as)
    - Different names used for the same entity in different sections
    
    For each name change or relationship detected, provide:
    1. Original company name
    2. Current/new company name
    3. Type of relationship (acquisition, subsidiary, rebranding, etc.)
    4. Any date information about when the change occurred
    5. Evidence from the document supporting this relationship
    
    Format the response as a JSON array of objects with these fields.
    
    If no name changes or relationships are detected, return an empty array [].
    """ 