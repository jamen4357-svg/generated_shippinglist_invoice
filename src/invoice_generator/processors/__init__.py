#!/usr/bin/env python3
"""
Invoice Generator Processors Package
Clean modular processing components
"""

from .base_processor import BaseProcessor
from .text_processor import TextProcessor
from .table_processor import TableProcessor
from .aggregation_processor import AggregationProcessor

__all__ = [
    'BaseProcessor',
    'TextProcessor', 
    'TableProcessor',
    'AggregationProcessor'
]