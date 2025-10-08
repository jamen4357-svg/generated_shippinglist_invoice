#!/usr/bin/env python3
"""
Service-Oriented Invoice Generator
Component: Data Parser
"""

import json
import logging
from typing import Dict, Any, List
from pydantic import ValidationError
from ..models import InvoiceData, InvoiceItem
from ..exceptions import DataParsingError

class DataParser:
    """Parses raw input data into a standardized InvoiceData model."""

    def parse(self, file_path: str) -> InvoiceData:
        """
        Loads data from a JSON file, transforms it, and validates it
        against the InvoiceData model.

        This is a critical step to standardize the data for the rest of the service.
        """
        logging.info(f"Starting data parsing for: {file_path}")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)

            # Detect format and parse accordingly
            if "processed_tables_data" in raw_data:
                logging.info("Detected 'CLW' data format.")
                return self._parse_clw_format(raw_data)
            else:
                logging.info("Detected 'JF' data format.")
                return self._parse_jf_format(raw_data)

        except FileNotFoundError:
            logging.error(f"Input data file not found: {file_path}")
            raise DataParsingError(f"Input data file not found: {file_path}")
        except json.JSONDecodeError:
            logging.error(f"Invalid JSON in file: {file_path}")
            raise DataParsingError(f"Invalid JSON in file: {file_path}")
        except ValidationError as e:
            logging.error(f"Data validation failed for {file_path}: {e}")
            raise DataParsingError(f"Data validation failed: {e}")
        except Exception as e:
            logging.error(f"An unexpected error occurred during data parsing for {file_path}: {e}", exc_info=True)
            raise DataParsingError(f"An unexpected error occurred during data parsing: {e}")

    def _parse_clw_format(self, raw_data: Dict[str, Any]) -> InvoiceData:
        """Parses the CLW-style data format."""
        items: List[InvoiceItem] = []
        total_amount = 0.0
        invoice_id = "N/A"
        invoice_date = None

        processed_data = raw_data.get("processed_tables_data", {})
        if not processed_data:
            raise DataParsingError("CLW format error: 'processed_tables_data' is missing or empty.")

        # Extract general info from the first item of the first table
        first_table_key = next(iter(processed_data))
        first_table = processed_data[first_table_key]
        if first_table.get("inv_no"):
            invoice_id = first_table["inv_no"][0]
        if first_table.get("inv_date"):
            invoice_date = first_table["inv_date"][0]

        for table_name, table_data in processed_data.items():
            num_rows = len(table_data.get("item", []))
            for i in range(num_rows):
                try:
                    amount = float(table_data.get("amount", [])[i] or 0.0)
                    item = InvoiceItem(
                        item_code=str(table_data.get("item", [])[i]),
                        description=table_data.get("description", [])[i] or "N/A",
                        quantity=float(table_data.get("sqft", [])[i] or 0.0),
                        unit_price=float(table_data.get("unit", [])[i] or 0.0),
                        total_price=amount,
                    )
                    items.append(item)
                    total_amount += amount
                except (ValueError, TypeError, IndexError) as e:
                    logging.warning(f"Skipping item in table '{table_name}' at row {i+1} due to data conversion error: {e}")
                    continue
        
        mapped_data = {
            'invoice_id': invoice_id,
            'customer_name': "CLW Customer", # Placeholder
            'shipping_address': "CLW Address", # Placeholder
            'items': items,
            'total_amount': total_amount,
            'invoice_date': invoice_date,
        }

        logging.info("Validating transformed CLW data against Pydantic model...")
        invoice_data = InvoiceData(**mapped_data)
        logging.info(f"Successfully parsed and validated data for invoice {invoice_id}.")
        return invoice_data

    def _parse_jf_format(self, raw_data: Dict[str, Any]) -> InvoiceData:
        """Parses the original JF-style data format."""
        # --- Data Transformation ---
        # This logic maps the complex, nested raw JSON to our clean Pydantic models.
        
        # 1. Extract top-level fields from various possible locations
        invoice_id = raw_data.get("invoice_info", {}).get("invoice_number") or raw_data.get("summary", {}).get("invoice_number", "N/A")
        customer_name = raw_data.get("customer_info", {}).get("name", "N/A")
        shipping_address = raw_data.get("customer_info", {}).get("address", "N/A")
        total_amount = float(raw_data.get("summary", {}).get("total_amount", 0.0))
        invoice_date = raw_data.get("invoice_info", {}).get("date")
        payment_terms = raw_data.get("invoice_info", {}).get("payment_terms")
        due_date = raw_data.get("invoice_info", {}).get("due_date")


        # 2. Process and aggregate line items from the 'raw_data' tables
        items: List[InvoiceItem] = []
        if "raw_data" in raw_data and isinstance(raw_data["raw_data"], dict):
            for table_name, table_data in raw_data["raw_data"].items():
                # Determine the number of rows from a reliable column, like 'po'
                num_rows = len(table_data.get("po", []))
                for i in range(num_rows):
                    try:
                        # Safely get values from each list, providing a default if index is out of bounds
                        item_code = table_data.get("item", [])[i] if i < len(table_data.get("item", [])) else "N/A"
                        description = table_data.get("description", [])[i] if i < len(table_data.get("description", [])) else "N/A"
                        quantity = float(table_data.get("sqft", [])[i] if i < len(table_data.get("sqft", [])) and table_data.get("sqft", [])[i] is not None else 0.0)
                        unit_price = float(table_data.get("unit", [])[i] if i < len(table_data.get("unit", [])) and table_data.get("unit", [])[i] is not None else 0.0)
                        total_price = float(table_data.get("amount", [])[i] if i < len(table_data.get("amount", [])) and table_data.get("amount", [])[i] is not None else 0.0)

                        item = InvoiceItem(
                            item_code=item_code,
                            description=description or "N/A",
                            quantity=quantity,
                            unit_price=unit_price,
                            total_price=total_price
                        )
                        items.append(item)
                    except (ValueError, TypeError) as e:
                        logging.warning(f"Skipping item in table '{table_name}' at row {i+1} due to data conversion error: {e}")
                        continue

        # 3. Assemble the final mapped data dictionary
        mapped_data = {
            'invoice_id': invoice_id,
            'customer_name': customer_name,
            'shipping_address': shipping_address,
            'items': items,
            'total_amount': total_amount,
            'invoice_date': invoice_date,
            'payment_terms': payment_terms,
            'due_date': due_date,
            # Pass through any other top-level data that might be useful
            'raw_metadata': raw_data.get('metadata', {}) 
        }
        
        # 4. Validate the mapped data with Pydantic
        logging.info("Validating transformed JF data against Pydantic model...")
        invoice_data = InvoiceData(**mapped_data)
        logging.info(f"Successfully parsed and validated data for invoice {invoice_id}.")
        return invoice_data


