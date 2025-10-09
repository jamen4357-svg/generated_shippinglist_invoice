#!/usr/bin/env python3
"""
Service-Oriented Invoice Generator
Component: Template Filler - Uses Builder Pattern for invoice construction.
"""

import logging
from openpyxl.workbook.workbook import Workbook
from ..models import InvoiceData, CompanyConfig
from ..exceptions import RenderingError
from .invoice_layout_builder import InvoiceLayoutBuilder

class TemplateFiller:
    """
    Orchestrates invoice construction using the Builder pattern.
    Provides a clean interface while delegating complex construction to the builder.
    """

    def fill(self, workbook: Workbook, data: InvoiceData, config: CompanyConfig) -> Workbook:
        """
        Fills an Excel workbook with invoice data using the Builder pattern.

        Args:
            workbook: The Excel workbook to fill
            data: The invoice data to populate
            config: The company configuration

        Returns:
            The completed workbook
        """
        logging.info(f"Starting to fill workbook for invoice '{data.invoice_id}' using Builder pattern")

        try:
            # Use the builder pattern to construct the invoice
            completed_workbook = InvoiceLayoutBuilder.build_complete_invoice(
                workbook=workbook,
                data=data,
                config=config
            )

            logging.info(f"Successfully filled workbook for invoice '{data.invoice_id}'")
            return completed_workbook

        except Exception as e:
            logging.error(f"An error occurred during the fill process: {e}", exc_info=True)
            raise RenderingError(f"An error occurred while filling the template: {e}")

    # Alternative method for custom construction
    def fill_with_builder(self, workbook: Workbook, data: InvoiceData, config: CompanyConfig) -> InvoiceLayoutBuilder:
        """
        Returns a builder instance for custom invoice construction.
        Allows for more granular control over the building process.

        Returns:
            An InvoiceLayoutBuilder instance ready for custom construction
        """
        return InvoiceLayoutBuilder(workbook, data, config)



