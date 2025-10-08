# src/invoice_generator_service/strategies/packing_list_strategy.py
from .base_strategy import GenerationStrategy
from ..models import InvoiceData, CompanyConfig

class PackingListStrategy(GenerationStrategy):
    """
    Strategy for generating a packing list.
    """
    def generate(self, data: InvoiceData, config: CompanyConfig, template_path: str, output_path: str):
        print("Generating packing list...")
        # Logic for generating a packing list will be implemented here.
        
        # For now, just a placeholder implementation
        print(f"Data: {data.model_dump_json(indent=2)}")
        print(f"Config: {config.model_dump_json(indent=2)}")
        print(f"Template: {template_path}")
        print(f"Output: {output_path}")

        # Placeholder: In a real scenario, we would save a file and return the path.
        with open(output_path, "w") as f:
            f.write("This is a packing list.")

        return output_path
