#!/usr/bin/env python3
"""
Service-Oriented Invoice Generator
Pydantic models for standardized data structures
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class InvoiceItem(BaseModel):
    """Represents a single line item in an invoice"""
    item_code: str
    description: str
    quantity: float
    unit_price: float
    total_price: float
    # Add other item-specific fields as needed
    # e.g., part_number: Optional[str] = None

class InvoiceData(BaseModel):
    """Represents the complete data for a single invoice"""
    invoice_id: str
    customer_name: str
    shipping_address: str
    items: List[InvoiceItem]
    total_amount: float
    
    # Add all other relevant fields from your JSON data
    # Use Optional for fields that may not always be present
    invoice_date: Optional[str] = None
    payment_terms: Optional[str] = None
    due_date: Optional[str] = None
    
    # Example of nested data structure
    # class ShippingDetails(BaseModel):
    #     carrier: str
    #     tracking_number: str
    # shipping_details: Optional[ShippingDetails] = None
    
    # Allow extra fields to accommodate variations in JSON data
    class Config:
        extra = "allow"

class CompanyConfig(BaseModel):
    """Represents the configuration for a specific company"""
    static_fields: Dict[str, str]
    table_start_row: int
    styling: Optional[Dict[str, Any]] = None
    footer_layout: Optional[List[Dict[str, Any]]] = None
    merge_rules: Optional[List[Dict[str, Any]]] = None
    header_layout: Optional[List[Dict[str, Any]]] = None
    # Add other config fields like merge rules, styling, etc.
    
    class Config:
        extra = "allow"
