"""
Entity mapper module for matching extracted entities with database records.
"""

import os
import logging
import json
from typing import List, Dict, Any, Optional, Tuple, Union
from pathlib import Path

from rapidfuzz import fuzz, process
from pydantic import BaseModel

from .schema import Entity, CompanyEntity, NameChange, MappingResult

logger = logging.getLogger(__name__)

class EntityDatabase:
    """Mock database of entities for the hackathon."""
    
    def __init__(self, db_path: Optional[Union[str, Path]] = None):
        """
        Initialize the entity database.
        
        Args:
            db_path: Optional path to JSON database file
        """
        self.entities = []
        self.name_changes = []
        
        # Load database if path provided
        if db_path:
            self.load_from_file(db_path)
        else:
            # Create mock data
            self._create_mock_data()
    
    def load_from_file(self, file_path: Union[str, Path]) -> None:
        """Load entity database from a JSON file."""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                self.entities = data.get('entities', [])
                self.name_changes = data.get('name_changes', [])
        except Exception as e:
            logger.error(f"Failed to load database: {e}")
            # Fall back to mock data
            self._create_mock_data()
    
    def _create_mock_data(self) -> None:
        """Create mock entity database for demonstration."""
        # Mock companies with known name changes
        self.entities = [
            {
                "id": "comp001",
                "name": "Bennett Truck Transport, LLC",
                "type": "company",
                "industry": "trucking",
                "aliases": ["Bennett", "BTT"],
                "address": {
                    "street": "PO Box 569",
                    "city": "McDonough",
                    "state": "GA",
                    "postal_code": "30253"
                },
                "contact": {
                    "phone": "770-957-1866",
                    "fax": "877-251-8541"
                }
            },
            {
                "id": "comp002",
                "name": "Road Masters Transportation",
                "type": "company",
                "industry": "logistics",
                "aliases": ["Road Masters", "RM Transport"],
                "address": {
                    "city": "McDonough",
                    "state": "GA"
                }
            },
            {
                "id": "comp003",
                "name": "Bennett International Logistics, LLC",
                "type": "company",
                "industry": "logistics",
                "parent_company": "comp001",
                "aliases": ["BIL", "Bennett International"],
                "address": {
                    "city": "McDonough",
                    "state": "GA",
                    "postal_code": "30253"
                },
                "contact": {
                    "phone": "770-957-1866",
                    "fax": "877-251-8541"
                }
            },
            {
                "id": "comp004",
                "name": "Steve Trucking Company",
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
                "id": "comp005",
                "name": "GT Express Incorporated",
                "type": "company", 
                "industry": "trucking",
                "aliases": ["GT Express", "GTE"],
                "contact": {
                    "phone": "877-377-2720"
                }
            },
            {
                "id": "comp006",
                "name": "Linbis Logistics Software",
                "type": "company",
                "industry": "technology",
                "aliases": ["Linbis", "LLS"],
                "address": {
                    "street": "5406 NW 72 AVE",
                    "city": "Miami",
                    "state": "FL",
                    "postal_code": "33166"
                },
                "contact": {
                    "phone": "305-513-8555",
                    "fax": "305-513-8555",
                    "email": "info@linbis.com",
                    "website": "www.linbis.com"
                }
            }
        ]
        
        # Mock name changes
        self.name_changes = [
            {
                "previous_name": "Steve's Trucking",
                "current_name": "Steve Trucking Company",
                "entity_id": "comp004",
                "change_date": "2020-01-15",
                "change_reason": "rebranding"
            },
            {
                "previous_name": "GT XPRESS INC",
                "current_name": "GT Express Incorporated",
                "entity_id": "comp005",
                "change_date": "2018-06-30",
                "change_reason": "acquisition"
            },
            {
                "previous_name": "Bennett Logistics International",
                "current_name": "Bennett International Logistics, LLC",
                "entity_id": "comp003",
                "change_date": "2017-11-01",
                "change_reason": "restructuring"
            }
        ]
    
    def search_by_name(self, name: str, threshold: float = 0.8) -> List[Dict]:
        """
        Search for entities by name with fuzzy matching.
        
        Args:
            name: Name to search for
            threshold: Similarity threshold (0-1)
            
        Returns:
            List of matching entities
        """
        results = []
        
        # Check direct matches with current names
        direct_matches = []
        for entity in self.entities:
            # Check exact match
            if entity["name"].lower() == name.lower():
                direct_matches.append((entity, 1.0))
                continue
                
            # Check aliases
            for alias in entity.get("aliases", []):
                if alias.lower() == name.lower():
                    direct_matches.append((entity, 1.0))
                    break
        
        # Add direct matches to results
        for entity, score in direct_matches:
            results.append({
                "entity": entity,
                "score": score,
                "name_change": None
            })
        
        # If we have direct matches, return them
        if direct_matches:
            return results
        
        # Check for name changes
        for change in self.name_changes:
            if change["previous_name"].lower() == name.lower():
                # Find the current entity
                for entity in self.entities:
                    if entity["id"] == change["entity_id"]:
                        results.append({
                            "entity": entity,
                            "score": 1.0,
                            "name_change": change
                        })
                        break
        
        # If we have exact name change matches, return them
        if results:
            return results
        
        # Perform fuzzy matching on current names
        for entity in self.entities:
            score = fuzz.ratio(entity["name"].lower(), name.lower()) / 100
            if score >= threshold:
                results.append({
                    "entity": entity,
                    "score": score,
                    "name_change": None
                })
                continue
                
            # Check aliases with fuzzy matching
            for alias in entity.get("aliases", []):
                alias_score = fuzz.ratio(alias.lower(), name.lower()) / 100
                if alias_score > score and alias_score >= threshold:
                    results.append({
                        "entity": entity,
                        "score": alias_score,
                        "name_change": None
                    })
                    break
        
        # Perform fuzzy matching on previous names
        for change in self.name_changes:
            score = fuzz.ratio(change["previous_name"].lower(), name.lower()) / 100
            if score >= threshold:
                # Find the current entity
                for entity in self.entities:
                    if entity["id"] == change["entity_id"]:
                        results.append({
                            "entity": entity,
                            "score": score,
                            "name_change": change
                        })
                        break
        
        # Sort results by score (descending)
        results.sort(key=lambda x: x["score"], reverse=True)
        
        return results


