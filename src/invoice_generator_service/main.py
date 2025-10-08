#!/usr/bin/env python3
"""
Command-Line Interface for the Invoice Generation Service (Strategy Pattern)
"""

import argparse
import logging
import os
from .service import InvoiceService
from .exceptions import InvoiceGenerationError
from .strategies.base_strategy import GenerationStrategy
from .strategies.standard_invoice_strategy import StandardInvoiceStrategy
from .strategies.hybrid_invoice_strategy import HybridInvoiceStrategy
from .strategies.packing_list_strategy import PackingListStrategy
from .components.data_parser import DataParser
from .components.config_loader import ConfigLoader

# A factory mapping strategy names to their classes
STRATEGY_MAP = {
    "standard": StandardInvoiceStrategy,
    "hybrid": HybridInvoiceStrategy,
    "packing": PackingListStrategy,
}

def setup_logging():
    """Sets up basic logging for the CLI tool."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    )

def main():
    """Main function to run the invoice generation service from the command line."""
    setup_logging()
    
    parser = argparse.ArgumentParser(description="Generate a document using the Invoice Service.")
    parser.add_argument("company_id", help="The company identifier (e.g., 'JF', 'MOTO').")
    parser.add_argument("input_file", help="Path to the input JSON data file.")
    parser.add_argument("output_file", help="Path to save the generated .xlsx document.")
    parser.add_argument(
        "--strategy",
        required=True,
        choices=STRATEGY_MAP.keys(),
        help="The generation strategy to use."
    )
    
    args = parser.parse_args()

    logging.info(f"Starting document generation with strategy '{args.strategy}' for company '{args.company_id}'")

    try:
        # 1. Select the strategy from the factory
        strategy_class = STRATEGY_MAP.get(args.strategy)
        if not strategy_class:
            raise InvoiceGenerationError(f"Unknown strategy: {args.strategy}")
        
        strategy_instance: GenerationStrategy = strategy_class()

        # 2. The CLI is now responsible for preparing the data models
        data_parser = DataParser()
        config_loader = ConfigLoader(configs_dir="src/invoice_generator_service/configs")
        
        invoice_data = data_parser.parse(args.input_file)
        company_config = config_loader.load(args.company_id)

        # 3. Determine template path (can be made more sophisticated later)
        template_path = f"src/invoice_generator_service/templates/{args.company_id}_template.xlsx"

        # 4. Instantiate the service with the chosen strategy
        invoice_service = InvoiceService(strategy=strategy_instance)

        # 5. Run the generation process
        invoice_service.generate(
            data=invoice_data,
            config=company_config,
            template_path=template_path,
            output_path=args.output_file
        )
        
        logging.info(f"Successfully completed document generation. Output at: {os.path.abspath(args.output_file)}")

    except InvoiceGenerationError as e:
        logging.error(f"An error occurred during generation: {e}", exc_info=True)
    except FileNotFoundError as e:
        logging.error(f"A required file was not found: {e}", exc_info=True)
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}", exc_info=True)

if __name__ == "__main__":
    main()

