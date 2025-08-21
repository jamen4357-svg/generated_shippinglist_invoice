"""
Unit tests for the ConfigWriter component.

Tests the functionality of writing configuration data to JSON files and
validating that all template sections are preserved.
"""

import json
import os
import tempfile
import unittest
from unittest.mock import patch, mock_open

from config_generator.config_writer import ConfigWriter, ConfigWriterError
from config_generator.models import ConfigurationData, SheetConfig, HeaderEntry


class TestConfigWriter(unittest.TestCase):
    """Test cases for the ConfigWriter class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config_writer = ConfigWriter()
        
        # Sample valid configuration for testing
        self.valid_config = {
            "sheets_to_process": ["Invoice", "Contract"],
            "sheet_data_map": {
                "Invoice": "aggregation",
                "Contract": "aggregation"
            },
            "data_mapping": {
                "Invoice": {
                    "start_row": 20,
                    "header_to_write": [
                        {"row": 0, "col": 0, "text": "Mark & Nº", "id": "col_static"},
                        {"row": 0, "col": 1, "text": "P.O. Nº", "id": "col_po"}
                    ],
                    "mappings": {
                        "po": {"key_index": 0, "id": "col_po"}
                    },
                    "footer_configurations": {
                        "total_text": "TOTAL OF:",
                        "style": {"font": {"name": "Times New Roman", "size": 12}}
                    },
                    "styling": {
                        "default_font": {"name": "Times New Roman", "size": 12},
                        "header_font": {"name": "Times New Roman", "size": 12, "bold": True}
                    }
                },
                "Contract": {
                    "start_row": 15,
                    "header_to_write": [
                        {"row": 0, "col": 0, "text": "No.", "id": "col_no"}
                    ],
                    "mappings": {
                        "po": {"key_index": 0, "id": "col_po"}
                    },
                    "footer_configurations": {
                        "total_text": "TOTAL OF:"
                    },
                    "styling": {
                        "default_font": {"name": "Times New Roman", "size": 14},
                        "header_font": {"name": "Times New Roman", "size": 16, "bold": True}
                    }
                }
            }
        }
    
    def test_init(self):
        """Test ConfigWriter initialization."""
        writer = ConfigWriter()
        self.assertIsInstance(writer, ConfigWriter)
    
    def test_write_config_success(self):
        """Test successful config writing to file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            self.config_writer.write_config(self.valid_config, temp_path)
            
            # Verify file was created and contains correct data
            self.assertTrue(os.path.exists(temp_path))
            
            with open(temp_path, 'r', encoding='utf-8') as file:
                written_data = json.load(file)
            
            self.assertEqual(written_data, self.valid_config)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_write_config_creates_directory(self):
        """Test that write_config creates output directory if it doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "subdir", "config.json")
            
            self.config_writer.write_config(self.valid_config, output_path)
            
            # Verify directory was created and file exists
            self.assertTrue(os.path.exists(output_path))
            
            with open(output_path, 'r', encoding='utf-8') as file:
                written_data = json.load(file)
            
            self.assertEqual(written_data, self.valid_config)
    
    def test_write_config_invalid_config_type(self):
        """Test write_config with invalid config type."""
        with self.assertRaises(ConfigWriterError) as context:
            self.config_writer.write_config("not a dict", "output.json")
        
        self.assertIn("Config must be a dictionary", str(context.exception))
    
    def test_write_config_invalid_output_path(self):
        """Test write_config with invalid output path."""
        with self.assertRaises(ConfigWriterError) as context:
            self.config_writer.write_config(self.valid_config, "")
        
        self.assertIn("Output path must be a non-empty string", str(context.exception))
        
        with self.assertRaises(ConfigWriterError) as context:
            self.config_writer.write_config(self.valid_config, None)
        
        self.assertIn("Output path must be a non-empty string", str(context.exception))
    
    @patch('builtins.open', side_effect=IOError("Permission denied"))
    def test_write_config_io_error(self, mock_file):
        """Test write_config with IO error."""
        with self.assertRaises(ConfigWriterError) as context:
            self.config_writer.write_config(self.valid_config, "output.json")
        
        self.assertIn("Error writing config file", str(context.exception))
    
    def test_write_config_validation_failure(self):
        """Test write_config with validation failure."""
        invalid_config = {"invalid": "config"}
        
        with self.assertRaises(ConfigWriterError) as context:
            self.config_writer.write_config(invalid_config, "output.json")
        
        # The validation error should be specific about what's missing
        self.assertIn("Missing required top-level key", str(context.exception))
    
    def test_validate_completeness_success(self):
        """Test successful completeness validation."""
        result = self.config_writer.validate_completeness(self.valid_config)
        self.assertTrue(result)
    
    def test_validate_completeness_invalid_type(self):
        """Test validate_completeness with invalid config type."""
        with self.assertRaises(ConfigWriterError) as context:
            self.config_writer.validate_completeness("not a dict")
        
        self.assertIn("Config must be a dictionary", str(context.exception))
    
    def test_validate_completeness_missing_top_level_keys(self):
        """Test validate_completeness with missing top-level keys."""
        incomplete_config = {"sheets_to_process": ["Invoice"]}
        
        with self.assertRaises(ConfigWriterError) as context:
            self.config_writer.validate_completeness(incomplete_config)
        
        self.assertIn("Missing required top-level key", str(context.exception))
    
    def test_validate_completeness_invalid_sheets_to_process(self):
        """Test validate_completeness with invalid sheets_to_process."""
        # Empty list
        config = self.valid_config.copy()
        config["sheets_to_process"] = []
        
        with self.assertRaises(ConfigWriterError) as context:
            self.config_writer.validate_completeness(config)
        
        self.assertIn("sheets_to_process must be a non-empty list", str(context.exception))
        
        # Non-string sheet name
        config["sheets_to_process"] = [123]
        
        with self.assertRaises(ConfigWriterError) as context:
            self.config_writer.validate_completeness(config)
        
        self.assertIn("All sheets in sheets_to_process must be non-empty strings", str(context.exception))
    
    def test_validate_completeness_missing_sheet_mapping(self):
        """Test validate_completeness with missing sheet in data_mapping."""
        config = self.valid_config.copy()
        config["sheets_to_process"] = ["Invoice", "Contract", "Missing"]
        
        with self.assertRaises(ConfigWriterError) as context:
            self.config_writer.validate_completeness(config)
        
        self.assertIn("Sheet 'Missing' missing from data_mapping", str(context.exception))
    
    def test_validate_completeness_missing_sheet_data_map(self):
        """Test validate_completeness with missing sheet in sheet_data_map."""
        config = self.valid_config.copy()
        config["sheets_to_process"] = ["Invoice", "Contract", "Missing"]
        config["data_mapping"]["Missing"] = {
            "start_row": 10,
            "header_to_write": [{"row": 0, "col": 0, "text": "Test", "id": "col_test"}],
            "mappings": {},
            "footer_configurations": {},
            "styling": {
                "default_font": {"name": "Arial", "size": 12},
                "header_font": {"name": "Arial", "size": 12}
            }
        }
        
        with self.assertRaises(ConfigWriterError) as context:
            self.config_writer.validate_completeness(config)
        
        self.assertIn("Sheet 'Missing' missing from sheet_data_map", str(context.exception))
    
    def test_validate_sheet_completeness_missing_sections(self):
        """Test sheet completeness validation with missing sections."""
        config = self.valid_config.copy()
        del config["data_mapping"]["Invoice"]["styling"]
        
        with self.assertRaises(ConfigWriterError) as context:
            self.config_writer.validate_completeness(config)
        
        self.assertIn("Sheet 'Invoice' missing required section: styling", str(context.exception))
    
    def test_validate_sheet_completeness_invalid_start_row(self):
        """Test sheet completeness validation with invalid start_row."""
        config = self.valid_config.copy()
        config["data_mapping"]["Invoice"]["start_row"] = -1
        
        with self.assertRaises(ConfigWriterError) as context:
            self.config_writer.validate_completeness(config)
        
        self.assertIn("start_row for sheet 'Invoice' must be a non-negative integer", str(context.exception))
    
    def test_validate_sheet_completeness_empty_headers(self):
        """Test sheet completeness validation with empty header_to_write."""
        config = self.valid_config.copy()
        config["data_mapping"]["Invoice"]["header_to_write"] = []
        
        with self.assertRaises(ConfigWriterError) as context:
            self.config_writer.validate_completeness(config)
        
        self.assertIn("header_to_write for sheet 'Invoice' cannot be empty", str(context.exception))
    
    def test_validate_sheet_completeness_missing_font_info(self):
        """Test sheet completeness validation with missing font information."""
        config = self.valid_config.copy()
        del config["data_mapping"]["Invoice"]["styling"]["default_font"]
        
        with self.assertRaises(ConfigWriterError) as context:
            self.config_writer.validate_completeness(config)
        
        self.assertIn("Styling section for sheet 'Invoice' missing required key: default_font", str(context.exception))
    
    def test_validate_sheet_completeness_invalid_font_info(self):
        """Test sheet completeness validation with invalid font information."""
        config = self.valid_config.copy()
        config["data_mapping"]["Invoice"]["styling"]["default_font"] = {"name": ""}
        
        with self.assertRaises(ConfigWriterError) as context:
            self.config_writer.validate_completeness(config)
        
        self.assertIn("default_font in styling for sheet 'Invoice' must have 'name' and 'size'", str(context.exception))
    
    def test_validate_header_entry_completeness_missing_keys(self):
        """Test header entry completeness validation with missing keys."""
        config = self.valid_config.copy()
        config["data_mapping"]["Invoice"]["header_to_write"][0] = {"row": 0, "col": 0}
        
        with self.assertRaises(ConfigWriterError) as context:
            self.config_writer.validate_completeness(config)
        
        self.assertIn("Header entry 0 in sheet 'Invoice' missing required key: text", str(context.exception))
    
    def test_validate_header_entry_completeness_missing_id_and_colspan(self):
        """Test header entry completeness validation with missing id and colspan."""
        config = self.valid_config.copy()
        config["data_mapping"]["Invoice"]["header_to_write"][0] = {
            "row": 0, "col": 0, "text": "Test"
        }
        
        with self.assertRaises(ConfigWriterError) as context:
            self.config_writer.validate_completeness(config)
        
        self.assertIn("Header entry 0 in sheet 'Invoice' must have either 'id' or 'colspan'", str(context.exception))
    
    def test_validate_header_entry_completeness_with_colspan(self):
        """Test header entry completeness validation with colspan (valid parent header)."""
        config = self.valid_config.copy()
        config["data_mapping"]["Invoice"]["header_to_write"][0] = {
            "row": 0, "col": 0, "text": "Quantity", "colspan": 2
        }
        
        # Should not raise an exception
        result = self.config_writer.validate_completeness(config)
        self.assertTrue(result)
    
    def test_write_configuration_data_success(self):
        """Test successful writing of ConfigurationData object."""
        # Create ConfigurationData object
        header_entries = [
            HeaderEntry(row=0, col=0, text="Mark & Nº", id="col_static"),
            HeaderEntry(row=0, col=1, text="P.O. Nº", id="col_po")
        ]
        
        sheet_config = SheetConfig(
            start_row=20,
            header_to_write=header_entries,
            mappings={"po": {"key_index": 0, "id": "col_po"}},
            footer_configurations={"total_text": "TOTAL OF:"},
            styling={
                "default_font": {"name": "Times New Roman", "size": 12},
                "header_font": {"name": "Times New Roman", "size": 12, "bold": True}
            }
        )
        
        config_data = ConfigurationData(
            sheets_to_process=["Invoice"],
            sheet_data_map={"Invoice": "aggregation"},
            data_mapping={"Invoice": sheet_config}
        )
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            self.config_writer.write_configuration_data(config_data, temp_path)
            
            # Verify file was created and contains correct data
            self.assertTrue(os.path.exists(temp_path))
            
            with open(temp_path, 'r', encoding='utf-8') as file:
                written_data = json.load(file)
            
            # Verify structure
            self.assertEqual(written_data["sheets_to_process"], ["Invoice"])
            self.assertEqual(written_data["sheet_data_map"]["Invoice"], "aggregation")
            self.assertEqual(written_data["data_mapping"]["Invoice"]["start_row"], 20)
            self.assertEqual(len(written_data["data_mapping"]["Invoice"]["header_to_write"]), 2)
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_write_configuration_data_invalid_type(self):
        """Test write_configuration_data with invalid type."""
        with self.assertRaises(ConfigWriterError) as context:
            self.config_writer.write_configuration_data("not config data", "output.json")
        
        self.assertIn("config_data must be a ConfigurationData instance", str(context.exception))
    
    def test_configuration_data_to_dict_conversion(self):
        """Test conversion of ConfigurationData to dictionary."""
        # Create ConfigurationData object with optional fields
        header_entries = [
            HeaderEntry(row=0, col=0, text="Mark & Nº", id="col_static", rowspan=1),
            HeaderEntry(row=0, col=1, text="Quantity", colspan=2)  # Parent header without id
        ]
        
        sheet_config = SheetConfig(
            start_row=20,
            header_to_write=header_entries,
            mappings={"po": {"key_index": 0, "id": "col_po"}},
            footer_configurations={"total_text": "TOTAL OF:"},
            styling={
                "default_font": {"name": "Times New Roman", "size": 12},
                "header_font": {"name": "Times New Roman", "size": 12, "bold": True}
            }
        )
        
        config_data = ConfigurationData(
            sheets_to_process=["Invoice"],
            sheet_data_map={"Invoice": "aggregation"},
            data_mapping={"Invoice": sheet_config}
        )
        
        result_dict = self.config_writer._configuration_data_to_dict(config_data)
        
        # Verify structure
        self.assertEqual(result_dict["sheets_to_process"], ["Invoice"])
        self.assertEqual(result_dict["sheet_data_map"]["Invoice"], "aggregation")
        
        headers = result_dict["data_mapping"]["Invoice"]["header_to_write"]
        self.assertEqual(len(headers), 2)
        
        # First header with id and rowspan
        self.assertEqual(headers[0]["row"], 0)
        self.assertEqual(headers[0]["col"], 0)
        self.assertEqual(headers[0]["text"], "Mark & Nº")
        self.assertEqual(headers[0]["id"], "col_static")
        self.assertEqual(headers[0]["rowspan"], 1)
        self.assertNotIn("colspan", headers[0])
        
        # Second header with colspan but no id
        self.assertEqual(headers[1]["row"], 0)
        self.assertEqual(headers[1]["col"], 1)
        self.assertEqual(headers[1]["text"], "Quantity")
        self.assertEqual(headers[1]["colspan"], 2)
        self.assertNotIn("id", headers[1])
        self.assertNotIn("rowspan", headers[1])


if __name__ == '__main__':
    unittest.main()