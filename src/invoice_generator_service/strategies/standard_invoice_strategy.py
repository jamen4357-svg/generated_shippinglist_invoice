# src/invoice_generator_service/strategies/standard_invoice_strategy.py
import shutil
import openpyxl
import logging
import os
from .base_strategy import GenerationStrategy
from ..models import InvoiceData, CompanyConfig
from ..components.template_filler import TemplateFiller
from ..exceptions import InvoiceGenerationError

class StandardInvoiceStrategy(GenerationStrategy):
    """
    Strategy for generating a standard invoice.
    This strategy orchestrates the process using the TemplateFiller component.
    """
    def generate(self, data: InvoiceData, config: CompanyConfig, template_path: str, output_path: str) -> str:
        logging.info("Executing StandardInvoiceStrategy...")
        
        try:
            # 1. Ensure output directory exists
            output_dir = os.path.dirname(output_path)
            os.makedirs(output_dir, exist_ok=True)

            # 2. Prepare the output file by copying the template
            logging.debug(f"Copying template from '{template_path}' to '{output_path}'")
            shutil.copy(template_path, output_path)

            # 3. Load the new workbook
            workbook = openpyxl.load_workbook(output_path)
            
            # 4. Instantiate the component that does the heavy lifting
            filler = TemplateFiller()

            # 5. Use the filler to populate the workbook
            # The filler will handle replacements, header writing, table filling, etc.
            filler.fill(workbook, data, config)

            # 6. Save the modified workbook
            workbook.save(output_path)
            logging.info(f"Standard invoice generated successfully at '{output_path}'")

        except FileNotFoundError as e:
            logging.error(f"Template file not found for standard strategy: {e}")
            raise InvoiceGenerationError(f"Template file not found: {template_path}") from e
        except Exception as e:
            logging.error(f"An unexpected error occurred in StandardInvoiceStrategy: {e}", exc_info=True)
            raise InvoiceGenerationError(f"Failed to generate standard invoice: {e}") from e
            
        return output_path

