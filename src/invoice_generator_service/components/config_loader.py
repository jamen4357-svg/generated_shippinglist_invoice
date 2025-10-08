#!/usr/bin/env python3
"""
Service-Oriented Invoice Generator
Component: Config Loader
"""

import json
from ..models import CompanyConfig
from ..exceptions import ConfigNotFound
from pydantic import ValidationError

class ConfigLoader:
    """Loads and validates company-specific configuration files"""
    
    def __init__(self, configs_dir="src/invoice_generator_service/configs"):
        self.configs_dir = configs_dir
    
    def load(self, company_id: str) -> CompanyConfig:
        """
        Loads the configuration for a specific company.
        
        Args:
            company_id: The identifier for the company (e.g., "BRO", "CLW")
            
        Returns:
            A validated CompanyConfig object
            
        Raises:
            ConfigNotFound: If the config file is not found or invalid
        """
        config_path = f"{self.configs_dir}/{company_id}_config.json"
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # Validate the config data with Pydantic
            company_config = CompanyConfig(**config_data)
            return company_config
            
        except FileNotFoundError:
            raise ConfigNotFound(f"Configuration file not found for company '{company_id}' at {config_path}")
        except json.JSONDecodeError:
            raise ConfigNotFound(f"Invalid JSON in config file: {config_path}")
        except ValidationError as e:
            raise ConfigNotFound(f"Configuration validation failed for '{company_id}': {e}")
        except Exception as e:
            raise ConfigNotFound(f"An unexpected error occurred while loading config for '{company_id}': {e}")
