#!/usr/bin/env python3
"""
Service-Oriented Invoice Generator
Custom exceptions for better error handling
"""

class InvoiceGenerationError(Exception):
    """Base exception for the invoice generator service."""
    pass

class ConfigError(InvoiceGenerationError):
    """Exception raised for errors in configuration files."""
    pass

class ConfigNotFound(ConfigError):
    """Raised when a company configuration file is not found"""
    pass

class DataParsingError(InvoiceGenerationError):
    """Exception raised for errors when parsing input data."""
    pass

class TemplateNotFound(InvoiceGenerationError):
    """Exception raised when a template file cannot be found."""
    pass

class RenderingError(InvoiceGenerationError):
    """Exception raised during the template rendering/filling process."""
    pass

