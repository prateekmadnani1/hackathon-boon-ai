from typing import List, Dict, Optional, Any, Literal
from enum import Enum
from pydantic import BaseModel, Field


class EntityType(str, Enum):
    """Types of entities that can be extracted from documents."""
    COMPANY = "company"
    PERSON = "person"
    LOCATION = "location"
    CONTACT = "contact"
    PRODUCT = "product"
    SERVICE = "service"
    SHIPMENT = "shipment"
    OTHER = "other"


class NameChange(BaseModel):
    """Represents a name change or alias for an entity."""
    previous_name: str = Field(..., description="Previous name of the entity")
    current_name: str = Field(..., description="Current name of the entity")
    change_date: Optional[str] = Field(None, description="Date when the name change occurred")
    change_reason: Optional[str] = Field(None, description="Reason for name change (acquisition, rebranding)")
    confidence: float = Field(default=1.0, description="Confidence score for this mapping")


class Address(BaseModel):
    """Structured representation of an address."""
    full_address: Optional[str] = Field(None, description="Complete address as a single string")
    street: Optional[str] = Field(None, description="Street address")
    city: Optional[str] = Field(None, description="City")
    state: Optional[str] = Field(None, description="State or province")
    postal_code: Optional[str] = Field(None, description="ZIP or postal code")
    country: Optional[str] = Field(None, description="Country")


class ContactInfo(BaseModel):
    """Contact information for an entity."""
    email: Optional[str] = Field(None, description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    website: Optional[str] = Field(None, description="Website URL")


class Entity(BaseModel):
    """Base model for extracted entities."""
    id: Optional[str] = Field(None, description="Unique identifier for the entity")
    name: str = Field(..., description="Primary name of the entity")
    type: EntityType = Field(..., description="Type of entity")
    aliases: List[str] = Field(default_factory=list, description="Alternative names or abbreviations")
    description: Optional[str] = Field(None, description="Brief description of the entity")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Additional attributes")
    confidence: float = Field(default=1.0, description="Confidence score for extraction")


class CompanyEntity(Entity):
    """Model for extracted company entities."""
    type: Literal[EntityType.COMPANY] = EntityType.COMPANY
    industry: Optional[str] = Field(None, description="Industry or sector")
    founding_date: Optional[str] = Field(None, description="Company founding date")
    address: Optional[Address] = Field(None, description="Company address")
    contact: Optional[ContactInfo] = Field(None, description="Contact information")
    name_changes: List[NameChange] = Field(default_factory=list, description="History of name changes")
    parent_company: Optional[str] = Field(None, description="Parent company name, if any")
    subsidiaries: List[str] = Field(default_factory=list, description="Subsidiary companies, if any")


class PersonEntity(Entity):
    """Model for extracted person entities."""
    type: Literal[EntityType.PERSON] = EntityType.PERSON
    title: Optional[str] = Field(None, description="Job title or role")
    organization: Optional[str] = Field(None, description="Affiliated organization")
    contact: Optional[ContactInfo] = Field(None, description="Contact information")


class ReferenceNumbers(BaseModel):
    """Reference numbers for a shipment."""
    order_number: Optional[str] = Field(None, description="Order or reference number")
    bol_number: Optional[str] = Field(None, description="Bill of lading number")
    tracking_number: Optional[str] = Field(None, description="Tracking number")
    pro_number: Optional[str] = Field(None, description="PRO number")
    load_number: Optional[str] = Field(None, description="Load number")
    carrier_reference: Optional[str] = Field(None, description="Carrier's reference number")


class ShipmentDates(BaseModel):
    """Important dates for a shipment."""
    pickup: Optional[str] = Field(None, description="Pickup or collection date")
    delivery: Optional[str] = Field(None, description="Delivery date")
    created: Optional[str] = Field(None, description="Date the shipment was created or booked")
    estimated_delivery: Optional[str] = Field(None, description="Estimated delivery date")


class CargoDetails(BaseModel):
    """Details about the cargo being shipped."""
    description: Optional[str] = Field(None, description="Description of the cargo")
    quantity: Optional[str] = Field(None, description="Quantity of items")
    weight: Optional[str] = Field(None, description="Weight of the cargo")
    dimensions: Optional[str] = Field(None, description="Dimensions of the cargo")
    hazardous: bool = Field(default=False, description="Whether the cargo is hazardous")
    special_instructions: Optional[str] = Field(None, description="Special handling instructions")


class FinancialDetails(BaseModel):
    """Financial details for a shipment."""
    total_charges: Optional[str] = Field(None, description="Total charges for the shipment")
    line_haul: Optional[str] = Field(None, description="Line haul charges")
    fuel_surcharge: Optional[str] = Field(None, description="Fuel surcharge")
    additional_charges: Dict[str, str] = Field(default_factory=dict, description="Additional charges with descriptions")
    payment_terms: Optional[str] = Field(None, description="Payment terms")
    currency: Optional[str] = Field(None, description="Currency used for financial amounts")


class LocationEntity(Entity):
    """Model for location entities (pickup/delivery points)."""
    type: Literal[EntityType.LOCATION] = EntityType.LOCATION
    address: Optional[Address] = Field(None, description="Location address")
    contact: Optional[ContactInfo] = Field(None, description="Contact information")
    location_type: Optional[str] = Field(None, description="Type of location (warehouse, terminal, etc.)")


class ShipmentEntity(Entity):
    """Model for shipment entities."""
    type: Literal[EntityType.SHIPMENT] = EntityType.SHIPMENT
    reference_numbers: Optional[ReferenceNumbers] = Field(None, description="Reference numbers for the shipment")
    dates: Optional[ShipmentDates] = Field(None, description="Important dates for the shipment")
    origin: Optional[str] = Field(None, description="Origin entity name")
    destination: Optional[str] = Field(None, description="Destination entity name")
    carrier: Optional[str] = Field(None, description="Carrier entity name")
    shipper: Optional[str] = Field(None, description="Shipper entity name")
    consignee: Optional[str] = Field(None, description="Consignee entity name")
    cargo: Optional[CargoDetails] = Field(None, description="Details about the cargo")
    financial: Optional[FinancialDetails] = Field(None, description="Financial details")
    status: Optional[str] = Field(None, description="Current status of the shipment")
    document_type: Optional[str] = Field(None, description="Type of document (BOL, freight invoice, etc.)")


class MappingResult(BaseModel):
    """Result of entity mapping process."""
    original_entity: Entity
    mapped_entity_id: Optional[str] = Field(None, description="ID of the mapped entity in database")
    mapped_entity_name: Optional[str] = Field(None, description="Name of the mapped entity in database")
    confidence: float = Field(default=0.0, description="Confidence score for this mapping")
    name_change_detected: bool = Field(default=False, description="Whether a name change was detected")
    name_change: Optional[NameChange] = Field(None, description="Name change details if detected")
