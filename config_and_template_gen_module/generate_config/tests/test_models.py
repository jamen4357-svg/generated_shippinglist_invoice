"""
Unit tests for data model validation.

Tests all data classes to ensure proper validation and error handling.
"""

import pytest
from config_generator.models import (
    FontInfo, HeaderPosition, SheetData, QuantityAnalysisData,
    HeaderEntry, SheetConfig, ConfigurationData
)


class TestFontInfo:
    """Test FontInfo data class validation."""
    
    def test_valid_font_info(self):
        """Test creating valid FontInfo instance."""
        font = FontInfo(name="Arial", size=12.0)
        assert font.name == "Arial"
        assert font.size == 12.0
    
    def test_empty_font_name_raises_error(self):
        """Test that empty font name raises ValueError."""
        with pytest.raises(ValueError, match="Font name must be a non-empty string"):
            FontInfo(name="", size=12.0)
    
    def test_whitespace_font_name_raises_error(self):
        """Test that whitespace-only font name raises ValueError."""
        with pytest.raises(ValueError, match="Font name must be a non-empty string"):
            FontInfo(name="   ", size=12.0)
    
    def test_non_string_font_name_raises_error(self):
        """Test that non-string font name raises ValueError."""
        with pytest.raises(ValueError, match="Font name must be a non-empty string"):
            FontInfo(name=123, size=12.0)
    
    def test_zero_font_size_raises_error(self):
        """Test that zero font size raises ValueError."""
        with pytest.raises(ValueError, match="Font size must be a positive number"):
            FontInfo(name="Arial", size=0)
    
    def test_negative_font_size_raises_error(self):
        """Test that negative font size raises ValueError."""
        with pytest.raises(ValueError, match="Font size must be a positive number"):
            FontInfo(name="Arial", size=-5.0)
    
    def test_non_numeric_font_size_raises_error(self):
        """Test that non-numeric font size raises ValueError."""
        with pytest.raises(ValueError, match="Font size must be a positive number"):
            FontInfo(name="Arial", size="12")


class TestHeaderPosition:
    """Test HeaderPosition data class validation."""
    
    def test_valid_header_position(self):
        """Test creating valid HeaderPosition instance."""
        header = HeaderPosition(keyword="Item No", row=1, column=2)
        assert header.keyword == "Item No"
        assert header.row == 1
        assert header.column == 2
    
    def test_empty_keyword_raises_error(self):
        """Test that empty keyword raises ValueError."""
        with pytest.raises(ValueError, match="Header keyword must be a non-empty string"):
            HeaderPosition(keyword="", row=1, column=2)
    
    def test_whitespace_keyword_raises_error(self):
        """Test that whitespace-only keyword raises ValueError."""
        with pytest.raises(ValueError, match="Header keyword must be a non-empty string"):
            HeaderPosition(keyword="   ", row=1, column=2)
    
    def test_negative_row_raises_error(self):
        """Test that negative row raises ValueError."""
        with pytest.raises(ValueError, match="Row must be a non-negative integer"):
            HeaderPosition(keyword="Item", row=-1, column=2)
    
    def test_negative_column_raises_error(self):
        """Test that negative column raises ValueError."""
        with pytest.raises(ValueError, match="Column must be a non-negative integer"):
            HeaderPosition(keyword="Item", row=1, column=-1)
    
    def test_non_integer_row_raises_error(self):
        """Test that non-integer row raises ValueError."""
        with pytest.raises(ValueError, match="Row must be a non-negative integer"):
            HeaderPosition(keyword="Item", row=1.5, column=2)


