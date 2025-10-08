#!/usr/bin/env python3
"""
Footer Operations - Clean Footer Writing Logic
"""

import logging
from typing import Dict, Any, List, Optional
from openpyxl.worksheet.worksheet import Worksheet
from ..models import InvoiceData, CompanyConfig
from .style_operations import StyleOperations

class FooterOperations:
    """A class to handle writing and styling footers in a worksheet."""

    def __init__(self, style_ops: Optional[StyleOperations] = None):
        self.style_ops = style_ops if style_ops else StyleOperations()

    def write_footer(
        self,
        worksheet: Worksheet,
        start_row: int,
        data: InvoiceData,
        config: CompanyConfig,
        header_info: Dict[str, Any]
    ) -> int:
        """
        Writes the footer section, including calculated totals.

        Args:
            worksheet: The openpyxl worksheet object.
            start_row: The row to start writing the footer.
            data: The standardized InvoiceData model.
            config: The company-specific configuration.
            header_info: Information about the table header, including column map.

        Returns:
            The next row index after the footer has been written.
        """
        if not config.footer_layout:
            logging.debug("No footer layout defined in config. Skipping footer.")
            return start_row

        logging.debug(f"Writing footer at start_row {start_row} on sheet '{worksheet.title}'")
        
        column_map = header_info.get('column_map', {})
        max_row_offset = 0

        # --- Perform Calculations ---
        # A simple example: calculating the total of the 'amount_usd' field.
        # A more robust version would get the field to sum from the config.
        total_amount = sum(item.amount_usd for item in data.items if item.amount_usd is not None)

        # Create a dictionary of values to be placed in the footer
        footer_values = {
            "total_amount_usd": total_amount,
            # Add other calculated values here as needed
        }

        for cell_config in config.footer_layout:
            label = cell_config.get('label', '')
            value_key = cell_config.get('value_key')
            
            # Determine the cell's value
            cell_value = label
            if value_key and value_key in footer_values:
                # If a value_key is present, combine label and value
                cell_value = f"{label}{footer_values[value_key]}"
            
            row_offset = cell_config.get('row', 1) - 1
            target_row = start_row + row_offset
            
            # Determine the column
            target_col_letter = cell_config.get('col')
            if not target_col_letter:
                # If 'col' isn't a letter, check if it maps to a table column
                field = cell_config.get('field')
                if field and field in column_map:
                    target_col_letter = column_map[field]
            
            if not target_col_letter:
                logging.warning(f"Could not determine column for footer cell: {cell_config}")
                continue

            cell = worksheet[f"{target_col_letter}{target_row}"]
            cell.value = cell_value

            # Apply styling
            style_key = cell_config.get('style_key')
            if config.styling and style_key and style_key in config.styling:
                style = config.styling[style_key]
                self.style_ops.apply_cell_style(cell, style)
            
            max_row_offset = max(max_row_offset, row_offset + 1)

        final_row = start_row + max_row_offset
        logging.debug(f"Footer written successfully. Ends at row {final_row -1}.")
        return final_row
