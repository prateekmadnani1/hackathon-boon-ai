"""
Document extraction module that processes images and extracts structured data
using Vision-enabled LLMs.
"""

import os
import logging
import base64
import json
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from io import BytesIO

import numpy as np
from PIL import Image
from pdf2image import convert_from_path
import openai
import google.generativeai as genai
import anthropic

# Add parent directory to path to enable imports
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from src.entity_mapper.schema import (
    Entity, CompanyEntity, PersonEntity, EntityType, Address, ContactInfo,
    ShipmentEntity, ReferenceNumbers, ShipmentDates, CargoDetails, FinancialDetails,
    LocationEntity
)

logger = logging.getLogger(__name__)

class DocumentExtractor:
    """
    Extracts structured information from document images using 
    vision-enabled LLMs.
    """
    
    def __init__(
        self,
        model: str,
        api_key: Optional[str] = None,
        detail_level: str = "high"
    ):
        """
        Initialize document extractor with model and API key.
        
        Args:
            model: Model name to use (e.g., 'gpt-4-vision-preview')
            api_key: OpenAI API key
            detail_level: Level of detail for vision analysis ('high', 'medium', 'low')
        """
        self.model = model
        self.detail_level = detail_level
        
        # Special handling for mock mode
        if model.lower() == 'mock':
            self.client_type = "mock"
            logger.info("Using mock mode - no API call will be made")
        else:
            openai.api_key = api_key or os.environ.get("OPENAI_API_KEY")
            if not openai.api_key:
                raise ValueError("OpenAI API key must be provided")
            self.client_type = "openai"
        
    def extract_from_pdf(self, pdf_path: Union[str, Path]) -> List[Entity]:
        """
        Extract entities from a PDF document.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            List of extracted entities
        """
        # Convert PDF to images
        pdf_path = Path(pdf_path)
        logger.info(f"Processing PDF: {pdf_path}")
        
        # Special handling for mock mode
        if self.client_type == "mock":
            logger.info("Using mock data for PDF processing")
            return self._generate_mock_entities(pdf_path.stem)
        
        # Normal processing for non-mock mode
        images = convert_from_path(pdf_path)
        logger.info(f"Converted PDF to {len(images)} images")
        
        # Process each image
        all_entities = []
        for i, image in enumerate(images):
            logger.info(f"Processing page {i+1}/{len(images)}")
            page_entities = self.extract_from_image(image)
            all_entities.extend(page_entities)
            
        return all_entities
    
    def extract_from_image(self, image: Union[str, Path, Image.Image]) -> List[Entity]:
        """
        Extract entities from an image.
        
        Args:
            image: Path to image file or PIL Image object
            
        Returns:
            List of extracted entities
        """
        # Special handling for mock mode
        if self.client_type == "mock":
            logger.info("Using mock data for image processing")
            # If we have a path, use it to generate appropriate mock entities
            if isinstance(image, (str, Path)):
                image_path = Path(image)
                return self._generate_mock_entities(image_path.stem)
            # Otherwise, just return generic mock entities
            return self._generate_mock_entities()
        
        # Load image if path is provided
        if isinstance(image, (str, Path)):
            image = Image.open(image)
        
        return self._extract_with_openai(image)
    
    def _generate_mock_entities(self, file_stem: Optional[str] = None) -> List[Entity]:
        """Generate mock entities based on the file name or generic ones if not provided."""
        entities = []
        
        # Create entities based on the document name if provided
        if file_stem:
            if "steves" in file_stem.lower() or "freight_invoice" in file_stem.lower():
                # Steve's Trucking freight invoice
                company = CompanyEntity(
                    name="Steve's Trucking",
                    type=EntityType.COMPANY,
                    aliases=["STC"],
                    industry="trucking",
                    address=Address(
                        street="PO Box 915654",
                        city="Kansas City",
                        state="MO",
                        postal_code="64111"
                    ),
                    contact=ContactInfo(
                        phone="(888) 564-6546"
                    )
                )
                
                customer = CompanyEntity(
                    name="Customer Company Name",
                    type=EntityType.COMPANY,
                    address=Address(
                        street="7834 18th St.",
                        city="Dallas",
                        state="TX",
                        postal_code="75391"
                    )
                )
                
                driver = PersonEntity(
                    name="Driver Name",
                    type=EntityType.PERSON,
                    title="Driver",
                    organization="Steve's Trucking"
                )
                
                entities.extend([company, customer, driver])
                
            elif "bennett" in file_stem.lower() or "rate_confirmation" in file_stem.lower():
                # Bennett International Logistics rate confirmation
                company = CompanyEntity(
                    name="Bennett International Logistics, LLC",
                    type=EntityType.COMPANY,
                    aliases=["BIL"],
                    industry="logistics",
                    address=Address(
                        street="PO Box 569",
                        city="McDonough",
                        state="GA",
                        postal_code="30253"
                    ),
                    contact=ContactInfo(
                        phone="770-957-1866",
                        fax="877-251-8541"
                    )
                )
                
                parent_company = CompanyEntity(
                    name="BENNETT TRUCK TRANSPORT, LLC",
                    type=EntityType.COMPANY,
                    industry="trucking"
                )
                
                carrier = CompanyEntity(
                    name="GT XPRESS INC",
                    type=EntityType.COMPANY,
                    industry="trucking",
                    contact=ContactInfo(
                        phone="8773772720"
                    )
                )
                
                driver = PersonEntity(
                    name="MARTY ROWE",
                    type=EntityType.PERSON,
                    title="Driver",
                    organization="GT XPRESS INC",
                    contact=ContactInfo(
                        phone="5174251761"
                    )
                )
                
                origin = CompanyEntity(
                    name="AGRI EMPRESSA",
                    type=EntityType.COMPANY,
                    address=Address(
                        street="6001 W INDUSTRIAL AVE",
                        city="MIDLAND",
                        state="TX",
                        postal_code="79701"
                    )
                )
                
                destination = CompanyEntity(
                    name="IDC 301 CYCLONE EA 23H",
                    type=EntityType.COMPANY,
                    address=Address(
                        street="CR 194",
                        city="SMILEY",
                        state="TX",
                        postal_code="78159"
                    )
                )
                
                entities.extend([company, parent_company, carrier, driver, origin, destination])
                
            elif "linbis" in file_stem.lower() or "bill_of_lading" in file_stem.lower():
                # Linbis Logistics Software bill of lading
                company = CompanyEntity(
                    name="Linbis Logistics Software",
                    type=EntityType.COMPANY,
                    industry="technology",
                    address=Address(
                        street="5406 NW 72 AVE",
                        city="Miami",
                        state="FL",
                        postal_code="33166"
                    ),
                    contact=ContactInfo(
                        phone="(305) 513-8555",
                        fax="(305) 513-8555",
                        email="info@linbis.com",
                        website="www.linbis.com"
                    )
                )
                
                shipper = CompanyEntity(
                    name="Sample Company TFASCLO",
                    type=EntityType.COMPANY,
                    address=Address(
                        street="8551 EAST 88 TH STREET",
                        city="Sample City",
                        state="CA",
                        postal_code="55532"
                    )
                )
                
                consignee = CompanyEntity(
                    name="Sample Company CODE001",
                    type=EntityType.COMPANY,
                    address=Address(
                        street="88185 NW 51th St Unit 811",
                        city="Sample City",
                        state="FL", 
                        postal_code="55532"
                    ),
                    contact=ContactInfo(
                        phone="7866839976"
                    )
                )
                
                carrier = CompanyEntity(
                    name="FEDEX",
                    type=EntityType.COMPANY,
                    industry="shipping"
                )
                
                driver = PersonEntity(
                    name="John Smith",
                    type=EntityType.PERSON,
                    title="Driver",
                    organization="FEDEX"
                )
                
                entities.extend([company, shipper, consignee, carrier, driver])
        
        # If no entities created based on file name, create generic ones
        if not entities:
            # Generic logistics document entities
            company = CompanyEntity(
                name="Example Logistics Corp",
                type=EntityType.COMPANY,
                aliases=["ELC", "Example Logistics"],
                industry="logistics",
                address=Address(
                    street="123 Main St",
                    city="Anytown",
                    state="CA",
                    postal_code="90210"
                ),
                contact=ContactInfo(
                    phone="(555) 123-4567",
                    email="info@examplelogistics.com"
                )
            )
            
            driver = PersonEntity(
                name="John Driver",
                type=EntityType.PERSON,
                title="Driver",
                organization="Example Logistics Corp"
            )
            
            entities.extend([company, driver])
            
        return entities
    
    def _extract_with_openai(self, image: Image.Image) -> List[Entity]:
        """Extract entities using OpenAI's vision models."""
        # Convert image to base64
        buffered = BytesIO()
        
        # Convert RGBA to RGB if needed
        if image.mode == 'RGBA':
            # Create a white background
            background = Image.new('RGB', image.size, (255, 255, 255))
            # Paste the image on the background using the alpha channel
            background.paste(image, mask=image.split()[3])
            image = background
        
        # Save image as JPEG
        image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        
        # Create message with image and more structured prompt
        messages = [
            {
                "role": "system",
                "content": """You are a document analysis system specialized in extracting structured information from logistics documents.
                Extract all entities and format them as a clean JSON object.
                Include ALL information you can find about each entity including addresses, contact info, etc.
                Pay special attention to shipment details, reference numbers, and financials.
                Be thorough and extract every detail present in the document."""
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": """Extract all entities from this logistics document and format as JSON with this structure:
                        {
                          "companies": [
                            {
                              "name": "full company name",
                              "type": "carrier|shipper|consignee|broker",
                              "industry": "type of business",
                              "address": {
                                "street": "full street address",
                                "city": "city name",
                                "state": "state code",
                                "postal_code": "zip code",
                                "country": "country name if present"
                              },
                              "contact": {
                                "phone": "phone numbers",
                                "fax": "fax numbers",
                                "email": "email addresses",
                                "website": "website url"
                              },
                              "identifiers": {
                                "mc_number": "MC number if present",
                                "dot_number": "DOT number if present",
                                "scac": "SCAC code if present"
                              }
                            }
                          ],
                          "people": [
                            {
                              "name": "full person name",
                              "title": "job title or role",
                              "organization": "associated company",
                              "contact": {
                                "phone": "phone number",
                                "email": "email address"
                              }
                            }
                          ],
                          "shipment": {
                            "reference_numbers": {
                              "order_number": "order/reference numbers",
                              "bol_number": "bill of lading number",
                              "tracking_number": "tracking numbers",
                              "pro_number": "PRO number if present",
                              "load_number": "load number if present"
                            },
                            "dates": {
                              "pickup": "pickup date",
                              "delivery": "delivery date",
                              "created": "document creation date",
                              "estimated_delivery": "estimated delivery date"
                            },
                            "locations": {
                              "origin": {
                                "name": "origin location name",
                                "address": {
                                  "street": "street address",
                                  "city": "city name",
                                  "state": "state code",
                                  "postal_code": "zip code"
                                }
                              },
                              "destination": {
                                "name": "destination location name", 
                                "address": {
                                  "street": "street address",
                                  "city": "city name",
                                  "state": "state code",
                                  "postal_code": "zip code"
                                }
                              }
                            },
                            "cargo": {
                              "description": "cargo description",
                              "quantity": "number of items",
                              "weight": "weight with units",
                              "dimensions": "dimensions with units",
                              "hazardous": true or false,
                              "special_instructions": "special handling instructions"
                            },
                            "financial": {
                              "total_charges": "total amount",
                              "line_haul": "line haul charges",
                              "fuel_surcharge": "fuel surcharge amount",
                              "additional_charges": {
                                "name of charge": "amount"
                              },
                              "payment_terms": "payment terms",
                              "currency": "currency code"
                            },
                            "status": "current shipment status",
                            "document_type": "type of document (BOL, invoice, etc.)"
                          }
                        }"""
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{img_str}",
                            "detail": self.detail_level
                        }
                    }
                ]
            }
        ]
        
        # Call API with JSON response format
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=2000,
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        
        # Parse response
        content = response.choices[0].message.content
        return self._parse_response(content)
    
    def _parse_response(self, response_content: str) -> List[Entity]:
        """
        Parse LLM response into structured entities.
        
        Args:
            response_content: JSON string from LLM
            
        Returns:
            List of structured entities
        """
        try:
            data = json.loads(response_content)
            entities = []
            
            # Process companies
            for company_data in data.get("companies", []):
                address_data = company_data.get("address", {})
                contact_data = company_data.get("contact", {})
                identifiers_data = company_data.get("identifiers", {})
                
                company = CompanyEntity(
                    name=company_data.get("name"),
                    type=EntityType.COMPANY,
                    industry=company_data.get("industry"),
                    address=Address(
                        street=address_data.get("street"),
                        city=address_data.get("city"),
                        state=address_data.get("state"),
                        postal_code=address_data.get("postal_code"),
                        country=address_data.get("country")
                    ),
                    contact=ContactInfo(
                        phone=contact_data.get("phone"),
                        email=contact_data.get("email"),
                        fax=contact_data.get("fax"),
                        website=contact_data.get("website")
                    ),
                    identifiers={
                        "mc_number": identifiers_data.get("mc_number"),
                        "dot_number": identifiers_data.get("dot_number"),
                        "scac": identifiers_data.get("scac")
                    }
                )
                entities.append(company)
            
            # Process people
            for person_data in data.get("people", []):
                contact_data = person_data.get("contact", {})
                person = PersonEntity(
                    name=person_data.get("name"),
                    type=EntityType.PERSON,
                    title=person_data.get("title"),
                    organization=person_data.get("organization"),
                    contact=ContactInfo(
                        phone=contact_data.get("phone"),
                        email=contact_data.get("email")
                    )
                )
                entities.append(person)
            
            # Process shipment data - create LocationEntity objects for origin and destination
            shipment_data = data.get("shipment", {})
            locations_data = shipment_data.get("locations", {})
            
            origin_location = None
            destination_location = None
            
            for location_type in ["origin", "destination"]:
                location_data = locations_data.get(location_type, {})
                if location_data and location_data.get("name"):
                    address_data = location_data.get("address", {})
                    location = LocationEntity(
                        name=location_data.get("name"),
                        type=EntityType.LOCATION,
                        location_type=location_type,
                        address=Address(
                            street=address_data.get("street"),
                            city=address_data.get("city"),
                            state=address_data.get("state"),
                            postal_code=address_data.get("postal_code"),
                            country=address_data.get("country")
                        )
                    )
                    entities.append(location)
                    
                    if location_type == "origin":
                        origin_location = location.name
                    else:
                        destination_location = location.name
            
            # Create a shipment entity if we have reference numbers or dates
            reference_data = shipment_data.get("reference_numbers", {})
            dates_data = shipment_data.get("dates", {})
            cargo_data = shipment_data.get("cargo", {})
            financial_data = shipment_data.get("financial", {})
            
            # Only create a shipment if we have meaningful data
            if reference_data or dates_data or cargo_data or financial_data:
                # Identify carrier, shipper, consignee from companies
                carrier_name = None
                shipper_name = None
                consignee_name = None
                
                for company in entities:
                    if isinstance(company, CompanyEntity):
                        company_type = company.attributes.get("company_type", "").lower()
                        if "type" in company_data and isinstance(company_data["type"], str):
                            company_type = company_data["type"].lower()
                            
                        if company_type == "carrier":
                            carrier_name = company.name
                        elif company_type == "shipper":
                            shipper_name = company.name
                        elif company_type == "consignee":
                            consignee_name = company.name
                
                # Create the shipment entity
                shipment = ShipmentEntity(
                    name=f"Shipment {reference_data.get('bol_number') or reference_data.get('order_number') or 'Unknown'}",
                    type=EntityType.SHIPMENT,
                    reference_numbers=ReferenceNumbers(
                        order_number=reference_data.get("order_number"),
                        bol_number=reference_data.get("bol_number"),
                        tracking_number=reference_data.get("tracking_number"),
                        pro_number=reference_data.get("pro_number"),
                        load_number=reference_data.get("load_number"),
                        carrier_reference=reference_data.get("carrier_reference")
                    ),
                    dates=ShipmentDates(
                        pickup=dates_data.get("pickup"),
                        delivery=dates_data.get("delivery"),
                        created=dates_data.get("created"),
                        estimated_delivery=dates_data.get("estimated_delivery")
                    ),
                    origin=origin_location,
                    destination=destination_location,
                    carrier=carrier_name,
                    shipper=shipper_name,
                    consignee=consignee_name,
                    cargo=CargoDetails(
                        description=cargo_data.get("description"),
                        quantity=cargo_data.get("quantity"),
                        weight=cargo_data.get("weight"),
                        dimensions=cargo_data.get("dimensions"),
                        hazardous=cargo_data.get("hazardous", False),
                        special_instructions=cargo_data.get("special_instructions")
                    ),
                    financial=FinancialDetails(
                        total_charges=financial_data.get("total_charges"),
                        line_haul=financial_data.get("line_haul"),
                        fuel_surcharge=financial_data.get("fuel_surcharge"),
                        additional_charges=financial_data.get("additional_charges", {}),
                        payment_terms=financial_data.get("payment_terms"),
                        currency=financial_data.get("currency")
                    ),
                    status=shipment_data.get("status"),
                    document_type=shipment_data.get("document_type")
                )
                entities.append(shipment)
            
            return entities
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response: {e}")
            logger.debug(f"Response content: {response_content}")
            return []
