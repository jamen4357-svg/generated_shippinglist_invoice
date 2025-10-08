#!/usr/bin/env python3
"""
Service-Oriented Invoice Generator
Component: Template Filler - The primary orchestrator for filling a sheet.
"""

import logging
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.workbook.workbook import Workbook
from ..models import InvoiceData, CompanyConfig
from ..exceptions import RenderingError
from ..operations import (
    CellOperations, RowOperations, MergeOperations, HeaderOperations, StyleOperations, FooterOperations
)

class TemplateFiller:
    """
    Orchestrates the entire process of filling a worksheet using dedicated
    operation classes.
    """

    def __init__(self):
        """Initializes the filler with all necessary operation handlers."""
        self.cell_ops = CellOperations()
        self.row_ops = RowOperations()
        self.merge_ops = MergeOperations()
        self.header_ops = HeaderOperations()
        self.style_ops = StyleOperations()
        self.footer_ops = FooterOperations()

    def fill(self, workbook: Workbook, data: InvoiceData, config: CompanyConfig):
        """
        Fills an Excel workbook with invoice data.
        """
        logging.info(f"Starting to fill workbook for invoice '{data.invoice_id}'")
        
        try:
            # For now, we operate on the active sheet. A multi-sheet config would be handled here.
            sheet = workbook.active
            
            # --- Main Orchestration Flow ---
            # 1. Fill static placeholder fields (e.g., {{invoice_id}})
            self._fill_static_fields(sheet, data, config)

            # 2. Write the main table header and get its dimensions/map
            header_info = self._write_header(sheet, config)

            # 3. Fill the dynamic line item table and get the next available row
            next_row = self._fill_table_data(sheet, data, config, header_info)

            # 4. Write the footer section below the table
            next_row = self._write_footer(sheet, next_row, data, config, header_info)
            
            # 5. Apply formatting and merge rules from the config
            self._apply_merges(sheet, config)
            
            # 6. Apply column widths
            self._apply_column_widths(sheet, config, header_info)

            logging.info(f"Successfully filled workbook for invoice '{data.invoice_id}'")

        except Exception as e:
            logging.error(f"An error occurred during the fill process: {e}", exc_info=True)
            raise RenderingError(f"An error occurred while filling the template: {e}")

    def _fill_static_fields(self, sheet: Worksheet, data: InvoiceData, config: CompanyConfig):
        """Fills static placeholder fields using a find-and-replace mechanism."""
        logging.debug("Filling static fields...")
        
        # Create a dictionary of all possible replacement values from the data model
        replacements = {f"{{{{{field}}}}}": getattr(data, field) for field in data.model_fields}
        
        # Filter out any placeholders where the data value is None
        valid_replacements = {k: v for k, v in replacements.items() if v is not None}

        self.cell_ops.find_and_replace_in_sheet(sheet, valid_replacements)

    def _write_header(self, sheet: Worksheet, config: CompanyConfig) -> dict:
        """Writes the table header and returns its metadata."""
        logging.debug("Writing table header...")
        if not config.header_layout:
            logging.warning("No header layout defined in config. Skipping header writing.")
            return {}
        
        header_info = self.header_ops.write_header(
            worksheet=sheet,
            start_row=config.table_start_row,
            header_layout=config.header_layout,
            sheet_styling_config=config.styling
        )
        return header_info

    def _fill_table_data(self, sheet: Worksheet, data: InvoiceData, config: CompanyConfig, header_info: dict) -> int:
        """Fills the line item table and returns the next available row index."""
        logging.debug("Filling table data...")
        
        # The table starts right after the header
        start_row = config.table_start_row + header_info.get('header_rows', 0)
        columns = header_info.get('column_map', {})
        num_items = len(data.items)

        if num_items == 0:
            logging.warning("No items to fill in the table.")
            return start_row

        # Insert rows if the template has fewer placeholder rows than needed
        # Assuming template has 1 placeholder row
        rows_to_insert = num_items - 1
        if rows_to_insert > 0:
            logging.debug(f"Inserting {rows_to_insert} new rows at row {start_row + 1}")
            # We copy the style of the first data row placeholder
            self.row_ops.insert_rows_and_copy_styles(sheet, start_row, rows_to_insert)

        # Populate data
        for i, item in enumerate(data.items):
            current_row = start_row + i
            for field, col_letter in columns.items():
                if hasattr(item, field):
                    value = getattr(item, field)
                    if value is not None:
                        cell = sheet[f"{col_letter}{current_row}"]
                        cell.value = value
        
        next_row_after_table = start_row + num_items
        logging.debug(f"Populated {num_items} items. Next available row is {next_row_after_table}.")
        return next_row_after_table

    def _write_footer(self, sheet: Worksheet, start_row: int, data: InvoiceData, config: CompanyConfig, header_info: dict) -> int:
        """Writes the footer and returns the next available row index."""
        logging.debug(f"Writing footer starting at row {start_row}...")
        
        next_row = self.footer_ops.write_footer(
            worksheet=sheet,
            start_row=start_row,
            data=data,
            config=config,
            header_info=header_info
        )
        return next_row

    def _apply_merges(self, sheet: Worksheet, config: CompanyConfig):
        """Applies cell merging rules from the configuration."""
        if config.merge_rules:
            logging.debug("Applying merge rules...")
            self.merge_ops.merge_cells_by_config(sheet, config.merge_rules)
        else:
            logging.debug("No merge rules to apply.")
            
    def _apply_column_widths(self, sheet: Worksheet, config: CompanyConfig, header_info: dict):
        """Applies column widths from the styling configuration."""
        if config.styling and 'column_widths' in config.styling:
            logging.debug("Applying column widths...")
            column_map = header_info.get('column_map', {})
            for field, width in config.styling['column_widths'].items():
                if field in column_map:
                    col_letter = column_map[field]
                    sheet.column_dimensions[col_letter].width = width
        else:
            logging.debug("No column widths to apply.")



