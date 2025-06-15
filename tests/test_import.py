"""
Simple test to make sure all modules can be imported correctly.
"""

import os
import sys
import unittest

# Add the src directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class ImportTest(unittest.TestCase):
    """Test that all modules can be imported correctly."""
    
    def test_document_processor_imports(self):
        """Test importing document processor modules."""
        from src.document_processor.extractor import DocumentExtractor
        self.assertTrue(DocumentExtractor)
    
    def test_entity_mapper_imports(self):
        """Test importing entity mapper modules."""
        from src.entity_mapper.mapper import EntityMapper, EntityDatabase
        from src.entity_mapper.schema import Entity, CompanyEntity
        self.assertTrue(EntityMapper)
        self.assertTrue(EntityDatabase)
        self.assertTrue(Entity)
        self.assertTrue(CompanyEntity)
    
    def test_main_imports(self):
        """Test importing the main module."""
        import src.main
        self.assertTrue(src.main)


if __name__ == '__main__':
    unittest.main()
