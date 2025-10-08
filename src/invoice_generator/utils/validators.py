#!/usr/bin/env python3
"""
Invoice Generator Utils - Input Validation
Clean validation logic with detailed error reporting
"""

from pathlib import Path
from typing import Dict, Any, List


class InputValidator:
    """Validates inputs for invoice generation"""
    
    def __init__(self):
        self.supported_input_formats = {'.json', '.pkl', '.pickle'}
        self.supported_output_formats = {'.xlsx'}
    
    def validate_generation_inputs(
        self, 
        input_file: Path, 
        output_file: Path
    ) -> Dict[str, Any]:
        """
        Validate inputs for invoice generation
        
        Args:
            input_file: Input file path
            output_file: Output file path
            
        Returns:
            Dictionary with validation results
        """
        errors = []
        warnings = []
        
        # Validate input file
        input_errors = self._validate_input_file(input_file)
        errors.extend(input_errors)
        
        # Validate output file
        output_errors = self._validate_output_file(output_file)
        errors.extend(output_errors)
        
        # Check for conflicts
        if input_file.resolve() == output_file.resolve():
            errors.append("Input and output files cannot be the same")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    def _validate_input_file(self, input_file: Path) -> List[str]:
        """Validate input file"""
        errors = []
        
        if not input_file.exists():
            errors.append(f"Input file does not exist: {input_file}")
            return errors  # No point checking further
        
        if not input_file.is_file():
            errors.append(f"Input path is not a file: {input_file}")
        
        if input_file.suffix.lower() not in self.supported_input_formats:
            errors.append(
                f"Unsupported input format: {input_file.suffix}. "
                f"Supported: {', '.join(self.supported_input_formats)}"
            )
        
        # Check file is readable
        try:
            with open(input_file, 'rb') as f:
                f.read(1)  # Try to read one byte
        except PermissionError:
            errors.append(f"Permission denied reading input file: {input_file}")
        except Exception as e:
            errors.append(f"Cannot read input file {input_file}: {e}")
        
        return errors
    
    def _validate_output_file(self, output_file: Path) -> List[str]:
        """Validate output file"""
        errors = []
        
        if output_file.suffix.lower() not in self.supported_output_formats:
            errors.append(
                f"Unsupported output format: {output_file.suffix}. "
                f"Supported: {', '.join(self.supported_output_formats)}"
            )
        
        # Check output directory exists and is writable
        output_dir = output_file.parent
        if not output_dir.exists():
            try:
                output_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                errors.append(f"Cannot create output directory {output_dir}: {e}")
        
        # Check if we can write to the output location
        if output_file.exists():
            try:
                # Test write access by opening in append mode
                with open(output_file, 'a'):
                    pass
            except PermissionError:
                errors.append(f"Permission denied writing to output file: {output_file}")
            except Exception as e:
                errors.append(f"Cannot write to output file {output_file}: {e}")
        else:
            # Test write access to directory
            try:
                test_file = output_dir / '.write_test'
                with open(test_file, 'w') as f:
                    f.write('test')
                test_file.unlink()
            except Exception as e:
                errors.append(f"Cannot write to output directory {output_dir}: {e}")
        
        return errors
    
    def validate_template_config(
        self, 
        template_file: Path, 
        config_file: Path
    ) -> Dict[str, Any]:
        """
        Validate template and config file pair
        
        Args:
            template_file: Template Excel file
            config_file: Configuration JSON file
            
        Returns:
            Dictionary with validation results
        """
        errors = []
        warnings = []
        
        # Check template file
        if not template_file.exists():
            errors.append(f"Template file does not exist: {template_file}")
        elif not template_file.suffix.lower() == '.xlsx':
            errors.append(f"Template must be Excel file (.xlsx): {template_file}")
        
        # Check config file
        if not config_file.exists():
            errors.append(f"Config file does not exist: {config_file}")
        elif not config_file.suffix.lower() == '.json':
            errors.append(f"Config must be JSON file (.json): {config_file}")
        
        # If both exist, try to validate compatibility
        if template_file.exists() and config_file.exists():
            compatibility_errors = self._validate_template_config_compatibility(
                template_file, config_file
            )
            errors.extend(compatibility_errors)
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    def _validate_template_config_compatibility(
        self, 
        template_file: Path, 
        config_file: Path
    ) -> List[str]:
        """Check if template and config are compatible"""
        errors = []
        
        try:
            # Load config
            import json
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Load template to check sheets
            import openpyxl
            workbook = openpyxl.load_workbook(template_file, read_only=True)
            template_sheets = set(workbook.sheetnames)
            workbook.close()
            
            # Check if configured sheets exist in template
            sheets_to_process = config.get('sheets_to_process', [])
            for sheet_name in sheets_to_process:
                if sheet_name not in template_sheets:
                    errors.append(
                        f"Sheet '{sheet_name}' configured in {config_file} "
                        f"but not found in template {template_file}"
                    )
            
        except Exception as e:
            errors.append(f"Error validating template/config compatibility: {e}")
        
        return errors


class ConfigValidator:
    """Validates configuration data and structure"""
    
    def __init__(self):
        self.required_config_fields = {'sheets_to_process', 'template_file'}
    
    def validate_config_structure(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate configuration structure
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Dictionary with validation results
        """
        errors = []
        warnings = []
        
        # Check required fields
        for field in self.required_config_fields:
            if field not in config:
                errors.append(f"Missing required config field: {field}")
        
        # Validate sheets_to_process
        if 'sheets_to_process' in config:
            sheets = config['sheets_to_process']
            if not isinstance(sheets, list):
                errors.append("sheets_to_process must be a list")
            elif len(sheets) == 0:
                warnings.append("sheets_to_process is empty")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }


class PathValidator:
    """Validates file and directory paths"""
    
    def __init__(self):
        self.max_path_length = 260  # Windows MAX_PATH
    
    def validate_path(self, path: Path) -> Dict[str, Any]:
        """
        Validate a file or directory path
        
        Args:
            path: Path to validate
            
        Returns:
            Dictionary with validation results
        """
        errors = []
        warnings = []
        
        # Check path length
        if len(str(path)) > self.max_path_length:
            warnings.append(f"Path length ({len(str(path))}) exceeds recommended maximum ({self.max_path_length})")
        
        # Check for invalid characters
        invalid_chars = '<>:"|?*'
        for char in invalid_chars:
            if char in str(path):
                errors.append(f"Path contains invalid character: {char}")
        
        # Check if path is absolute
        if not path.is_absolute():
            warnings.append("Path is not absolute - may cause issues in different working directories")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }