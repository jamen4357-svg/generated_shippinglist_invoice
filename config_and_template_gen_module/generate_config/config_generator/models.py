"""
Data models for the Config Generator.

This module defines the data classes used throughout the config generator system
for representing quantity analysis data and configuration structures.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional


@dataclass
class FontInfo:
    """Font information extracted from quantity analysis data."""
    name: str
    size: float
    
    def __post_init__(self):
        """Validate font data after initialization."""
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("Font name must be a non-empty string")
        if not isinstance(self.size, (int, float)) or self.size <= 0:
            raise ValueError("Font size must be a positive number")


@dataclass
class HeaderPosition:
    """Position and metadata for a header in the spreadsheet."""
    keyword: str
    row: int
    column: int
    
    def __post_init__(self):
        """Validate header position data after initialization."""
        if not isinstance(self.keyword, str) or not self.keyword.strip():
            raise ValueError("Header keyword must be a non-empty string")
        if not isinstance(self.row, int) or self.row < 0:
            raise ValueError("Row must be a non-negative integer")
        if not isinstance(self.column, int) or self.column < 0:
            raise ValueError("Column must be a non-negative integer")


@dataclass
class FooterInfo:
    """Footer information extracted from quantity analysis data."""
    row: int
    font: FontInfo
    has_formulas: bool = False
    formula_columns: List[int] = None
    
    def __post_init__(self):
        """Validate footer data after initialization."""
        if not isinstance(self.row, int) or self.row < 0:
            raise ValueError("Footer row must be a non-negative integer")
        if self.formula_columns is None:
            self.formula_columns = []


@dataclass
class SheetData:
    """Data for a single sheet from quantity analysis."""
    sheet_name: str
    header_font: FontInfo
    data_font: FontInfo
    start_row: int
    header_positions: List[HeaderPosition]
    footer_info: Optional[FooterInfo] = None
    
    def __post_init__(self):
        """Validate sheet data after initialization."""
        if not isinstance(self.sheet_name, str) or not self.sheet_name.strip():
            raise ValueError("Sheet name must be a non-empty string")
        if not isinstance(self.start_row, int) or self.start_row < 0:
            raise ValueError("Start row must be a non-negative integer")
        if not isinstance(self.header_positions, list):
            raise ValueError("Header positions must be a list")


@dataclass
class QuantityAnalysisData:
    """Complete quantity analysis data structure."""
    file_path: str
    timestamp: str
    sheets: List[SheetData]
    
    def __post_init__(self):
        """Validate quantity analysis data after initialization."""
        if not isinstance(self.file_path, str) or not self.file_path.strip():
            raise ValueError("File path must be a non-empty string")
        if not isinstance(self.timestamp, str) or not self.timestamp.strip():
            raise ValueError("Timestamp must be a non-empty string")
        if not isinstance(self.sheets, list) or len(self.sheets) == 0:
            raise ValueError("Sheets must be a non-empty list")


@dataclass
class HeaderEntry:
    """Entry in the header_to_write configuration section."""
    row: int
    col: int
    text: str
    id: Optional[str] = None
    rowspan: Optional[int] = None
    colspan: Optional[int] = None
    
    def __post_init__(self):
        """Validate header entry data after initialization."""
        if not isinstance(self.row, int) or self.row < 0:
            raise ValueError("Row must be a non-negative integer")
        if not isinstance(self.col, int) or self.col < 0:
            raise ValueError("Column must be a non-negative integer")
        if not isinstance(self.text, str) or not self.text.strip():
            raise ValueError("Text must be a non-empty string")
        if self.id is not None and (not isinstance(self.id, str) or not self.id.strip()):
            raise ValueError("ID must be a non-empty string when provided")
        
        # If header has colspan but no id, it's a parent header (valid case)
        # If header has no colspan, it must have an id
        if self.colspan is None and self.id is None:
            raise ValueError("Header entry must have either 'id' or 'colspan'")


@dataclass
class SheetConfig:
    """Configuration for a single sheet."""
    start_row: int
    header_to_write: List[HeaderEntry]
    mappings: Dict[str, Any]
    footer_configurations: Dict[str, Any]
    styling: Dict[str, Any]
    
    def __post_init__(self):
        """Validate sheet configuration data after initialization."""
        if not isinstance(self.start_row, int) or self.start_row < 0:
            raise ValueError("Start row must be a non-negative integer")
        if not isinstance(self.header_to_write, list):
            raise ValueError("Header to write must be a list")
        if not isinstance(self.mappings, dict):
            raise ValueError("Mappings must be a dictionary")
        if not isinstance(self.footer_configurations, dict):
            raise ValueError("Footer configurations must be a dictionary")
        if not isinstance(self.styling, dict):
            raise ValueError("Styling must be a dictionary")


@dataclass
class ConfigurationData:
    """Complete configuration data structure."""
    sheets_to_process: List[str]
    sheet_data_map: Dict[str, str]
    data_mapping: Dict[str, SheetConfig]
    
    def __post_init__(self):
        """Validate configuration data after initialization."""
        if not isinstance(self.sheets_to_process, list):
            raise ValueError("Sheets to process must be a list")
        if not isinstance(self.sheet_data_map, dict):
            raise ValueError("Sheet data map must be a dictionary")
        if not isinstance(self.data_mapping, dict):
            raise ValueError("Data mapping must be a dictionary")
        
        # Validate that all sheets in sheets_to_process have corresponding data_mapping entries
        for sheet_name in self.sheets_to_process:
            if sheet_name not in self.data_mapping:
                raise ValueError(f"Sheet '{sheet_name}' in sheets_to_process missing from data_mapping")