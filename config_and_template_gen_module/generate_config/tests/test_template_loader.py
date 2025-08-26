"""
Unit tests for the TemplateLoader component.

This module contains comprehensive tests for template loading functionality,
including validation of valid templates and error handling for invalid ones.
"""

import json
import os
import tempfile
import unittest
from unittest.mock import patch, mock_open

from config_generator.template_loader import TemplateLoader, TemplateLoaderError
from config_generator.models import ConfigurationData, SheetConfig, HeaderEntry


class TestTemplateLoader(unittest.TestCase):
    """Test cases for the TemplateLoader class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.loader = TemplateLoader()
        
        # Valid template structure for testing
        self.valid_template = {
            "sheets_to_process": ["Invoice", "Contract", "Packing list"],
            "sheet_data_map": {
                "Invoice": "aggregation",
                "Contract": "aggregation",
                "Packing list": "processed_tables_multi"
            },
            "data_mapping": {
                "Invoice": {
                    "start_row": 20,
                    "header_to_write": [
                        {"row": 0, "col": 0, "text": "Mark & Nº", "id": "col_static", "rowspan": 1},
                        {"row": 0, "col": 1, "text": "P.O. Nº", "id": "col_po", "rowspan": 1}
                    ],
                    "mappings": {"po": {"key_index": 0, "id": "col_po"}},
                    "footer_configurations": {"total_text": "TOTAL OF:"},
                    "styling": {"default_font": {"name": "Times New Roman", "size": 12}}
                },
                "Contract": {
                    "start_row": 15,
                    "header_to_write": [
                        {"row": 0, "col": 0, "text": "No.", "id": "col_no", "rowspan": 1}
                    ],
                    "mappings": {"po": {"key_index": 0, "id": "col_po"}},
                    "footer_configurations": {"total_text": "TOTAL OF:"},
                    "styling": {"default_font": {"name": "Times New Roman", "size": 14}}
                },
                "Packing list": {
                    "start_row": 19,
                    "header_to_write": [
                        {"row": 0, "col": 0, "text": "Mark & Nº", "id": "col_static", "rowspan": 2},
                        {"row": 1, "col": 5, "text": "PCS", "id": "col_qty_pcs"}
                    ],
                    "mappings": {"data_map": {"po": {"id": "col_po"}}},
                    "footer_configurations": {"total_text": "TOTAL OF:"},
                    "styling": {"default_font": {"name": "Times New Roman", "size": 12}}
                }
            }
        }
    
    def test_load_template_success(self):
        """Test successful template loading."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            json.dump(self.valid_template, temp_file)
            temp_file_path = temp_file.name
        
        try:
            result = self.loader.load_template(temp_file_path)
            self.assertEqual(result, self.valid_template)
        finally:
            os.unlink(temp_file_path)
    
    def test_load_template_file_not_found(self):
        """Test error handling when template file doesn't exist."""
        with self.assertRaises(TemplateLoaderError) as context:
            self.loader.load_template("nonexistent_file.json")
        
        self.assertIn("Template file not found", str(context.exception))
    
    def test_load_template_empty_path(self):
        """Test error handling with empty template path."""
        with self.assertRaises(TemplateLoaderError) as context:
            self.loader.load_template("")
        
        self.assertIn("Template path must be a non-empty string", str(context.exception))
    
    def test_load_template_none_path(self):
        """Test error handling with None template path."""
        with self.assertRaises(TemplateLoaderError) as context:
            self.loader.load_template(None)
        
        self.assertIn("Template path must be a non-empty string", str(context.exception))
    
    def test_load_template_directory_path(self):
        """Test error handling when path points to a directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with self.assertRaises(TemplateLoaderError) as context:
                self.loader.load_template(temp_dir)
            
            self.assertIn("Template path is not a file", str(context.exception))
    
    def test_load_template_invalid_json(self):
        """Test error handling with invalid JSON content."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            temp_file.write("{ invalid json content")
            temp_file_path = temp_file.name
        
        try:
            with self.assertRaises(TemplateLoaderError) as context:
                self.loader.load_template(temp_file_path)
            
            self.assertIn("Invalid JSON in template file", str(context.exception))
        finally:
            os.unlink(temp_file_path)
    
    @patch("os.path.isfile", return_value=True)
    @patch("os.path.exists", return_value=True)
    @patch("builtins.open", side_effect=IOError("Permission denied"))
    def test_load_template_io_error(self, mock_file, mock_exists, mock_isfile):
        """Test error handling with file I/O errors."""
        with self.assertRaises(TemplateLoaderError) as context:
            self.loader.load_template("test_file.json")
        
        self.assertIn("Error reading template file", str(context.exception))
    
    def test_validate_template_structure_success(self):
        """Test successful template structure validation."""
        result = self.loader.validate_template_structure(self.valid_template)
        self.assertTrue(result)
    
    def test_validate_template_structure_not_dict(self):
        """Test validation failure when template is not a dictionary."""
        with self.assertRaises(TemplateLoaderError) as context:
            self.loader.validate_template_structure("not a dict")
        
        self.assertIn("Template must be a dictionary", str(context.exception))
    
    def test_validate_template_structure_missing_keys(self):
        """Test validation failure when required keys are missing."""
        incomplete_template = {"sheets_to_process": ["Invoice"]}
        
        with self.assertRaises(TemplateLoaderError) as context:
            self.loader.validate_template_structure(incomplete_template)
        
        self.assertIn("Missing required key", str(context.exception))
    
    def test_validate_template_structure_empty_sheets_list(self):
        """Test validation failure with empty sheets_to_process list."""
        invalid_template = self.valid_template.copy()
        invalid_template["sheets_to_process"] = []
        
        with self.assertRaises(TemplateLoaderError) as context:
            self.loader.validate_template_structure(invalid_template)
        
        self.assertIn("sheets_to_process must be a non-empty list", str(context.exception))
    
    def test_validate_template_structure_invalid_sheet_names(self):
        """Test validation failure with invalid sheet names."""
        invalid_template = self.valid_template.copy()
        invalid_template["sheets_to_process"] = ["", "  ", "Valid Sheet"]
        
        with self.assertRaises(TemplateLoaderError) as context:
            self.loader.validate_template_structure(invalid_template)
        
        self.assertIn("All sheets in sheets_to_process must be non-empty strings", str(context.exception))
    
    def test_validate_template_structure_missing_sheet_mapping(self):
        """Test validation failure when sheet is missing from data_mapping."""
        invalid_template = self.valid_template.copy()
        invalid_template["sheets_to_process"] = ["Invoice", "Missing Sheet"]
        
        with self.assertRaises(TemplateLoaderError) as context:
            self.loader.validate_template_structure(invalid_template)
        
        self.assertIn("Sheet 'Missing Sheet' missing from data_mapping", str(context.exception))
    
    def test_validate_template_structure_missing_sheet_data_map(self):
        """Test validation failure when sheet is missing from sheet_data_map."""
        invalid_template = self.valid_template.copy()
        del invalid_template["sheet_data_map"]["Invoice"]
        
        with self.assertRaises(TemplateLoaderError) as context:
            self.loader.validate_template_structure(invalid_template)
        
        self.assertIn("Sheet 'Invoice' missing from sheet_data_map", str(context.exception))
    
    def test_validate_sheet_config_invalid_start_row(self):
        """Test validation failure with invalid start_row."""
        invalid_template = self.valid_template.copy()
        invalid_template["data_mapping"]["Invoice"]["start_row"] = -1
        
        with self.assertRaises(TemplateLoaderError) as context:
            self.loader.validate_template_structure(invalid_template)
        
        self.assertIn("start_row for sheet 'Invoice' must be a non-negative integer", str(context.exception))
    
    def test_validate_sheet_config_missing_required_keys(self):
        """Test validation failure when sheet config is missing required keys."""
        invalid_template = self.valid_template.copy()
        del invalid_template["data_mapping"]["Invoice"]["mappings"]
        
        with self.assertRaises(TemplateLoaderError) as context:
            self.loader.validate_template_structure(invalid_template)
        
        self.assertIn("Sheet 'Invoice' missing required key: mappings", str(context.exception))
    
    def test_validate_header_entry_invalid_structure(self):
        """Test validation failure with invalid header entry structure."""
        invalid_template = self.valid_template.copy()
        invalid_template["data_mapping"]["Invoice"]["header_to_write"][0] = "not a dict"
        
        with self.assertRaises(TemplateLoaderError) as context:
            self.loader.validate_template_structure(invalid_template)
        
        self.assertIn("Header entry 0 in sheet 'Invoice' must be a dictionary", str(context.exception))
    
    def test_validate_header_entry_missing_required_keys(self):
        """Test validation failure when header entry is missing required keys."""
        invalid_template = self.valid_template.copy()
        del invalid_template["data_mapping"]["Invoice"]["header_to_write"][0]["text"]
        
        with self.assertRaises(TemplateLoaderError) as context:
            self.loader.validate_template_structure(invalid_template)
        
        self.assertIn("Header entry 0 in sheet 'Invoice' missing required key: text", str(context.exception))
    
    def test_validate_header_entry_missing_id_and_colspan(self):
        """Test validation failure when header entry has neither id nor colspan."""
        invalid_template = self.valid_template.copy()
        del invalid_template["data_mapping"]["Invoice"]["header_to_write"][0]["id"]
        
        with self.assertRaises(TemplateLoaderError) as context:
            self.loader.validate_template_structure(invalid_template)
        
        self.assertIn("Header entry 0 in sheet 'Invoice' must have either 'id' or 'colspan'", str(context.exception))
    
    def test_validate_header_entry_invalid_coordinates(self):
        """Test validation failure with invalid row/col coordinates."""
        invalid_template = self.valid_template.copy()
        invalid_template["data_mapping"]["Invoice"]["header_to_write"][0]["row"] = -1
        
        with self.assertRaises(TemplateLoaderError) as context:
            self.loader.validate_template_structure(invalid_template)
        
        self.assertIn("row in header entry 0 of sheet 'Invoice' must be a non-negative integer", str(context.exception))
    
    def test_validate_header_entry_empty_text(self):
        """Test validation failure with empty header text."""
        invalid_template = self.valid_template.copy()
        invalid_template["data_mapping"]["Invoice"]["header_to_write"][0]["text"] = ""
        
        with self.assertRaises(TemplateLoaderError) as context:
            self.loader.validate_template_structure(invalid_template)
        
        self.assertIn("text in header entry 0 of sheet 'Invoice' must be a non-empty string", str(context.exception))
    
    def test_validate_header_entry_invalid_span(self):
        """Test validation failure with invalid rowspan/colspan values."""
        invalid_template = self.valid_template.copy()
        invalid_template["data_mapping"]["Invoice"]["header_to_write"][0]["rowspan"] = 0
        
        with self.assertRaises(TemplateLoaderError) as context:
            self.loader.validate_template_structure(invalid_template)
        
        self.assertIn("rowspan in header entry 0 of sheet 'Invoice' must be a positive integer", str(context.exception))
    
    def test_convert_to_configuration_data_success(self):
        """Test successful conversion to ConfigurationData object."""
        result = self.loader.convert_to_configuration_data(self.valid_template)
        
        self.assertIsInstance(result, ConfigurationData)
        self.assertEqual(result.sheets_to_process, ["Invoice", "Contract", "Packing list"])
        self.assertEqual(result.sheet_data_map["Invoice"], "aggregation")
        
        # Check that sheet configs are properly converted
        invoice_config = result.data_mapping["Invoice"]
        self.assertIsInstance(invoice_config, SheetConfig)
        self.assertEqual(invoice_config.start_row, 20)
        
        # Check that header entries are properly converted
        header_entry = invoice_config.header_to_write[0]
        self.assertIsInstance(header_entry, HeaderEntry)
        self.assertEqual(header_entry.text, "Mark & Nº")
        self.assertEqual(header_entry.id, "col_static")
        self.assertEqual(header_entry.rowspan, 1)
    
    def test_convert_to_configuration_data_with_optional_fields(self):
        """Test conversion with optional header entry fields."""
        template_with_colspan = self.valid_template.copy()
        template_with_colspan["data_mapping"]["Invoice"]["header_to_write"][0]["colspan"] = 2
        del template_with_colspan["data_mapping"]["Invoice"]["header_to_write"][0]["rowspan"]
        
        result = self.loader.convert_to_configuration_data(template_with_colspan)
        header_entry = result.data_mapping["Invoice"].header_to_write[0]
        
        self.assertEqual(header_entry.colspan, 2)
        self.assertIsNone(header_entry.rowspan)
    
    def test_validate_header_entry_with_colspan_no_id(self):
        """Test validation success when header entry has colspan but no id (parent header)."""
        template_with_parent_header = self.valid_template.copy()
        # Add a parent header with colspan but no id
        parent_header = {"row": 0, "col": 2, "text": "Quantity", "colspan": 2}
        template_with_parent_header["data_mapping"]["Invoice"]["header_to_write"].append(parent_header)
        
        # This should not raise an exception
        result = self.loader.validate_template_structure(template_with_parent_header)
        self.assertTrue(result)
        
        # Test conversion as well
        config_data = self.loader.convert_to_configuration_data(template_with_parent_header)
        parent_entry = config_data.data_mapping["Invoice"].header_to_write[-1]
        self.assertEqual(parent_entry.text, "Quantity")
        self.assertEqual(parent_entry.colspan, 2)
        self.assertIsNone(parent_entry.id)


if __name__ == '__main__':
    unittest.main()