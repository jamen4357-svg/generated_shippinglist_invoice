# Strategies package
from .base_strategy import InvoiceGenerationStrategy
from .high_quality_strategy import HighQualityLeatherStrategy
from .second_layer_strategy import SecondLayerLeatherStrategy
from .components.excel_processor import ExcelProcessor
from .components.calculator import Calculator

# Strategy registry
STRATEGIES = {
    "high_quality": HighQualityLeatherStrategy(),
    "second_layer": SecondLayerLeatherStrategy(),
}

# Re-export utility functions that were in the original invoice_strategies.py
# These will be moved to utils/ in future phases
def apply_print_settings_to_files(*args, **kwargs):
    """Placeholder - will be moved to utils/"""
    pass

def create_download_zip(*args, **kwargs):
    """Placeholder - will be moved to utils/"""
    pass