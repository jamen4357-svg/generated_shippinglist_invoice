"""
Main Excel analysis functionality.

This module provides the ExcelAnalyzer class that coordinates header detection
and font extraction to analyze Excel files and generate analysis results.
"""

from datetime import datetime
from pathlib import Path
from typing import List, Optional
import json
import openpyxl
from openpyxl.workbook.workbook import Workbook
from openpyxl.worksheet.worksheet import Worksheet

from models.data_models import AnalysisResult, SheetAnalysis, FontInfo, HeaderMatch
from analyzers.header_detector import HeaderDetector
from analyzers.font_extractor import FontExtractor


class ExcelAnalyzer:
    """Main class that coordinates Excel file analysis."""
    
    def __init__(self, quantity_mode: bool = False):
        """Initialize the ExcelAnalyzer with detector and extractor components.
        
        Args:
            quantity_mode: If True, adds PCS and SQFT columns for packing list sheets
        """
        self.header_detector = HeaderDetector(quantity_mode=quantity_mode)
        self.font_extractor = FontExtractor()
    
    def analyze_file(self, file_path: str) -> AnalysisResult:
        """
        Analyze an Excel file and extract font information and start row data.
        
        Args:
            file_path: Path to the Excel file to analyze
            
        Returns:
            AnalysisResult containing analysis data for all sheets
            
        Raises:
            FileNotFoundError: If the Excel file doesn't exist
            Exception: If the file cannot be opened or analyzed
        """
        # Validate file exists
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Excel file not found: {file_path}")
        
        try:
            # Load Excel file using openpyxl
            workbook = openpyxl.load_workbook(file_path, data_only=True)
            
            # Process each worksheet separately
            sheet_analyses = []
            for sheet_name in workbook.sheetnames:
                worksheet = workbook[sheet_name]
                sheet_analysis = self._analyze_worksheet(worksheet, sheet_name)
                if sheet_analysis:
                    sheet_analyses.append(sheet_analysis)
            
            # Generate AnalysisResult with text output
            return AnalysisResult(
                file_path=str(path.absolute()),
                sheets=sheet_analyses,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            raise Exception(f"Failed to analyze Excel file '{file_path}': {str(e)}")
    
    def _analyze_worksheet(self, worksheet: Worksheet, sheet_name: str) -> Optional[SheetAnalysis]:
        """
        Analyze a single worksheet for headers and font information.
        
        Args:
            worksheet: The openpyxl worksheet to analyze
            sheet_name: Name of the worksheet
            
        Returns:
            SheetAnalysis object or None if analysis fails
        """
        try:
            # Find headers using HeaderDetector
            header_positions = self.header_detector.find_headers(worksheet)
            
            # Calculate start row
            start_row = self.header_detector.calculate_start_row(header_positions)
            
            # Extract font information using FontExtractor
            header_font, data_font = self.font_extractor.extract_header_and_data_fonts(
                worksheet, header_positions
            )
            
            # Create SheetAnalysis object
            return SheetAnalysis(
                sheet_name=sheet_name,
                header_font=header_font,
                data_font=data_font,
                start_row=start_row,
                header_positions=header_positions
            )
            
        except Exception as e:
            # Log warning but continue with other sheets
            print(f"Warning: Failed to analyze sheet '{sheet_name}': {str(e)}")
            return None
    
    def analyze_and_output_text(self, file_path: str) -> str:
        """
        Analyze an Excel file and return results as formatted text.
        
        Args:
            file_path: Path to the Excel file to analyze
            
        Returns:
            Formatted text string with analysis results
        """
        try:
            analysis_result = self.analyze_file(file_path)
            return analysis_result.to_text()
        except Exception as e:
            return f"Error analyzing file: {str(e)}"
    
    def analyze_and_output_json(self, file_path: str, indent: int = 2) -> str:
        """
        Analyze an Excel file and return results as JSON.
        
        Args:
            file_path: Path to the Excel file to analyze
            indent: JSON indentation level
            
        Returns:
            JSON string with analysis results
        """
        try:
            analysis_result = self.analyze_file(file_path)
            return analysis_result.to_json(indent=indent)
        except Exception as e:
            error_result = {
                "error": f"Error analyzing file: {str(e)}",
                "file_path": file_path,
                "timestamp": datetime.now().isoformat()
            }
            return json.dumps(error_result, indent=indent)