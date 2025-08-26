"""
Core data models for Excel analysis tool.

This module contains simplified dataclasses for representing Excel font analysis results.
Focus is on extracting font name, font size, and start row information.
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Optional
import json


@dataclass
class FontInfo:
    """Represents basic font information (name and size only)."""
    name: str
    size: float
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


@dataclass
class HeaderMatch:
    """Represents a detected header keyword match."""
    keyword: str
    row: int
    column: int
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


@dataclass
class SheetAnalysis:
    """Analysis results for a single Excel sheet."""
    sheet_name: str
    header_font: FontInfo
    data_font: FontInfo
    start_row: int
    header_positions: List[HeaderMatch]
    
    def to_text(self) -> str:
        """Convert analysis results to simple text format."""
        return f"""Sheet: {self.sheet_name}
Header Font: {self.header_font.name}, Size: {self.header_font.size}
Data Font: {self.data_font.name}, Size: {self.data_font.size}
Start Row: {self.start_row}"""
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'sheet_name': self.sheet_name,
            'header_font': self.header_font.to_dict(),
            'data_font': self.data_font.to_dict(),
            'start_row': self.start_row,
            'header_positions': [pos.to_dict() for pos in self.header_positions]
        }


@dataclass
class AnalysisResult:
    """Complete analysis results for an Excel file."""
    file_path: str
    sheets: List[SheetAnalysis]
    timestamp: datetime
    
    def to_text(self) -> str:
        """Convert all analysis results to simple text format."""
        result = f"Excel Analysis Results\nFile: {self.file_path}\nAnalyzed: {self.timestamp}\n\n"
        for sheet in self.sheets:
            result += sheet.to_text() + "\n\n"
        return result
    
    def to_json(self, indent: int = 2) -> str:
        """Convert all analysis results to JSON format."""
        data = {
            'file_path': self.file_path,
            'timestamp': self.timestamp.isoformat(),
            'sheets': [sheet.to_dict() for sheet in self.sheets]
        }
        return json.dumps(data, indent=indent)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'file_path': self.file_path,
            'timestamp': self.timestamp.isoformat(),
            'sheets': [sheet.to_dict() for sheet in self.sheets]
        }