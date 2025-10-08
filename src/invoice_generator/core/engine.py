#!/usr/bin/env python3
"""
Invoice Generator Core - Main Engine
Clean, orchestrated invoice generation workflow
"""

from pathlib import Path
from typing import Dict, Any, Optional
import time

from .config import InvoiceConfig, ConfigManager
from .result import (
    InvoiceResult, ResultBuilder, SheetResult, ProcessingStatus,
    create_template_not_found_error, create_validation_error,
    create_processing_error
)
from ..io.data_loader import DataLoader
from ..io.excel_writer import ExcelWriter
from ..processors.text_processor import TextProcessor
from ..processors.table_processor import TableProcessor
from ..utils.validators import InputValidator


class InvoiceEngine:
    """
    Main invoice generation engine
    Orchestrates the entire invoice generation process
    """
    
    def __init__(self, config: InvoiceConfig):
        self.config = config
        self.config_manager = ConfigManager(config)
        self.data_loader = DataLoader()
        self.validator = InputValidator()
        
    def generate(self, input_file: Path, output_file: Path) -> InvoiceResult:
        """
        Generate invoice from input file
        
        Args:
            input_file: Path to input JSON/PKL file
            output_file: Path for output Excel file
            
        Returns:
            InvoiceResult with processing details
        """
        builder = ResultBuilder()
        builder.set_input_file(input_file).set_output_path(output_file)
        
        try:
            # 1. Validate inputs
            validation_result = self._validate_inputs(input_file, output_file)
            if not validation_result['valid']:
                return builder.set_error(
                    create_validation_error(validation_result['error'])
                ).build()
            
            # 2. Load and validate data
            invoice_data = self._load_invoice_data(input_file)
            if not invoice_data:
                return builder.set_error(
                    create_processing_error("Failed to load invoice data")
                ).build()
            
            # 3. Resolve template and configuration
            template_config = self._resolve_template_config(input_file.name)
            if not template_config:
                return builder.set_error(
                    create_template_not_found_error(input_file.stem)
                ).build()
            
            builder.set_template(template_config['template_name'])
            builder.set_config(template_config['config_file'].name)
            
            # 4. Process invoice
            result = self._process_invoice(
                invoice_data, 
                template_config, 
                output_file, 
                builder
            )
            
            return result
            
        except Exception as e:
            return builder.set_error(
                create_processing_error(f"Unexpected error: {str(e)}")
            ).build()
    
    def _validate_inputs(self, input_file: Path, output_file: Path) -> Dict[str, Any]:
        """Validate input parameters"""
        return self.validator.validate_generation_inputs(input_file, output_file)
    
    def _load_invoice_data(self, input_file: Path) -> Optional[Dict[str, Any]]:
        """Load invoice data from file"""
        try:
            return self.data_loader.load_invoice_data(input_file)
        except Exception as e:
            if self.config.options.verbose:
                print(f"Error loading data: {e}")
            return None
    
    def _resolve_template_config(self, input_filename: str) -> Optional[Dict[str, Any]]:
        """Resolve template and configuration files"""
        return self.config_manager.resolve_template_config(input_filename)
    
    def _process_invoice(
        self, 
        invoice_data: Dict[str, Any],
        template_config: Dict[str, Any],
        output_file: Path,
        builder: ResultBuilder
    ) -> InvoiceResult:
        """Process the actual invoice generation"""
        
        try:
            # Initialize Excel writer
            excel_writer = ExcelWriter(
                template_file=template_config['template_file'],
                output_file=output_file
            )
            
            # Apply text replacements
            self._apply_text_replacements(excel_writer, invoice_data, template_config)
            
            # Process sheets
            sheets_to_process = self.config_manager.get_sheets_to_process(template_config)
            
            for sheet_name in sheets_to_process:
                sheet_result = self._process_sheet(
                    excel_writer, 
                    sheet_name, 
                    invoice_data, 
                    template_config
                )
                builder.add_sheet_result(sheet_result)
            
            # Save workbook
            excel_writer.save()
            
            return builder.build()
            
        except Exception as e:
            return builder.set_error(
                create_processing_error(f"Invoice processing failed: {str(e)}")
            ).build()
    
    def _apply_text_replacements(
        self, 
        excel_writer: ExcelWriter, 
        invoice_data: Dict[str, Any],
        template_config: Dict[str, Any]
    ):
        """Apply text replacements to the workbook"""
        text_processor = TextProcessor(self.config.options.verbose)
        text_processor.process_workbook(excel_writer.workbook, invoice_data)
    
    def _process_sheet(
        self,
        excel_writer: ExcelWriter,
        sheet_name: str,
        invoice_data: Dict[str, Any],
        template_config: Dict[str, Any]
    ) -> SheetResult:
        """Process a single sheet"""
        start_time = time.time()
        
        try:
            if sheet_name not in excel_writer.workbook.sheetnames:
                return SheetResult(
                    sheet_name=sheet_name,
                    status=ProcessingStatus.FAILED,
                    error=create_processing_error(f"Sheet '{sheet_name}' not found in template"),
                    processing_time=time.time() - start_time
                )
            
            worksheet = excel_writer.workbook[sheet_name]
            
            # Get sheet configuration
            sheet_config = self.config_manager.get_sheet_config(template_config, sheet_name)
            data_source = self.config_manager.get_sheet_data_source(template_config, sheet_name)
            
            if not sheet_config or not data_source:
                return SheetResult(
                    sheet_name=sheet_name,
                    status=ProcessingStatus.FAILED,
                    error=create_processing_error(f"No configuration found for sheet '{sheet_name}'"),
                    processing_time=time.time() - start_time
                )
            
            # Process table data
            table_processor = TableProcessor(
                verbose=self.config.options.verbose,
                enable_daf=self.config.options.enable_daf,
                enable_custom=self.config.options.enable_custom
            )
            
            rows_processed = table_processor.process_sheet(
                worksheet=worksheet,
                sheet_name=sheet_name,
                sheet_config=sheet_config,
                data_source=data_source,
                invoice_data=invoice_data
            )
            
            return SheetResult(
                sheet_name=sheet_name,
                status=ProcessingStatus.SUCCESS,
                rows_processed=rows_processed,
                processing_time=time.time() - start_time
            )
            
        except Exception as e:
            return SheetResult(
                sheet_name=sheet_name,
                status=ProcessingStatus.FAILED,
                error=create_processing_error(f"Sheet processing failed: {str(e)}", sheet_name),
                processing_time=time.time() - start_time
            )
    
    def list_templates(self) -> Dict[str, Any]:
        """List available templates"""
        templates = self.config_manager.list_available_templates()
        
        return {
            'templates': [
                {
                    'name': t['name'],
                    'has_config': t['has_config'],
                    'template_file': str(t['template_file']),
                    'config_file': str(t['config_file']) if t['config_file'] else None
                }
                for t in templates
            ],
            'count': len(templates)
        }


# Convenience function for simple usage
def generate_invoice(
    input_file: str | Path,
    output_file: str | Path,
    template_dir: str | Path,
    config_dir: str | Path,
    **options
) -> Dict[str, Any]:
    """
    Simple function for generating invoices
    
    Args:
        input_file: Path to input JSON file
        output_file: Path for output Excel file  
        template_dir: Path to template directory
        config_dir: Path to config directory
        **options: Processing options (verbose, enable_daf, etc.)
        
    Returns:
        Dictionary representation of InvoiceResult
    """
    from .config import create_config
    
    # Create configuration
    config = create_config(
        template_dir=template_dir,
        config_dir=config_dir,
        **options
    )
    
    # Create engine and generate
    engine = InvoiceEngine(config)
    result = engine.generate(Path(input_file), Path(output_file))
    
    return result.to_dict()