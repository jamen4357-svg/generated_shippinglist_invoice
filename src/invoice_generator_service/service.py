#!/usr/bin/env python3
"""
Service-Oriented Invoice Generator
Main InvoiceService Class - The Context for the Strategy Pattern
"""
from .strategies.base_strategy import GenerationStrategy
from .models import InvoiceData, CompanyConfig

class InvoiceService:
    """
    Acts as the Context for the Strategy pattern. It is configured with a
    generation strategy and delegates the generation task to it.
    """
    
    def __init__(self, strategy: GenerationStrategy):
        self._strategy = strategy

    @property
    def strategy(self) -> GenerationStrategy:
        return self._strategy

    @strategy.setter
    def strategy(self, strategy: GenerationStrategy):
        self._strategy = strategy

    def generate(self, data: InvoiceData, config: CompanyConfig, template_path: str, output_path: str) -> str:
        """
        Delegates the generation job to the configured strategy.

        Args:
            data (InvoiceData): The standardized data model.
            config (CompanyConfig): The company-specific configuration model.
            template_path (str): The path to the template file.
            output_path (str): The path where the output file will be saved.

        Returns:
            str: The path to the generated file.
        """
        print(f"InvoiceService: Delegating generation to {self._strategy.__class__.__name__}")
        
        # The actual work is done by the strategy object.
        result_path = self._strategy.generate(
            data=data,
            config=config,
            template_path=template_path,
            output_path=output_path
        )
        
        print(f"InvoiceService: Generation complete. File at: {result_path}")
        return result_path

