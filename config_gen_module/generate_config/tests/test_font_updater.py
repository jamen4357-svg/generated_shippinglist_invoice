"""
Unit tests for the FontUpdater component.

Tests font information updates in styling sections using quantity analysis data.
"""

import pytest
import copy
from config_generator.font_updater import FontUpdater
from config_generator.models import QuantityAnalysisData, SheetData, FontInfo, HeaderPosition


class TestFontUpdater:
    """Test cases for FontUpdater component."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.font_updater = FontUpdater()
        
        # Sample font information
        self.header_font = FontInfo(name="Times New Roman", size=12.0)
        self.data_font = FontInfo(name="Times New Roman", size=10.0)
        
        # Sample sheet data
        self.sheet_data = SheetData(
            sheet_name="Invoice",
            header_font=self.header_font,
            data_font=self.data_font,
            start_row=21,
            header_positions=[
                HeaderPosition(keyword="Description", row=20, column=4)
            ]
        )
        
        # Sample quantity analysis data
        self.quantity_data = QuantityAnalysisData(
            file_path="test.xlsx",
            timestamp="2025-01-01T00:00:00",
            sheets=[self.sheet_data]
        )
        
        # Sample template with styling section
        self.template = {
            "data_mapping": {
                "Invoice": {
                    "start_row": 20,
                    "styling": {
                        "header_font": {"name": "Arial", "size": 14, "bold": True},
                        "default_font": {"name": "Arial", "size": 12},
                        "column_id_styles": {"col_amount": {"number_format": "#,##0.00"}}
                    },
                    "footer_configurations": {
                        "style": {
                            "font": {"name": "Arial", "size": 14, "bold": True}
                        }
                    }
                }
            }
        }
    
    def test_update_fonts_basic(self):
        """Test basic font update functionality."""
        result = self.font_updater.update_fonts(self.template, self.quantity_data)
        
        invoice_styling = result["data_mapping"]["Invoice"]["styling"]
        
        # Check header font was updated
        assert invoice_styling["header_font"]["name"] == "Times New Roman"
        assert invoice_styling["header_font"]["size"] == 12.0
        assert invoice_styling["header_font"]["bold"] is True  # Should preserve existing attributes
        
        # Check default font was updated
        assert invoice_styling["default_font"]["name"] == "Times New Roman"
        assert invoice_styling["default_font"]["size"] == 10.0
        
        # Check other styling attributes are preserved
        assert "column_id_styles" in invoice_styling
        assert invoice_styling["column_id_styles"]["col_amount"]["number_format"] == "#,##0.00"
    
    def test_update_fonts_footer_font(self):
        """Test that footer font is updated to match header font."""
        result = self.font_updater.update_fonts(self.template, self.quantity_data)
        
        footer_font = result["data_mapping"]["Invoice"]["footer_configurations"]["style"]["font"]
        
        # Footer font should match header font
        assert footer_font["name"] == "Times New Roman"
        assert footer_font["size"] == 12.0
        assert footer_font["bold"] is True  # Should preserve existing attributes
    
    def test_update_fonts_multiple_sheets(self):
        """Test font updates for multiple sheets."""
        # Add another sheet to quantity data
        contract_sheet = SheetData(
            sheet_name="Contract",
            header_font=FontInfo(name="Calibri", size=16.0),
            data_font=FontInfo(name="Calibri", size=14.0),
            start_row=18,
            header_positions=[]
        )
        
        multi_sheet_data = QuantityAnalysisData(
            file_path="test.xlsx",
            timestamp="2025-01-01T00:00:00",
            sheets=[self.sheet_data, contract_sheet]
        )
        
        # Add Contract to template
        template_with_contract = copy.deepcopy(self.template)
        template_with_contract["data_mapping"]["Contract"] = {
            "start_row": 15,
            "styling": {
                "header_font": {"name": "Arial", "size": 16, "bold": True},
                "default_font": {"name": "Arial", "size": 14}
            }
        }
        
        result = self.font_updater.update_fonts(template_with_contract, multi_sheet_data)
        
        # Check Invoice fonts
        invoice_styling = result["data_mapping"]["Invoice"]["styling"]
        assert invoice_styling["header_font"]["name"] == "Times New Roman"
        assert invoice_styling["default_font"]["size"] == 10.0
        
        # Check Contract fonts
        contract_styling = result["data_mapping"]["Contract"]["styling"]
        assert contract_styling["header_font"]["name"] == "Calibri"
        assert contract_styling["header_font"]["size"] == 16.0
        assert contract_styling["default_font"]["name"] == "Calibri"
        assert contract_styling["default_font"]["size"] == 14.0
    
    def test_update_fonts_missing_sheet_data(self):
        """Test behavior when sheet data is missing from quantity analysis."""
        # Template has a sheet not in quantity data
        template_with_extra_sheet = copy.deepcopy(self.template)
        template_with_extra_sheet["data_mapping"]["Packing list"] = {
            "styling": {
                "header_font": {"name": "Arial", "size": 12},
                "default_font": {"name": "Arial", "size": 10}
            }
        }
        
        result = self.font_updater.update_fonts(template_with_extra_sheet, self.quantity_data)
        
        # Invoice should be updated
        invoice_styling = result["data_mapping"]["Invoice"]["styling"]
        assert invoice_styling["header_font"]["name"] == "Times New Roman"
        
        # Packing list should remain unchanged (no matching sheet data)
        packing_styling = result["data_mapping"]["Packing list"]["styling"]
        assert packing_styling["header_font"]["name"] == "Arial"
        assert packing_styling["default_font"]["name"] == "Arial"
    
    def test_update_fonts_missing_styling_section(self):
        """Test behavior when styling section is missing."""
        template_no_styling = {
            "data_mapping": {
                "Invoice": {
                    "start_row": 20,
                    "mappings": {"po": {"key_index": 0}}
                }
            }
        }
        
        # Should not raise an error
        result = self.font_updater.update_fonts(template_no_styling, self.quantity_data)
        
        # Template should remain unchanged
        assert result["data_mapping"]["Invoice"]["start_row"] == 20
        assert "styling" not in result["data_mapping"]["Invoice"]
    
    def test_update_fonts_missing_font_keys(self):
        """Test behavior when font keys are missing from styling."""
        template_partial_fonts = {
            "data_mapping": {
                "Invoice": {
                    "styling": {
                        "header_font": {"name": "Arial", "size": 14},
                        # Missing default_font
                        "column_id_styles": {}
                    }
                }
            }
        }
        
        result = self.font_updater.update_fonts(template_partial_fonts, self.quantity_data)
        
        # Header font should be updated
        styling = result["data_mapping"]["Invoice"]["styling"]
        assert styling["header_font"]["name"] == "Times New Roman"
        
        # Should not create default_font if it wasn't there
        assert "default_font" not in styling
    
    def test_update_fonts_preserves_original_template(self):
        """Test that original template is not modified."""
        original_template = copy.deepcopy(self.template)
        
        self.font_updater.update_fonts(self.template, self.quantity_data)
        
        # Original template should be unchanged
        assert self.template == original_template
    
    def test_update_fonts_invalid_template(self):
        """Test error handling for invalid template."""
        from config_generator.font_updater import FontUpdaterError
        with pytest.raises(FontUpdaterError, match="Template must be a dictionary"):
            self.font_updater.update_fonts("invalid", self.quantity_data)
    
    def test_update_fonts_invalid_quantity_data(self):
        """Test error handling for invalid quantity data."""
        from config_generator.font_updater import FontUpdaterError
        with pytest.raises(FontUpdaterError, match="Quantity data must be a QuantityAnalysisData instance"):
            self.font_updater.update_fonts(self.template, "invalid")
    
    def test_find_sheet_data_existing_sheet(self):
        """Test finding existing sheet data."""
        result = self.font_updater._find_sheet_data(self.quantity_data, "Invoice")
        assert result is not None
        assert result.sheet_name == "Invoice"
        assert result.header_font.name == "Times New Roman"
    
    def test_find_sheet_data_nonexistent_sheet(self):
        """Test finding non-existent sheet data."""
        result = self.font_updater._find_sheet_data(self.quantity_data, "NonExistent")
        assert result is None
    
    def test_update_sheet_fonts_complete(self):
        """Test updating sheet fonts with complete font information."""
        styling = {
            "header_font": {"name": "Arial", "size": 14, "bold": True},
            "default_font": {"name": "Arial", "size": 12},
            "other_style": "preserved"
        }
        
        header_font = FontInfo(name="Times New Roman", size=16.0)
        data_font = FontInfo(name="Calibri", size=11.0)
        
        self.font_updater._update_sheet_fonts(styling, header_font, data_font)
        
        # Check updates
        assert styling["header_font"]["name"] == "Times New Roman"
        assert styling["header_font"]["size"] == 16.0
        assert styling["header_font"]["bold"] is True  # Preserved
        
        assert styling["default_font"]["name"] == "Calibri"
        assert styling["default_font"]["size"] == 11.0
        
        # Check preservation
        assert styling["other_style"] == "preserved"
    
    def test_update_footer_font(self):
        """Test updating footer font information."""
        footer_font = {"name": "Arial", "size": 12, "bold": True}
        header_font = FontInfo(name="Times New Roman", size=14.0)
        
        self.font_updater._update_footer_font(footer_font, header_font)
        
        assert footer_font["name"] == "Times New Roman"
        assert footer_font["size"] == 14.0
        assert footer_font["bold"] is True  # Should preserve existing attributes