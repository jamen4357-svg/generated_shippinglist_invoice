#!/usr/bin/env python3
"""
Invoice Generator IO - Data Loading
Clean data loading with multiple format support
"""

from pathlib import Path
from typing import Dict, Any, Optional
import json
import pickle


class DataLoader:
    """Handles loading invoice data from various formats"""
    
    def __init__(self):
        self.supported_formats = {'.json', '.pkl', '.pickle'}
    
    def load_invoice_data(self, input_file: Path) -> Dict[str, Any]:
        """
        Load invoice data from file
        
        Args:
            input_file: Path to input file
            
        Returns:
            Dictionary containing invoice data
            
        Raises:
            ValueError: If file format not supported
            FileNotFoundError: If file doesn't exist
            Exception: If file cannot be parsed
        """
        if not input_file.exists():
            raise FileNotFoundError(f"Input file not found: {input_file}")
        
        if input_file.suffix.lower() not in self.supported_formats:
            raise ValueError(
                f"Unsupported file format: {input_file.suffix}. "
                f"Supported formats: {', '.join(self.supported_formats)}"
            )
        
        if input_file.suffix.lower() == '.json':
            return self._load_json(input_file)
        elif input_file.suffix.lower() in {'.pkl', '.pickle'}:
            return self._load_pickle(input_file)
        else:
            raise ValueError(f"Unsupported format: {input_file.suffix}")
    
    def _load_json(self, file_path: Path) -> Dict[str, Any]:
        """Load JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not isinstance(data, dict):
                raise ValueError("JSON file must contain a dictionary at root level")
            
            return data
            
        except json.JSONDecodeError as e:
            raise Exception(f"Invalid JSON format in {file_path}: {e}")
        except Exception as e:
            raise Exception(f"Error reading JSON file {file_path}: {e}")
    
    def _load_pickle(self, file_path: Path) -> Dict[str, Any]:
        """Load pickle file"""
        try:
            with open(file_path, 'rb') as f:
                data = pickle.load(f)
            
            if not isinstance(data, dict):
                raise ValueError("Pickle file must contain a dictionary")
            
            return data
            
        except Exception as e:
            raise Exception(f"Error reading pickle file {file_path}: {e}")
    
    def validate_invoice_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate loaded invoice data structure
        
        Args:
            data: Loaded invoice data
            
        Returns:
            Dictionary with validation results
        """
        validation_result = {
            'valid': True,
            'warnings': [],
            'errors': []
        }
        
        # Check for required top-level keys
        required_keys = ['metadata']
        for key in required_keys:
            if key not in data:
                validation_result['errors'].append(f"Missing required key: {key}")
                validation_result['valid'] = False
        
        # Check for common data sources
        data_sources = [
            'processed_tables_data',
            'standard_aggregation_results', 
            'custom_aggregation_results',
            'final_DAF_compounded_result'
        ]
        
        found_sources = [key for key in data_sources if key in data]
        if not found_sources:
            validation_result['warnings'].append(
                "No recognized data sources found. Available: " + 
                ", ".join(data_sources)
            )
        
        # Validate metadata if present
        if 'metadata' in data:
            metadata = data['metadata']
            if not isinstance(metadata, dict):
                validation_result['errors'].append("metadata must be a dictionary")
                validation_result['valid'] = False
        
        return validation_result