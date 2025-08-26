"""
Unit tests for QuantityDataLoader component.
"""

import json
import os
import tempfile
import unittest
from unittest.mock import patch, mock_open

from config_generator.quantity_data_loader import QuantityDataLoader, QuantityDataLoaderError
from config_generator.models import QuantityAnalysisData, SheetData, HeaderPosition, FontInfo


class TestQuantityDataLoader(unittest.TestCase):
    """Test cases for QuantityDataLoader class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.loader = QuantityDataLoader()
        
        # Valid test data
        self.valid_data = {
            "file_path": "test_file.xlsx",
            "timestamp": "2025-07-19T16:08:19.374269",
            "sheets": [
                {
                    "sheet_name": "Contract",
                    "header_font": {"name": "Times New Roman", "size": 10.0},
                    "data_font": {"name": "Times New Roman", "size": 10.0},
                    "start_row": 18,
                    "header_positions": [
                        {"keyword": "Cargo Description", "row": 17, "column": 1},
                        {"keyword": "HL ITEM", "row": 17, "column": 2}
                    ]
                }
            ]
        }
    
    def test_load_quantity_data_success(self):
        """Test successful loading of valid quantity data."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            json.dump(self.valid_data, temp_file)
            temp_file_path = temp_file.name
        
        try:
            result = self.loader.load_quantity_data(temp_file_path)
            self.assertIsInstance(result, QuantityAnalysisData)
            self.assertEqual(result.file_path, "test_file.xlsx")
            self.assertEqual(len(result.sheets), 1)
        finally:
            os.unlink(temp_file_path)
    
    def test_load_quantity_data_file_not_found(self):
        """Test error handling when file doesn't exist."""
        with self.assertRaises(QuantityDataLoaderError) as context:
            self.loader.load_quantity_data("nonexistent_file.json")
        self.assertIn("File not found", str(context.exception))
    
    def test_validate_structure_success(self):
        """Test successful structure validation."""
        result = self.loader.validate_structure(self.valid_data)
        self.assertTrue(result)


    def test_load_quantity_data_invalid_json(self):
        """Test error handling for invalid JSON format."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            temp_file.write("{ invalid json content")
            temp_file_path = temp_file.name
        
        try:
            with self.assertRaises(QuantityDataLoaderError) as context:
                self.loader.load_quantity_data(temp_file_path)
            self.assertIn("Invalid JSON format", str(context.exception))
        finally:
            os.unlink(temp_file_path)
    
    def test_validate_structure_missing_root_field(self):
        """Test validation failure for missing root fields."""
        invalid_data = self.valid_data.copy()
        del invalid_data['file_path']
        
        with self.assertRaises(QuantityDataLoaderError) as context:
            self.loader.validate_structure(invalid_data)
        self.assertIn("Missing required field: file_path", str(context.exception))
    
    def test_validate_structure_invalid_font_structure(self):
        """Test validation failure for invalid font structure."""
        invalid_data = self.valid_data.copy()
        invalid_data['sheets'][0]['header_font'] = "not a dictionary"
        
        with self.assertRaises(QuantityDataLoaderError) as context:
            self.loader.validate_structure(invalid_data)
        self.assertIn("header_font must be a dictionary", str(context.exception))
    
    def test_validate_structure_invalid_header_position(self):
        """Test validation failure for invalid header position structure."""
        invalid_data = self.valid_data.copy()
        invalid_data['sheets'][0]['header_positions'][0] = "not a dictionary"
        
        with self.assertRaises(QuantityDataLoaderError) as context:
            self.loader.validate_structure(invalid_data)
        self.assertIn("header_position 0 must be a dictionary", str(context.exception))
    
    def test_load_real_quantity_data(self):
        """Test loading the actual quantity_mode_analysis.json file."""
        if os.path.exists("quantity_mode_analysis.json"):
            result = self.loader.load_quantity_data("quantity_mode_analysis.json")
            self.assertIsInstance(result, QuantityAnalysisData)
            self.assertEqual(len(result.sheets), 3)


if __name__ == '__main__':
    unittest.main()