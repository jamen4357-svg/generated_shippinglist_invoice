#!/usr/bin/env python3
"""
Invoice Generator Processors - Text Processing
Clean text replacement logic extracted and modularized
"""

from typing import Dict, Any
from openpyxl.workbook import Workbook


class TextProcessor:
    """Handles text replacements in Excel workbooks"""
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
    
    def process_workbook(self, workbook: Workbook, invoice_data: Dict[str, Any]):
        """
        Apply text replacements to entire workbook
        
        Args:
            workbook: Excel workbook to process
            invoice_data: Invoice data containing replacement values
        """
        if self.verbose:
            print("--- Running Invoice Header Replacement Task (within A1:N14) ---")
        
        try:
            # Import existing text replacement logic
            from .. import text_replace_utils
            
            # Apply text replacements using existing utility
            text_replace_utils.process_workbook_replacements(
                workbook, 
                invoice_data,
                search_range=(1, 14, 1, 14),  # A1:N14
                verbose=self.verbose
            )
            
            if self.verbose:
                print("--- Finished Invoice Header Replacement Task ---")
                
        except ImportError:
            if self.verbose:
                print("Warning: text_replace_utils not available, skipping text replacements")
        except Exception as e:
            if self.verbose:
                print(f"Warning: Text replacement failed: {e}")
    
    def process_sheet(
        self, 
        worksheet, 
        invoice_data: Dict[str, Any], 
        search_range: tuple = None
    ):
        """
        Apply text replacements to a specific sheet
        
        Args:
            worksheet: Excel worksheet to process
            invoice_data: Invoice data containing replacement values
            search_range: (start_row, end_row, start_col, end_col) or None for full sheet
        """
        try:
            from .. import text_replace_utils
            
            if search_range:
                start_row, end_row, start_col, end_col = search_range
            else:
                # Default to header area
                start_row, end_row, start_col, end_col = 1, 14, 1, 14
            
            text_replace_utils.process_sheet_replacements(
                worksheet,
                invoice_data,
                start_row=start_row,
                end_row=end_row,
                start_col=start_col,
                end_col=end_col,
                verbose=self.verbose
            )
            
        except ImportError:
            if self.verbose:
                print("Warning: text_replace_utils not available")
        except Exception as e:
            if self.verbose:
                print(f"Warning: Text replacement failed for sheet: {e}")
    
    def get_replacement_rules(self, invoice_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Extract replacement rules from invoice data
        
        Args:
            invoice_data: Invoice data
            
        Returns:
            Dictionary mapping placeholders to replacement values
        """
        rules = {}
        
        # Extract metadata-based replacements
        metadata = invoice_data.get('metadata', {})
        
        # Common placeholder mappings
        placeholder_mappings = {
            'JFREF': metadata.get('inv_ref', ''),
            'JFINV': metadata.get('inv_no', ''),
            'JFTIME': metadata.get('inv_date', ''),
            'WORKBOOK_FILENAME': metadata.get('workbook_filename', ''),
            'WORKSHEET_NAME': metadata.get('worksheet_name', ''),
            'TIMESTAMP': metadata.get('timestamp', '')
        }
        
        # Add non-empty values
        for placeholder, value in placeholder_mappings.items():
            if value:
                rules[placeholder] = str(value)
        
        return rules