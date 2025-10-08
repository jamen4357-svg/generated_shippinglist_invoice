#!/usr/bin/env python3
"""
Invoice Generator Core - Configuration Management
Clean, type-safe configuration handling
"""

from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
import json


@dataclass
class ProcessingOptions:
    """Processing options for invoice generation"""
    enable_daf: bool = False
    enable_custom: bool = False
    verbose: bool = True
    sheets_to_process: Optional[List[str]] = None


@dataclass
class InvoiceConfig:
    """Main configuration container"""
    template_dir: Path
    config_dir: Path
    options: ProcessingOptions = field(default_factory=ProcessingOptions)
    
    def __post_init__(self):
        """Validate paths on initialization"""
        if not self.template_dir.exists():
            raise ValueError(f"Template directory not found: {self.template_dir}")
        if not self.config_dir.exists():
            raise ValueError(f"Config directory not found: {self.config_dir}")


class ConfigManager:
    """Manages configuration loading and resolution"""
    
    def __init__(self, config: InvoiceConfig):
        self.config = config
        self._template_configs: Dict[str, Dict[str, Any]] = {}
    
    def resolve_template_config(self, input_filename: str) -> Optional[Dict[str, Any]]:
        """
        Resolve template and config files based on input filename
        
        Args:
            input_filename: Input file name (e.g., "CLW250039.json")
            
        Returns:
            Dictionary containing template and config info, or None if not found
        """
        # Extract base name
        base_name = Path(input_filename).stem
        
        # Try exact match first
        exact_config = self._try_exact_match(base_name)
        if exact_config:
            return exact_config
        
        # Try prefix match
        prefix_config = self._try_prefix_match(base_name)
        if prefix_config:
            return prefix_config
        
        return None
    
    def _try_exact_match(self, base_name: str) -> Optional[Dict[str, Any]]:
        """Try to find exact match for template and config"""
        template_file = self.config.template_dir / f"{base_name}.xlsx"
        config_file = self.config.config_dir / f"{base_name}_config.json"
        
        if template_file.exists() and config_file.exists():
            return self._load_template_config(template_file, config_file)
        
        return None
    
    def _try_prefix_match(self, base_name: str) -> Optional[Dict[str, Any]]:
        """Try to find prefix match (e.g., CLW250039 -> CLW)"""
        # Extract prefix (everything before first number)
        import re
        match = re.match(r'^([A-Za-z]+)', base_name)
        if not match:
            return None
        
        prefix = match.group(1)
        
        template_file = self.config.template_dir / f"{prefix}.xlsx"
        config_file = self.config.config_dir / f"{prefix}_config.json"
        
        if template_file.exists() and config_file.exists():
            return self._load_template_config(template_file, config_file)
        
        return None
    
    def _load_template_config(self, template_file: Path, config_file: Path) -> Dict[str, Any]:
        """Load and cache template configuration"""
        config_key = str(config_file)
        
        if config_key not in self._template_configs:
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                self._template_configs[config_key] = {
                    'template_file': template_file,
                    'config_file': config_file,
                    'config_data': config_data,
                    'template_name': template_file.stem
                }
            except Exception as e:
                raise ValueError(f"Failed to load config from {config_file}: {e}")
        
        return self._template_configs[config_key]
    
    def get_sheet_config(self, template_config: Dict[str, Any], sheet_name: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific sheet"""
        config_data = template_config.get('config_data', {})
        data_mapping = config_data.get('data_mapping', {})
        
        return data_mapping.get(sheet_name)
    
    def get_sheet_data_source(self, template_config: Dict[str, Any], sheet_name: str) -> Optional[str]:
        """Get data source indicator for a sheet"""
        config_data = template_config.get('config_data', {})
        sheet_data_map = config_data.get('sheet_data_map', {})
        
        return sheet_data_map.get(sheet_name)
    
    def get_sheets_to_process(self, template_config: Dict[str, Any]) -> List[str]:
        """Get list of sheets to process"""
        config_data = template_config.get('config_data', {})
        
        # Use config override if specified
        if self.config.options.sheets_to_process:
            return self.config.options.sheets_to_process
        
        # Otherwise use config file
        return config_data.get('sheets_to_process', [])
    
    def list_available_templates(self) -> List[Dict[str, Any]]:
        """List all available templates"""
        templates = []
        
        for template_file in self.config.template_dir.glob("*.xlsx"):
            # Look for corresponding config
            config_file = self.config.config_dir / f"{template_file.stem}_config.json"
            
            template_info = {
                'name': template_file.stem,
                'template_file': template_file,
                'has_config': config_file.exists(),
                'config_file': config_file if config_file.exists() else None
            }
            
            templates.append(template_info)
        
        return templates


def create_config(
    template_dir: str | Path,
    config_dir: str | Path,
    **options
) -> InvoiceConfig:
    """
    Create configuration with validation
    
    Args:
        template_dir: Path to template directory
        config_dir: Path to config directory
        **options: Processing options (enable_daf, enable_custom, verbose, etc.)
        
    Returns:
        Validated InvoiceConfig instance
    """
    processing_options = ProcessingOptions(**options)
    
    return InvoiceConfig(
        template_dir=Path(template_dir),
        config_dir=Path(config_dir),
        options=processing_options
    )