class TestSheetData:
    """Test SheetData data class validation."""
    
    def test_valid_sheet_data(self):
        """Test creating valid SheetData instance."""
        font_info = FontInfo(name="Arial", size=12.0)
        header_pos = HeaderPosition(keyword="Item", row=1, column=2)
        
        sheet = SheetData(
            sheet_name="Invoice",
            header_font=font_info,
            data_font=font_info,
            start_row=3,
            header_positions=[header_pos]
        )
        
        assert sheet.sheet_name == "Invoice"
        assert sheet.start_row == 3
        assert len(sheet.header_positions) == 1
    
    def test_empty_sheet_name_raises_error(self):
        """Test that empty sheet name raises ValueError."""
        font_info = FontInfo(name="Arial", size=12.0)
        
        with pytest.raises(ValueError, match="Sheet name must be a non-empty string"):
            SheetData(
                sheet_name="",
                header_font=font_info,
                data_font=font_info,
                start_row=3,
                header_positions=[]
            )
    
    def test_negative_start_row_raises_error(self):
        """Test that negative start row raises ValueError."""
        font_info = FontInfo(name="Arial", size=12.0)
        
        with pytest.raises(ValueError, match="Start row must be a non-negative integer"):
            SheetData(
                sheet_name="Invoice",
                header_font=font_info,
                data_font=font_info,
                start_row=-1,
                header_positions=[]
            )
    
    def test_non_list_header_positions_raises_error(self):
        """Test that non-list header positions raises ValueError."""
        font_info = FontInfo(name="Arial", size=12.0)
        
        with pytest.raises(ValueError, match="Header positions must be a list"):
            SheetData(
                sheet_name="Invoice",
                header_font=font_info,
                data_font=font_info,
                start_row=3,
                header_positions="not a list"
            )


class TestQuantityAnalysisData:
    """Test QuantityAnalysisData data class validation."""
    
    def test_valid_quantity_analysis_data(self):
        """Test creating valid QuantityAnalysisData instance."""
        font_info = FontInfo(name="Arial", size=12.0)
        header_pos = HeaderPosition(keyword="Item", row=1, column=2)
        sheet_data = SheetData(
            sheet_name="Invoice",
            header_font=font_info,
            data_font=font_info,
            start_row=3,
            header_positions=[header_pos]
        )
        
        analysis = QuantityAnalysisData(
            file_path="/path/to/file.json",
            timestamp="2024-01-01T00:00:00Z",
            sheets=[sheet_data]
        )
        
        assert analysis.file_path == "/path/to/file.json"
        assert analysis.timestamp == "2024-01-01T00:00:00Z"
        assert len(analysis.sheets) == 1
    
    def test_empty_file_path_raises_error(self):
        """Test that empty file path raises ValueError."""
        with pytest.raises(ValueError, match="File path must be a non-empty string"):
            QuantityAnalysisData(
                file_path="",
                timestamp="2024-01-01T00:00:00Z",
                sheets=[]
            )
    
    def test_empty_sheets_raises_error(self):
        """Test that empty sheets list raises ValueError."""
        with pytest.raises(ValueError, match="Sheets must be a non-empty list"):
            QuantityAnalysisData(
                file_path="/path/to/file.json",
                timestamp="2024-01-01T00:00:00Z",
                sheets=[]
            )


