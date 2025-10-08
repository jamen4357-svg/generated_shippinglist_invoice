# src/invoice_generator_service/strategies/base_strategy.py
from abc import ABC, abstractmethod
from ..models import InvoiceData, CompanyConfig

class GenerationStrategy(ABC):
    """
    The interface for an invoice or document generation strategy.
    """
    @abstractmethod
    def generate(self, data: InvoiceData, config: CompanyConfig, template_path: str, output_path: str):
        """
        Takes standardized data and a config, performs the generation logic,
        and returns the path to the output file.
        """
        pass
