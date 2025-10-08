#!/usr/bin/env python3
"""
Operations Package - Clean Excel Operations
Organized by concern, not by random utility growth
"""

from .cell_operations import CellOperations
from .merge_operations import MergeOperations  
from .style_operations import StyleOperations
from .data_operations import DataOperations
from .layout_operations import LayoutOperations
from .header_operations import HeaderOperations
from .row_operations import RowOperations
from .footer_operations import FooterOperations

__all__ = [
    'CellOperations',
    'MergeOperations',
    'StyleOperations', 
    'DataOperations',
    'LayoutOperations',
    'HeaderOperations',
    'RowOperations',
    'FooterOperations'
]