class TestHeaderEntry:
    """Test HeaderEntry data class validation."""
    
    def test_valid_header_entry(self):
        """Test creating valid HeaderEntry instance."""
        entry = HeaderEntry(row=0, col=1, text="Item No", id="col_item")
        assert entry.row == 0
        assert entry.col == 1
        assert entry.text == "Item No"
        assert entry.id == "col_item"
        assert entry.rowspan is None
        assert entry.colspan is None
    
    def test_header_entry_with_spans(self):
        """Test creating HeaderEntry with rowspan and colspan."""
        entry = HeaderEntry(
            row=0, col=1, text="Quantity", id="col_qty", 
            rowspan=2, colspan=2
        )
        assert entry.rowspan == 2
        assert entry.colspan == 2
    
    def test_negative_row_raises_error(self):
        """Test that negative row raises ValueError."""
        with pytest.raises(ValueError, match="Row must be a non-negative integer"):
            HeaderEntry(row=-1, col=1, text="Item", id="col_item")
    
    def test_empty_text_raises_error(self):
        """Test that empty text raises ValueError."""
        with pytest.raises(ValueError, match="Text must be a non-empty string"):
            HeaderEntry(row=0, col=1, text="", id="col_item")
    
    def test_empty_id_raises_error(self):
        """Test that empty id raises ValueError when provided."""
        with pytest.raises(ValueError, match="ID must be a non-empty string when provided"):
            HeaderEntry(row=0, col=1, text="Item", id="")
    
    def test_header_entry_with_optional_id(self):
        """Test creating HeaderEntry with no id (parent header with colspan)."""
        entry = HeaderEntry(row=0, col=1, text="Quantity", colspan=2)
        assert entry.row == 0
        assert entry.col == 1
        assert entry.text == "Quantity"
        assert entry.id is None
        assert entry.colspan == 2
    
    def test_header_entry_without_id_or_colspan_raises_error(self):
        """Test that HeaderEntry without id or colspan raises ValueError."""
        with pytest.raises(ValueError, match="Header entry must have either 'id' or 'colspan'"):
            HeaderEntry(row=0, col=1, text="Item")


class TestSheetConfig:
    """Test SheetConfig data class validation."""
    
    def test_valid_sheet_config(self):
        """Test creating valid SheetConfig instance."""
        header_entry = HeaderEntry(row=0, col=1, text="Item", id="col_item")
        
        config = SheetConfig(
            start_row=3,
            header_to_write=[header_entry],
            mappings={"col_item": "A"},
            footer_configurations={},
            styling={}
        )
        
        assert config.start_row == 3
        assert len(config.header_to_write) == 1
        assert config.mappings == {"col_item": "A"}
    
    def test_negative_start_row_raises_error(self):
        """Test that negative start row raises ValueError."""
        with pytest.raises(ValueError, match="Start row must be a non-negative integer"):
            SheetConfig(
                start_row=-1,
                header_to_write=[],
                mappings={},
                footer_configurations={},
                styling={}
            )
    
    def test_non_list_header_to_write_raises_error(self):
        """Test that non-list header_to_write raises ValueError."""
        with pytest.raises(ValueError, match="Header to write must be a list"):
            SheetConfig(
                start_row=3,
                header_to_write="not a list",
                mappings={},
                footer_configurations={},
                styling={}
            )


class TestConfigurationData:
    """Test ConfigurationData data class validation."""
    
    def test_valid_configuration_data(self):
        """Test creating valid ConfigurationData instance."""
        header_entry = HeaderEntry(row=0, col=1, text="Item", id="col_item")
        sheet_config = SheetConfig(
            start_row=3,
            header_to_write=[header_entry],
            mappings={"col_item": "A"},
            footer_configurations={},
            styling={}
        )
        
        config = ConfigurationData(
            sheets_to_process=["Invoice"],
            sheet_data_map={"Invoice": "aggregation"},
            data_mapping={"Invoice": sheet_config}
        )
        
        assert config.sheets_to_process == ["Invoice"]
        assert config.sheet_data_map == {"Invoice": "aggregation"}
        assert "Invoice" in config.data_mapping
    
    def test_missing_data_mapping_raises_error(self):
        """Test that missing data mapping for sheet raises ValueError."""
        with pytest.raises(ValueError, match="Sheet 'Invoice' in sheets_to_process missing from data_mapping"):
            ConfigurationData(
                sheets_to_process=["Invoice"],
                sheet_data_map={"Invoice": "aggregation"},
                data_mapping={}
            )
    
    def test_non_list_sheets_to_process_raises_error(self):
        """Test that non-list sheets_to_process raises ValueError."""
        with pytest.raises(ValueError, match="Sheets to process must be a list"):
            ConfigurationData(
                sheets_to_process="not a list",
                sheet_data_map={},
                data_mapping={}
            )