class EntityMapper:
    """Maps extracted entities to database records."""
    
    def __init__(
        self,
        database: Optional[EntityDatabase] = None,
        match_threshold: float = 0.85,
        enable_fuzzy_matching: bool = True
    ):
        """
        Initialize the entity mapper.
        
        Args:
            database: Optional EntityDatabase instance
            match_threshold: Minimum similarity score to consider a match
            enable_fuzzy_matching: Whether to enable fuzzy matching
        """
        self.database = database or EntityDatabase()
        self.match_threshold = match_threshold
        self.enable_fuzzy_matching = enable_fuzzy_matching
    
    def map_entity(self, entity: Entity) -> MappingResult:
        """
        Map a single entity to the database.
        
        Args:
            entity: Entity to map
            
        Returns:
            MappingResult object with mapping information
        """
        # Only try to map company entities for now
        if not isinstance(entity, CompanyEntity):
            return MappingResult(
                original_entity=entity,
                confidence=0.0
            )
        
        # Search for matches
        matches = self.database.search_by_name(
            entity.name,
            threshold=self.match_threshold if self.enable_fuzzy_matching else 1.0
        )
        
        if not matches:
            return MappingResult(
                original_entity=entity,
                confidence=0.0
            )
        
        # Get best match
        best_match = matches[0]
        entity_match = best_match["entity"]
        name_change = best_match["name_change"]
        
        # Create result
        result = MappingResult(
            original_entity=entity,
            mapped_entity_id=entity_match["id"],
            mapped_entity_name=entity_match["name"],
            confidence=best_match["score"],
            name_change_detected=name_change is not None
        )
        
        # Add name change if detected
        if name_change:
            result.name_change = NameChange(
                previous_name=name_change["previous_name"],
                current_name=name_change["current_name"],
                change_date=name_change.get("change_date"),
                change_reason=name_change.get("change_reason")
            )
        
        return result
    
    def map_entities(self, entities: List[Entity]) -> List[MappingResult]:
        """
        Map a list of entities to the database.
        
        Args:
            entities: List of entities to map
            
        Returns:
            List of MappingResult objects
        """
        results = []
        
        for entity in entities:
            result = self.map_entity(entity)
            results.append(result)
        
        return results
