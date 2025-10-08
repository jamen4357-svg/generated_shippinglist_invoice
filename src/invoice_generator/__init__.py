#!/usr/bin/env python3
"""
Invoice Generator Package - Modular Architecture
Clean separation of concerns for maintainable invoice generation
"""

__version__ = "2.0.0"
__author__ = "Invoice Generator Team"
__description__ = "Modular invoice generation system"

# Legacy API functions for backward compatibility
def generate_invoice(json_file_path, output_file_path, flags=None, **kwargs):
    """API function to generate invoice programmatically."""
    # Import the module (avoid name collision by using different name)
    from .generate_invoice import generate_invoice as _generate_invoice_func
    
    # Call the implementation function directly
    return _generate_invoice_func(
        json_file_path=json_file_path,
        output_file_path=output_file_path,
        flags=flags,
        **kwargs
    )

def hybrid_generate_invoice(*args, **kwargs):
    """Wrapper function to import and call the main function from hybrid_generate_invoice.py"""
    from .hybrid_generate_invoice import main
    return main(*args, **kwargs)

def generate_invoice_api(*args, **kwargs):
    """Direct access to the API function for advanced usage."""
    from .generate_invoice import generate_invoice_api as _api
    return _api(*args, **kwargs)

# New Modular Architecture Components
try:
    # Core components
    from .core.config import ConfigManager, InvoiceConfig
    from .core.result import InvoiceResult, ProcessingStatus, ResultBuilder  
    from .core.engine import InvoiceEngine

    # Processors
    from .processors import TextProcessor, TableProcessor, AggregationProcessor

    # IO components  
    from .io.data_loader import DataLoader
    from .io.excel_writer import ExcelWriter

    # Utilities
    from .utils.validators import ConfigValidator, PathValidator
    
    # Extended exports for new architecture
    __all__ = [
        # Legacy API
        'generate_invoice', 
        'hybrid_generate_invoice', 
        'generate_invoice_api',
        
        # Core
        'ConfigManager',
        'InvoiceConfig', 
        'InvoiceResult',
        'ProcessingStatus',
        'ResultBuilder',
        'InvoiceEngine',
        
        # Processors
        'TextProcessor',
        'TableProcessor', 
        'AggregationProcessor',
        
        # IO
        'DataLoader',
        'ExcelWriter',
        
        # Utils
        'ConfigValidator',
        'PathValidator'
    ]

except ImportError:
    # Fallback to legacy API only if modular components not available
    __all__ = ['generate_invoice', 'hybrid_generate_invoice', 'generate_invoice_api']
