#!/usr/bin/env python3
"""
Clean Invoice Generator Core - Business Logic Only
Separated from CLI and API concerns for maintainability
"""

from pathlib import Path
from typing import Dict, Any, Optional
import json
import time
import openpyxl
from dataclasses import dataclass


@dataclass
class InvoiceConfig:
    """Clean configuration container"""
    template_dir: Path
    config_dir: Path
    enable_daf: bool = False
    enable_custom: bool = False
    verbose: bool = True


@dataclass
class InvoiceResult:
    """Clean result container"""
    success: bool
    output_path: Optional[str] = None
    error: Optional[str] = None
    duration: float = 0.0
    warnings: list = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []


class InvoiceGenerator:
    """Clean, focused invoice generator"""
    
    def __init__(self, config: InvoiceConfig):
        self.config = config
        self._load_utilities()
    
    def _load_utilities(self):
        """Load utility modules with proper error handling"""
        try:
            from . import invoice_utils, merge_utils, text_replace_utils
            self.utils_available = True
            self.invoice_utils = invoice_utils
            self.merge_utils = merge_utils
            self.text_utils = text_replace_utils
        except ImportError as e:
            self.utils_available = False
            self._log(f"Warning: Utility modules not available: {e}")
    
    def generate(self, input_path: Path, output_path: Path) -> InvoiceResult:
        """Generate invoice with clean error handling"""
        start_time = time.time()
        
        try:
            # Validate inputs
            if not self._validate_inputs(input_path):
                return InvoiceResult(
                    success=False, 
                    error="Invalid input file or configuration"
                )
            
            # Load data and config
            data = self._load_data(input_path)
            template_config = self._load_template_config(input_path)
            
            if not data or not template_config:
                return InvoiceResult(
                    success=False,
                    error="Failed to load data or configuration"
                )
            
            # Process invoice
            success = self._process_invoice(data, template_config, output_path)
            
            duration = time.time() - start_time
            
            if success:
                return InvoiceResult(
                    success=True,
                    output_path=str(output_path),
                    duration=duration
                )
            else:
                return InvoiceResult(
                    success=False,
                    error="Invoice processing failed",
                    duration=duration
                )
                
        except Exception as e:
            return InvoiceResult(
                success=False,
                error=f"Unexpected error: {str(e)}",
                duration=time.time() - start_time
            )
    
    def _validate_inputs(self, input_path: Path) -> bool:
        """Clean input validation"""
        return (
            input_path.exists() and 
            input_path.suffix.lower() in ['.json', '.pkl'] and
            self.config.template_dir.exists() and
            self.config.config_dir.exists()
        )
    
    def _load_data(self, input_path: Path) -> Optional[Dict[str, Any]]:
        """Clean data loading"""
        try:
            if input_path.suffix.lower() == '.json':
                with open(input_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            # Add pickle support if needed
            return None
        except Exception as e:
            self._log(f"Error loading data: {e}")
            return None
    
    def _load_template_config(self, input_path: Path) -> Optional[Dict[str, Any]]:
        """Clean template config loading"""
        # This would contain the template/config resolution logic
        # Simplified for this example
        config_name = input_path.stem
        config_file = self.config.config_dir / f"{config_name}_config.json"
        
        if not config_file.exists():
            # Try prefix matching
            prefix = config_name.split('25')[0] if '25' in config_name else config_name[:3]
            config_file = self.config.config_dir / f"{prefix}_config.json"
        
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self._log(f"Error loading config: {e}")
        
        return None
    
    def _process_invoice(self, data: Dict[str, Any], config: Dict[str, Any], output_path: Path) -> bool:
        """Clean invoice processing"""
        try:
            # Copy template
            template_name = self._get_template_name(data, config)
            template_path = self.config.template_dir / template_name
            
            if not template_path.exists():
                self._log(f"Template not found: {template_path}")
                return False
            
            # Copy to output
            import shutil
            shutil.copy2(template_path, output_path)
            
            # Process workbook
            workbook = openpyxl.load_workbook(output_path)
            
            # Text replacements
            self._apply_text_replacements(workbook, data, config)
            
            # Table processing
            self._process_tables(workbook, data, config)
            
            # Save
            workbook.save(output_path)
            workbook.close()
            
            return True
            
        except Exception as e:
            self._log(f"Error processing invoice: {e}")
            return False
    
    def _get_template_name(self, data: Dict[str, Any], config: Dict[str, Any]) -> str:
        """Determine template name from data/config"""
        # Implementation depends on your naming convention
        return "default.xlsx"
    
    def _apply_text_replacements(self, workbook, data: Dict[str, Any], config: Dict[str, Any]):
        """Clean text replacement logic"""
        if not self.utils_available:
            return
        
        # Use text_replace_utils for clean replacements
        # Implementation here...
        pass
    
    def _process_tables(self, workbook, data: Dict[str, Any], config: Dict[str, Any]):
        """Clean table processing logic"""
        if not self.utils_available:
            return
        
        sheets_config = config.get('sheet_data_map', {})
        
        for sheet_name, data_source in sheets_config.items():
            if sheet_name in workbook.sheetnames:
                worksheet = workbook[sheet_name]
                self._process_single_sheet(worksheet, sheet_name, data_source, data, config)
    
    def _process_single_sheet(self, worksheet, sheet_name: str, data_source: str, data: Dict[str, Any], config: Dict[str, Any]):
        """Process a single sheet with clean logic"""
        if data_source == 'aggregation':
            self._process_aggregation_sheet(worksheet, data, config)
        elif data_source in ['processed_tables_multi', 'processed_tables_data']:
            self._process_multi_table_sheet(worksheet, data, config)
    
    def _process_aggregation_sheet(self, worksheet, data: Dict[str, Any], config: Dict[str, Any]):
        """Clean aggregation processing"""
        # Implementation here...
        pass
    
    def _process_multi_table_sheet(self, worksheet, data: Dict[str, Any], config: Dict[str, Any]):
        """Clean multi-table processing"""
        # Implementation here...
        pass
    
    def _log(self, message: str):
        """Clean logging"""
        if self.config.verbose:
            print(message)


# Simple API wrapper
def generate_invoice(json_file_path: str, output_file_path: str, **kwargs) -> Dict[str, Any]:
    """Clean API function"""
    config = InvoiceConfig(
        template_dir=Path(kwargs.get('template_dir', './TEMPLATE')),
        config_dir=Path(kwargs.get('config_dir', './config')),
        verbose=kwargs.get('verbose', True)
    )
    
    generator = InvoiceGenerator(config)
    result = generator.generate(Path(json_file_path), Path(output_file_path))
    
    return {
        'success': result.success,
        'output_path': result.output_path,
        'error': result.error,
        'duration': result.duration,
        'warnings': result.warnings
    }