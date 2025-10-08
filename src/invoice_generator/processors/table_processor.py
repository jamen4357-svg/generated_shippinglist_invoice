#!/usr/bin/env python3
"""
Invoice Generator Processors - Table Processing
Clean table data processing logic extracted and modularized
"""

from typing import Dict, Any, Optional
from openpyxl.worksheet.worksheet import Worksheet


class TableProcessor:
    """Handles table data processing for invoice sheets"""
    
    def __init__(self, verbose: bool = True, enable_daf: bool = False, enable_custom: bool = False):
        self.verbose = verbose
        self.enable_daf = enable_daf
        self.enable_custom = enable_custom
    
    def process_sheet(
        self,
        worksheet: Worksheet,
        sheet_name: str,
        sheet_config: Dict[str, Any],
        data_source: str,
        invoice_data: Dict[str, Any]
    ) -> int:
        """
        Process table data for a sheet
        
        Args:
            worksheet: Excel worksheet to process
            sheet_name: Name of the sheet
            sheet_config: Configuration for this sheet
            data_source: Data source indicator (e.g., 'aggregation', 'processed_tables_data')
            invoice_data: Complete invoice data
            
        Returns:
            Number of rows processed
        """
        if self.verbose:
            print(f"Processing sheet '{sheet_name}' as {data_source}")
        
        if data_source in ['aggregation', 'DAF_aggregation']:
            return self._process_aggregation_sheet(
                worksheet, sheet_name, sheet_config, invoice_data
            )
        elif data_source in ['processed_tables_data', 'processed_tables_multi']:
            return self._process_multi_table_sheet(
                worksheet, sheet_name, sheet_config, invoice_data
            )
        else:
            if self.verbose:
                print(f"Unknown data source: {data_source}")
            return 0
    
    def _process_aggregation_sheet(
        self,
        worksheet: Worksheet,
        sheet_name: str,
        sheet_config: Dict[str, Any],
        invoice_data: Dict[str, Any]
    ) -> int:
        """Process sheet with aggregation data"""
        try:
            # Import existing processing logic
            from .. import invoice_utils
            
            # Use existing aggregation processing
            success = self._call_existing_processor(
                worksheet=worksheet,
                sheet_name=sheet_name,
                sheet_config=sheet_config,
                data_source_indicator='aggregation',
                invoice_data=invoice_data
            )
            
            if success:
                # Extract row count from sheet config or estimate
                start_row = sheet_config.get('start_row', 18)
                return self._count_processed_rows(worksheet, start_row)
            else:
                return 0
                
        except ImportError:
            if self.verbose:
                print("Warning: invoice_utils not available")
            return 0
        except Exception as e:
            if self.verbose:
                print(f"Error processing aggregation sheet: {e}")
            return 0
    
    def _process_multi_table_sheet(
        self,
        worksheet: Worksheet,
        sheet_name: str,
        sheet_config: Dict[str, Any],
        invoice_data: Dict[str, Any]
    ) -> int:
        """Process sheet with multi-table data"""
        try:
            # Import existing processing logic
            from .. import invoice_utils
            
            # Use existing multi-table processing
            success = self._call_existing_processor(
                worksheet=worksheet,
                sheet_name=sheet_name,
                sheet_config=sheet_config,
                data_source_indicator='processed_tables_data',
                invoice_data=invoice_data
            )
            
            if success:
                # Count processed rows
                start_row = sheet_config.get('start_row', 18)
                return self._count_processed_rows(worksheet, start_row)
            else:
                return 0
                
        except ImportError:
            if self.verbose:
                print("Warning: invoice_utils not available")
            return 0
        except Exception as e:
            if self.verbose:
                print(f"Error processing multi-table sheet: {e}")
            return 0
    
    def _call_existing_processor(
        self,
        worksheet: Worksheet,
        sheet_name: str,
        sheet_config: Dict[str, Any],
        data_source_indicator: str,
        invoice_data: Dict[str, Any]
    ) -> bool:
        """Call the existing processing function"""
        try:
            # This is a bridge to the existing complex processing logic
            # Until we fully refactor, we'll use the existing process_single_table_sheet
            
            # Create a minimal args object for compatibility
            class ProcessingArgs:
                def __init__(self):
                    self.DAF = self.enable_daf
                    self.custom = self.enable_custom
                    self.verbose = self.verbose
            
            args = ProcessingArgs()
            
            # Import and call existing function
            from ..generate_invoice import process_single_table_sheet
            
            return process_single_table_sheet(
                worksheet=worksheet,
                sheet_name=sheet_name,
                sheet_mapping_section=sheet_config,
                data_mapping_config=sheet_config,  # Same as sheet_mapping_section for now
                args=args,
                invoice_data=invoice_data,
                data_source_indicator=data_source_indicator
            )
            
        except Exception as e:
            if self.verbose:
                print(f"Error calling existing processor: {e}")
            return False
    
    def _count_processed_rows(self, worksheet: Worksheet, start_row: int) -> int:
        """Count number of rows that appear to have been processed"""
        count = 0
        max_row = worksheet.max_row
        
        # Look for data starting from start_row
        for row in range(start_row, max_row + 1):
            # Check if row has any non-empty cells
            has_data = False
            for col in range(1, 15):  # Check first 14 columns
                cell = worksheet.cell(row=row, column=col)
                if cell.value is not None and str(cell.value).strip():
                    has_data = True
                    break
            
            if has_data:
                count += 1
            else:
                # Stop counting when we hit empty rows
                break
        
        return count
    
    def get_data_for_source(
        self, 
        invoice_data: Dict[str, Any], 
        data_source: str
    ) -> Optional[Dict[str, Any]]:
        """
        Extract data for a specific data source
        
        Args:
            invoice_data: Complete invoice data
            data_source: Data source identifier
            
        Returns:
            Data for the specified source, or None if not found
        """
        if data_source == 'aggregation':
            return invoice_data.get('standard_aggregation_results')
        elif data_source == 'DAF_aggregation':
            return invoice_data.get('final_DAF_compounded_result')
        elif data_source in ['processed_tables_data', 'processed_tables_multi']:
            return invoice_data.get('processed_tables_data')
        else:
            return None