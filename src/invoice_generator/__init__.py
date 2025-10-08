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


# Export the main API functions
__all__ = ['generate_invoice', 'hybrid_generate_invoice', 'generate_invoice_api']

def generate_invoice_api(*args, **kwargs):
    """Direct access to the API function for advanced usage."""
    from .generate_invoice import generate_invoice_api as _api
    return _api(*args, **kwargs)
