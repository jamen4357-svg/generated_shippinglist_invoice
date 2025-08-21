"""
Unit tests for comprehensive error handling and validation.

This module tests error scenarios across all components to ensure proper
error handling, fallback strategies, and validation.
"""

import unittest
import tempfile
import os
import json
from unittest.mock import patch, mock_open, MagicMock

from config_generator.config_generator import ConfigGenerator, ConfigGeneratorError
from config_generator.template_loader import TemplateLoader, TemplateLoaderError
from config_generator.quantity_data_loader import QuantityDataLoader, QuantityDataLoaderError
from config_generator.header_text_updater import HeaderTextUpdater, HeaderTextUpdaterError
from config_generator.font_updater import FontUpdater, FontUpdaterError
from config_generator.position_updater import PositionUpdater, PositionUpdaterError
from config_generator.config_writer import ConfigWriter, ConfigWriterError
from config_generator.models import QuantityAnalysisData, SheetData, HeaderPosition, FontInfo


class TestErrorHandling(unittest.TestCase):
    """Test comprehensive error handling across all components."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config_generator = ConfigGenerator()
        self.template_loader = TemplateLoader()
        self.quantity_data_loader = QuantityDataLoader()
        self.header_text_updater = HeaderTextUpdater()
        self.font_updater = FontUpdater()
        self.position_updater = PositionUpdater()
        self.config_writer = ConfigWriter()
        
        # Sample valid data for testing
        self.valid_template = {
            "sheets_to_process": ["Invoice"],
            "sheet_data_map": {"Invoice": "aggregation"},
            "data_mapping": {
                "Invoice": {
                    "start_row": 21,
                    "header_to_write": [
                        {"row": 0, "col": 0, "text": "Mark & Nº", "id": "col_static"}
                    ],
                    "mappings": {"col_static": {"column": "A", "data_type": "string"}},
                    "footer_configurations": {},
                    "styling": {
                        "header_font": {"name": "Arial", "size": 12},
                        "default_font": {"name": "Arial", "size": 10}
                    }
                }
            }
        }
        
        self.valid_quantity_data = QuantityAnalysisData(
            file_path="test.xlsx",
            timestamp="2024-01-01",
            sheets=[
                SheetData(
                    sheet_name="Invoice",
                    header_font=FontInfo(name="Calibri", size=11),
                    data_font=FontInfo(name="Calibri", size=9),
                    start_row=21,
                    header_positions=[
                        HeaderPosition(keyword="Mark & Nº", row=0, column=1)
                    ]
                )
            ]
        )
    
    def test_config_generator_invalid_template_path(self):
        """Test ConfigGenerator with invalid template path."""
        with self.assertRaises(ConfigGeneratorError) as context:
            self.config_generator.generate_config("", "valid_quantity.json", "output.json")
        
        self.assertIn("Template loading failed", str(context.exception))
    
    def test_config_generator_invalid_quantity_path(self):
        """Test ConfigGenerator with invalid quantity data path."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            json.dump(self.valid_template, temp_file)
            temp_file.flush()
            temp_file_name = temp_file.name
            
        try:
            with self.assertRaises(ConfigGeneratorError) as context:
                self.config_generator.generate_config(temp_file_name, "", "output.json")
            
            self.assertIn("Quantity data loading failed", str(context.exception))
        finally:
            try:
                os.unlink(temp_file_name)
            except (OSError, PermissionError):
                pass  # Ignore cleanup errors on Windows
    
    def test_config_generator_invalid_output_path(self):
        """Test ConfigGenerator with invalid output path."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            json.dump(self.valid_template, temp_file)
            temp_file.flush()
            temp_file_name = temp_file.name
            
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as quantity_file:
            quantity_data = {
                "file_path": "test.xlsx",
                "timestamp": "2024-01-01",
                "sheets": [
                    {
                        "sheet_name": "Invoice",
                        "header_font": {"name": "Calibri", "size": 11},
                        "data_font": {"name": "Calibri", "size": 9},
                        "start_row": 21,
                        "header_positions": [
                            {"keyword": "Mark & Nº", "row": 0, "column": 1}
                        ]
                    }
                ]
            }
            json.dump(quantity_data, quantity_file)
            quantity_file.flush()
            quantity_file_name = quantity_file.name
            
        try:
            with self.assertRaises(ConfigGeneratorError) as context:
                self.config_generator.generate_config(temp_file_name, quantity_file_name, "")
            
            self.assertIn("Configuration writing failed", str(context.exception))
        finally:
            try:
                os.unlink(temp_file_name)
                os.unlink(quantity_file_name)
            except (OSError, PermissionError):
                pass  # Ignore cleanup errors on Windows
    
    def test_header_text_updater_invalid_template_structure(self):
        """Test HeaderTextUpdater with invalid template structure."""
        invalid_template = {"invalid": "structure"}
        
        with self.assertRaises(HeaderTextUpdaterError) as context:
            self.header_text_updater.update_header_texts(invalid_template, self.valid_quantity_data)
        
        self.assertIn("Template missing 'data_mapping' section", str(context.exception))
    
    def test_header_text_updater_invalid_quantity_data(self):
        """Test HeaderTextUpdater with invalid quantity data."""
        with self.assertRaises(HeaderTextUpdaterError) as context:
            self.header_text_updater.update_header_texts(self.valid_template, "invalid")
        
        self.assertIn("Quantity data must be QuantityAnalysisData instance", str(context.exception))
    
    def test_header_text_updater_missing_header_to_write(self):
        """Test HeaderTextUpdater with missing header_to_write section."""
        invalid_template = {
            "data_mapping": {
                "Invoice": {
                    "start_row": 21,
                    # Missing header_to_write
                    "mappings": {},
                    "footer_configurations": {},
                    "styling": {}
                }
            }
        }
        
        with self.assertRaises(HeaderTextUpdaterError) as context:
            self.header_text_updater.update_header_texts(invalid_template, self.valid_quantity_data)
        
        self.assertIn("missing 'header_to_write' section", str(context.exception))
    
    def test_font_updater_invalid_template_structure(self):
        """Test FontUpdater with invalid template structure."""
        invalid_template = {"invalid": "structure"}
        
        with self.assertRaises(FontUpdaterError) as context:
            self.font_updater.update_fonts(invalid_template, self.valid_quantity_data)
        
        self.assertIn("Template missing 'data_mapping' section", str(context.exception))
    
    def test_font_updater_invalid_quantity_data(self):
        """Test FontUpdater with invalid quantity data."""
        with self.assertRaises(FontUpdaterError) as context:
            self.font_updater.update_fonts(self.valid_template, "invalid")
        
        self.assertIn("Quantity data must be a QuantityAnalysisData instance", str(context.exception))
    
    def test_font_updater_missing_font_data(self):
        """Test FontUpdater with missing font data."""
        # Create quantity data with missing font information
        invalid_quantity_data = QuantityAnalysisData(
            file_path="test.xlsx",
            timestamp="2024-01-01",
            sheets=[
                SheetData(
                    sheet_name="Invoice",
                    header_font=None,  # Missing font data
                    data_font=None,    # Missing font data
                    start_row=21,
                    header_positions=[]
                )
            ]
        )
        
        with self.assertRaises(FontUpdaterError) as context:
            self.font_updater.update_fonts(self.valid_template, invalid_quantity_data)
        
        self.assertIn("missing header_font data", str(context.exception))
    
    def test_position_updater_invalid_template_structure(self):
        """Test PositionUpdater with invalid template structure."""
        invalid_template = {"invalid": "structure"}
        
        with self.assertRaises(PositionUpdaterError) as context:
            self.position_updater.update_start_rows(invalid_template, self.valid_quantity_data)
        
        self.assertIn("Template missing 'data_mapping' section", str(context.exception))
    
    def test_position_updater_invalid_quantity_data(self):
        """Test PositionUpdater with invalid quantity data."""
        with self.assertRaises(PositionUpdaterError) as context:
            self.position_updater.update_start_rows(self.valid_template, "invalid")
        
        self.assertIn("Quantity data must be QuantityAnalysisData instance", str(context.exception))
    
    def test_position_updater_invalid_start_row_data(self):
        """Test PositionUpdater with invalid start row data."""
        # The model validation will catch this before it gets to the updater
        with self.assertRaises(ValueError) as context:
            invalid_quantity_data = QuantityAnalysisData(
                file_path="test.xlsx",
                timestamp="2024-01-01",
                sheets=[
                    SheetData(
                        sheet_name="Invoice",
                        header_font=FontInfo(name="Arial", size=12),
                        data_font=FontInfo(name="Arial", size=10),
                        start_row=-1,  # Invalid start row
                        header_positions=[]
                    )
                ]
            )
        
        self.assertIn("Start row must be a non-negative integer", str(context.exception))
    
    def test_config_writer_invalid_config_type(self):
        """Test ConfigWriter with invalid config type."""
        with self.assertRaises(ConfigWriterError) as context:
            self.config_writer.write_config("invalid", "output.json")
        
        self.assertIn("Config must be a dictionary", str(context.exception))
    
    def test_config_writer_invalid_output_path(self):
        """Test ConfigWriter with invalid output path."""
        with self.assertRaises(ConfigWriterError) as context:
            self.config_writer.write_config(self.valid_template, "")
        
        self.assertIn("Output path must be a non-empty string", str(context.exception))
    
    def test_config_writer_incomplete_config(self):
        """Test ConfigWriter with incomplete configuration."""
        incomplete_config = {"sheets_to_process": ["Invoice"]}  # Missing required sections
        
        with self.assertRaises(ConfigWriterError) as context:
            self.config_writer.write_config(incomplete_config, "output.json")
        
        self.assertIn("Missing required top-level key", str(context.exception))
    
    @patch('os.access')
    def test_config_writer_permission_denied(self, mock_access):
        """Test ConfigWriter with permission denied."""
        mock_access.return_value = False
        
        with self.assertRaises(ConfigWriterError) as context:
            self.config_writer.write_config(self.valid_template, "/readonly/output.json")
        
        self.assertIn("No write permission", str(context.exception))
    
    @patch('builtins.open', side_effect=IOError("Disk full"))
    def test_config_writer_io_error(self, mock_open):
        """Test ConfigWriter with I/O error."""
        with self.assertRaises(ConfigWriterError) as context:
            self.config_writer.write_config(self.valid_template, "output.json")
        
        self.assertIn("Error writing config file", str(context.exception))
    
    def test_template_preservation_validation(self):
        """Test template preservation validation."""
        # Create updated config missing critical sections
        incomplete_updated_config = {
            "sheets_to_process": ["Invoice"],
            "sheet_data_map": {"Invoice": "aggregation"}
            # Missing data_mapping
        }
        
        with self.assertRaises(ConfigWriterError) as context:
            self.config_writer.validate_template_preservation(self.valid_template, incomplete_updated_config)
        
        self.assertIn("Critical section 'data_mapping' was removed", str(context.exception))
    
    def test_fallback_strategies_unrecognized_headers(self):
        """Test fallback strategies for unrecognized headers."""
        # Create quantity data with unrecognized headers
        unrecognized_quantity_data = QuantityAnalysisData(
            file_path="test.xlsx",
            timestamp="2024-01-01",
            sheets=[
                SheetData(
                    sheet_name="Invoice",
                    header_font=FontInfo(name="Calibri", size=11),
                    data_font=FontInfo(name="Calibri", size=9),
                    start_row=21,
                    header_positions=[
                        HeaderPosition(keyword="Unknown Header", row=0, column=1)
                    ]
                )
            ]
        )
        
        # Should not raise error, but apply fallback strategies
        result = self.header_text_updater.update_header_texts(self.valid_template, unrecognized_quantity_data)
        
        # Verify template structure is preserved
        self.assertIn("data_mapping", result)
        self.assertIn("Invoice", result["data_mapping"])
    
    def test_fallback_strategies_missing_font_data(self):
        """Test fallback strategies for missing font data."""
        # Create quantity data with missing sheet
        missing_sheet_quantity_data = QuantityAnalysisData(
            file_path="test.xlsx",
            timestamp="2024-01-01",
            sheets=[
                SheetData(
                    sheet_name="Contract",  # Different sheet name
                    header_font=FontInfo(name="Calibri", size=11),
                    data_font=FontInfo(name="Calibri", size=9),
                    start_row=18,
                    header_positions=[]
                )
            ]
        )
        
        # Should not raise error, but apply fallback strategies
        result = self.font_updater.update_fonts(self.valid_template, missing_sheet_quantity_data)
        
        # Verify template structure is preserved
        self.assertIn("data_mapping", result)
        self.assertIn("Invoice", result["data_mapping"])
    
    def test_input_validation_comprehensive(self):
        """Test comprehensive input validation."""
        # Test various invalid input scenarios
        test_cases = [
            (None, self.valid_quantity_data, "output.json"),
            (self.valid_template, None, "output.json"),
            (self.valid_template, self.valid_quantity_data, None),
            (123, self.valid_quantity_data, "output.json"),
            (self.valid_template, "invalid", "output.json"),
            (self.valid_template, self.valid_quantity_data, 123),
        ]
        
        for template, quantity_data, output_path in test_cases:
            with self.assertRaises(ConfigGeneratorError):
                self.config_generator.validate_inputs(template, quantity_data, output_path)


class TestFileOperationErrorHandling(unittest.TestCase):
    """Test file operation error handling scenarios."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config_writer = ConfigWriter()
        self.template_loader = TemplateLoader()
        self.quantity_data_loader = QuantityDataLoader()
        
        self.valid_config = {
            "sheets_to_process": ["Invoice"],
            "sheet_data_map": {"Invoice": "aggregation"},
            "data_mapping": {
                "Invoice": {
                    "start_row": 21,
                    "header_to_write": [{"row": 0, "col": 0, "text": "Test", "id": "col_test"}],
                    "mappings": {},
                    "footer_configurations": {},
                    "styling": {
                        "header_font": {"name": "Arial", "size": 12},
                        "default_font": {"name": "Arial", "size": 10}
                    }
                }
            }
        }
    
    @patch('os.makedirs', side_effect=OSError("Permission denied"))
    def test_directory_creation_failure(self, mock_makedirs):
        """Test handling of directory creation failure."""
        with self.assertRaises(ConfigWriterError) as context:
            self.config_writer.write_config(self.valid_config, "/readonly/subdir/output.json")
        
        self.assertIn("Failed to create output directory", str(context.exception))
    
    @patch('builtins.open')
    @patch('os.path.exists', return_value=False)
    def test_atomic_write_failure(self, mock_exists, mock_open):
        """Test handling of atomic write failure."""
        mock_open.side_effect = IOError("Disk full")
        
        with self.assertRaises(ConfigWriterError) as context:
            self.config_writer.write_config(self.valid_config, "output.json")
        
        self.assertIn("Error writing config file", str(context.exception))
    
    def test_template_loader_file_locked(self):
        """Test handling of locked template file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            json.dump(self.valid_config, temp_file)
            temp_file.flush()
            temp_file_name = temp_file.name
            
        # Simulate file lock by keeping file open
        with open(temp_file_name, 'r'):
            try:
                # This should still work on most systems, but tests the error path
                result = self.template_loader.load_template(temp_file_name)
                self.assertIsInstance(result, dict)
            except TemplateLoaderError:
                # Expected on systems where file locking prevents reading
                pass
        
        try:
            os.unlink(temp_file_name)
        except (OSError, PermissionError):
            pass  # Ignore cleanup errors on Windows
    
    def test_quantity_data_loader_corrupted_file(self):
        """Test handling of corrupted quantity data file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            temp_file.write('{"invalid": json content')  # Corrupted JSON
            temp_file.flush()
            temp_file_name = temp_file.name
            
        try:
            with self.assertRaises(QuantityDataLoaderError) as context:
                self.quantity_data_loader.load_quantity_data(temp_file_name)
            
            self.assertIn("Invalid JSON format", str(context.exception))
        finally:
            try:
                os.unlink(temp_file_name)
            except (OSError, PermissionError):
                pass  # Ignore cleanup errors on Windows


if __name__ == '__main__':
    unittest.main()