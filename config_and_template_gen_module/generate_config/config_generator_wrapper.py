#!/usr/bin/env python3
"""
Config Generator Wrapper - Easy integration for external applications.

This wrapper makes it easy to use the Config Generator from other applications
by handling path resolution and providing a simple interface.
"""

import os
import sys
from pathlib import Path
from typing import Optional, Tuple, Dict, Any


class ConfigGeneratorWrapper:
    """
    Wrapper class for easy integration of Config Generator into other applications.
    
    This class handles path resolution and provides a simple interface for
    generating configurations from external applications.
    """
    
    def __init__(self, config_gen_path: Optional[str] = None):
        """
        Initialize the wrapper.
        
        Args:
            config_gen_path: Path to the config_gen directory. If None, assumes
                           it's in the same directory as this wrapper file.
        """
        if config_gen_path is None:
            # Assume config_gen is in the same directory as this wrapper
            self.config_gen_path = Path(__file__).parent
        else:
            self.config_gen_path = Path(config_gen_path)
        
        # Add config_gen to Python path
        if str(self.config_gen_path) not in sys.path:
            sys.path.insert(0, str(self.config_gen_path))
        
        # Verify required files exist
        self._verify_installation()
        
        # Import the main generator
        try:
            from config_generator.config_generator import ConfigGenerator, ConfigGeneratorError
            from config_generator.mapping_manager import MappingManager, MappingManagerError
            self.ConfigGenerator = ConfigGenerator
            self.ConfigGeneratorError = ConfigGeneratorError
            self.MappingManager = MappingManager
            self.MappingManagerError = MappingManagerError
        except ImportError as e:
            raise RuntimeError(f"Could not import Config Generator modules: {e}")
    
    def _verify_installation(self) -> None:
        """Verify that all required files are present."""
        required_files = [
            "sample_config.json",
            "mapping_config.json",
            "config_generator/__init__.py",
            "config_generator/config_generator.py",
            "config_generator/mapping_manager.py"
        ]
        
        missing_files = []
        for file_path in required_files:
            full_path = self.config_gen_path / file_path
            if not full_path.exists():
                missing_files.append(str(full_path))
        
        if missing_files:
            raise RuntimeError(f"Missing required files: {missing_files}")
    
    def generate_config(self, 
                       quantity_data_path: str,
                       output_path: Optional[str] = None,
                       template_path: Optional[str] = None,
                       mapping_config_path: Optional[str] = None) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Generate configuration from quantity data.
        
        Args:
            quantity_data_path: Path to quantity analysis JSON file
            output_path: Path for output config (optional, auto-generated if None)
            template_path: Path to template config (optional, uses default if None)
            mapping_config_path: Path to mapping config (optional, uses default if None)
            
        Returns:
            Tuple of (success: bool, output_path: str, info: dict)
        """
        try:
            # Resolve paths
            quantity_data_path = str(Path(quantity_data_path).resolve())
            
            if output_path is None:
                # Auto-generate output path
                input_name = Path(quantity_data_path).stem
                output_path = str(Path(quantity_data_path).parent / f"{input_name}_config.json")
            else:
                output_path = str(Path(output_path).resolve())
            
            if template_path is None:
                template_path = str(self.config_gen_path / "sample_config.json")
            else:
                template_path = str(Path(template_path).resolve())
            
            # Initialize generator
            generator = self.ConfigGenerator()
            
            # Generate configuration
            generator.generate_config(template_path, quantity_data_path, output_path)
            
            # Collect information
            info = {
                "template_used": template_path,
                "quantity_data": quantity_data_path,
                "output_file": output_path,
                "config_gen_path": str(self.config_gen_path)
            }
            
            return True, output_path, info
            
        except Exception as e:
            error_info = {
                "error": str(e),
                "error_type": type(e).__name__,
                "quantity_data": quantity_data_path,
                "config_gen_path": str(self.config_gen_path)
            }
            return False, str(e), error_info
    
    def add_sheet_mapping(self, quantity_name: str, template_name: str) -> bool:
        """
        Add a sheet name mapping.
        
        Args:
            quantity_name: Sheet name from quantity data
            template_name: Sheet name in template
            
        Returns:
            True if successful, False otherwise
        """
        try:
            mapping_config_path = str(self.config_gen_path / "mapping_config.json")
            manager = self.MappingManager(mapping_config_path)
            manager.add_sheet_mapping(quantity_name, template_name)
            manager.save_mappings()
            return True
        except Exception:
            return False
    
    def add_header_mapping(self, header_text: str, column_id: str) -> bool:
        """
        Add a header text mapping.
        
        Args:
            header_text: Header text from quantity data
            column_id: Column ID in template
            
        Returns:
            True if successful, False otherwise
        """
        try:
            mapping_config_path = str(self.config_gen_path / "mapping_config.json")
            manager = self.MappingManager(mapping_config_path)
            manager.add_header_mapping(header_text, column_id)
            manager.save_mappings()
            return True
        except Exception:
            return False
    
    def get_mappings(self) -> Dict[str, Any]:
        """
        Get current mappings.
        
        Returns:
            Dictionary with current sheet and header mappings
        """
        try:
            mapping_config_path = str(self.config_gen_path / "mapping_config.json")
            manager = self.MappingManager(mapping_config_path)
            return {
                "sheet_mappings": manager.sheet_mappings,
                "header_mappings": manager.header_mappings,
                "unrecognized_items": manager.get_unrecognized_items()
            }
        except Exception:
            return {"error": "Could not load mappings"}
    
    def validate_quantity_data(self, quantity_data_path: str) -> Tuple[bool, str]:
        """
        Validate quantity data file.
        
        Args:
            quantity_data_path: Path to quantity data file
            
        Returns:
            Tuple of (is_valid: bool, message: str)
        """
        try:
            from config_generator.quantity_data_loader import QuantityDataLoader
            loader = QuantityDataLoader()
            loader.load_quantity_data(quantity_data_path)
            return True, "Quantity data is valid"
        except Exception as e:
            return False, f"Validation failed: {e}"


# Convenience function for simple usage
def generate_config_simple(quantity_data_path: str, 
                          config_gen_path: Optional[str] = None,
                          output_path: Optional[str] = None) -> Tuple[bool, str]:
    """
    Simple function to generate config with minimal setup.
    
    Args:
        quantity_data_path: Path to quantity analysis JSON file
        config_gen_path: Path to config_gen directory (optional)
        output_path: Path for output config (optional)
        
    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        wrapper = ConfigGeneratorWrapper(config_gen_path)
        success, result, info = wrapper.generate_config(quantity_data_path, output_path)
        
        if success:
            return True, f"Configuration generated successfully: {result}"
        else:
            return False, f"Generation failed: {result}"
            
    except Exception as e:
        return False, f"Setup failed: {e}"


# Example usage
if __name__ == "__main__":
    # Example of how to use from another application
    
    # Method 1: Simple function
    success, message = generate_config_simple(
        quantity_data_path="path/to/your/data.json",
        config_gen_path="path/to/config_gen"  # Optional
    )
    print(f"Simple method: {message}")
    
    # Method 2: Wrapper class (more control)
    try:
        wrapper = ConfigGeneratorWrapper("path/to/config_gen")
        
        # Generate config
        success, output_path, info = wrapper.generate_config("path/to/your/data.json")
        
        if success:
            print(f"Generated: {output_path}")
            print(f"Info: {info}")
        else:
            print(f"Failed: {output_path}")
        
        # Add mappings if needed
        wrapper.add_sheet_mapping("NEW_SHEET", "Invoice")
        wrapper.add_header_mapping("NEW_HEADER", "col_amount")
        
        # Check current mappings
        mappings = wrapper.get_mappings()
        print(f"Current mappings: {len(mappings.get('sheet_mappings', {}))}")
        
    except Exception as e:
        print(f"Error: {e}")