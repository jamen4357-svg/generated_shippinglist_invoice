#!/usr/bin/env python3
"""
Invoice Generator Processors - Aggregation Processor
Handles data aggregation processing for invoice generation
"""

from typing import Dict, Any, List, Optional
from .base_processor import BaseProcessor


class AggregationProcessor(BaseProcessor):
    """Handles aggregation data processing"""
    
    def __init__(self, verbose: bool = True, enable_daf: bool = False):
        super().__init__(verbose)
        self.enable_daf = enable_daf
    
    def process(
        self, 
        invoice_data: Dict[str, Any], 
        aggregation_type: str = 'standard'
    ) -> Optional[Dict[str, Any]]:
        """
        Process aggregation data
        
        Args:
            invoice_data: Complete invoice data
            aggregation_type: Type of aggregation ('standard' or 'DAF')
            
        Returns:
            Processed aggregation data or None if error
        """
        if not self.validate_input(invoice_data):
            return None
        
        if aggregation_type == 'standard':
            return self._process_standard_aggregation(invoice_data)
        elif aggregation_type == 'DAF' and self.enable_daf:
            return self._process_daf_aggregation(invoice_data)
        else:
            self.log(f"Unsupported aggregation type: {aggregation_type}", "ERROR")
            return None
    
    def _process_standard_aggregation(self, invoice_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process standard aggregation"""
        try:
            # Extract standard aggregation results
            aggregation_data = invoice_data.get('standard_aggregation_results')
            
            if not aggregation_data:
                self.log("No standard aggregation results found", "WARNING")
                return None
            
            self.log(f"Processing standard aggregation with {len(aggregation_data)} entries")
            
            # Process and validate the aggregation data
            processed_data = self._validate_aggregation_structure(aggregation_data)
            
            return processed_data
            
        except Exception as e:
            self.log(f"Error processing standard aggregation: {e}", "ERROR")
            return None
    
    def _process_daf_aggregation(self, invoice_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process DAF aggregation"""
        try:
            # Extract DAF aggregation results
            daf_data = invoice_data.get('final_DAF_compounded_result')
            
            if not daf_data:
                self.log("No DAF aggregation results found", "WARNING")
                return None
            
            self.log(f"Processing DAF aggregation")
            
            # Process and validate the DAF data
            processed_data = self._validate_aggregation_structure(daf_data)
            
            return processed_data
            
        except Exception as e:
            self.log(f"Error processing DAF aggregation: {e}", "ERROR")
            return None
    
    def _validate_aggregation_structure(self, data: Any) -> Dict[str, Any]:
        """Validate and normalize aggregation data structure"""
        if isinstance(data, list):
            # Convert list to dict if needed
            return {
                'items': data,
                'count': len(data),
                'type': 'list'
            }
        elif isinstance(data, dict):
            # Already a dict, ensure it has required fields
            return {
                'items': data.get('items', data),
                'count': len(data.get('items', data)),
                'type': 'dict',
                'metadata': data.get('metadata', {})
            }
        else:
            self.log(f"Unexpected aggregation data type: {type(data)}", "WARNING")
            return {
                'items': data,
                'count': 1 if data else 0,
                'type': 'unknown'
            }
    
    def get_aggregation_summary(self, processed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get summary of aggregation processing"""
        if not processed_data:
            return {'status': 'error', 'message': 'No data processed'}
        
        return {
            'status': 'success',
            'count': processed_data.get('count', 0),
            'type': processed_data.get('type', 'unknown'),
            'has_metadata': bool(processed_data.get('metadata'))
        }