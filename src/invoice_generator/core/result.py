#!/usr/bin/env python3
"""
Invoice Generator Core - Result and Error Handling
Clean result objects with type safety
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from pathlib import Path
from enum import Enum
import time


class ProcessingStatus(Enum):
    """Processing status enumeration"""
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"
    CANCELLED = "cancelled"


class ErrorCode(Enum):
    """Error code enumeration"""
    INVALID_INPUT = "INVALID_INPUT"
    TEMPLATE_NOT_FOUND = "TEMPLATE_NOT_FOUND"
    CONFIG_NOT_FOUND = "CONFIG_NOT_FOUND"
    DATA_PROCESSING_ERROR = "DATA_PROCESSING_ERROR"
    FILE_IO_ERROR = "FILE_IO_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    UNKNOWN_ERROR = "UNKNOWN_ERROR"


@dataclass
class ProcessingError:
    """Structured error information"""
    code: ErrorCode
    message: str
    details: Optional[Dict[str, Any]] = None
    sheet_name: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        result = {
            'code': self.code.value,
            'message': self.message
        }
        
        if self.details:
            result['details'] = self.details
        if self.sheet_name:
            result['sheet_name'] = self.sheet_name
            
        return result


@dataclass 
class SheetResult:
    """Result for individual sheet processing"""
    sheet_name: str
    status: ProcessingStatus
    rows_processed: int = 0
    columns_processed: int = 0
    error: Optional[ProcessingError] = None
    processing_time: float = 0.0
    
    @property
    def success(self) -> bool:
        """Check if processing was successful"""
        return self.status == ProcessingStatus.SUCCESS
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        result = {
            'sheet_name': self.sheet_name,
            'status': self.status.value,
            'rows_processed': self.rows_processed,
            'columns_processed': self.columns_processed,
            'processing_time': self.processing_time,
            'success': self.success
        }
        
        if self.error:
            result['error'] = self.error.to_dict()
            
        return result


@dataclass
class InvoiceResult:
    """Complete invoice generation result"""
    status: ProcessingStatus
    output_path: Optional[Path] = None
    processing_time: float = 0.0
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    
    # Sheet-level results
    sheet_results: List[SheetResult] = field(default_factory=list)
    
    # Overall metrics
    total_rows_processed: int = 0
    total_sheets_processed: int = 0
    
    # Errors and warnings
    error: Optional[ProcessingError] = None
    warnings: List[str] = field(default_factory=list)
    
    # Metadata
    template_used: Optional[str] = None
    config_used: Optional[str] = None
    input_file: Optional[str] = None
    
    def __post_init__(self):
        """Calculate derived fields"""
        if self.start_time and self.end_time:
            self.processing_time = self.end_time - self.start_time
    
    @property
    def success(self) -> bool:
        """Check if overall processing was successful"""
        return self.status == ProcessingStatus.SUCCESS
    
    def add_sheet_result(self, sheet_result: SheetResult):
        """Add a sheet result"""
        self.sheet_results.append(sheet_result)
        self.total_rows_processed += sheet_result.rows_processed
        
        if sheet_result.success:
            self.total_sheets_processed += 1
    
    def add_warning(self, message: str):
        """Add a warning message"""
        self.warnings.append(message)
    
    def set_error(self, error: ProcessingError):
        """Set the main error"""
        self.error = error
        self.status = ProcessingStatus.FAILED
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        result = {
            'success': self.success,
            'status': self.status.value,
            'processing_time': self.processing_time,
            'total_rows_processed': self.total_rows_processed,
            'total_sheets_processed': self.total_sheets_processed,
            'warnings': self.warnings
        }
        
        if self.output_path:
            result['output_path'] = str(self.output_path)
        
        if self.error:
            result['error'] = self.error.to_dict()
        
        if self.template_used:
            result['template_used'] = self.template_used
            
        if self.config_used:
            result['config_used'] = self.config_used
            
        if self.input_file:
            result['input_file'] = self.input_file
        
        # Add sheet results
        result['sheet_results'] = [sr.to_dict() for sr in self.sheet_results]
        
        # Add timing info
        if self.start_time:
            result['start_time'] = self.start_time
        if self.end_time:
            result['end_time'] = self.end_time
        
        return result


class ResultBuilder:
    """Builder for creating InvoiceResult objects"""
    
    def __init__(self):
        self.result = InvoiceResult(status=ProcessingStatus.SUCCESS)
        self.result.start_time = time.time()
    
    def set_input_file(self, input_file: str | Path) -> 'ResultBuilder':
        """Set input file"""
        self.result.input_file = str(input_file)
        return self
    
    def set_output_path(self, output_path: str | Path) -> 'ResultBuilder':
        """Set output path"""
        self.result.output_path = Path(output_path)
        return self
    
    def set_template(self, template_name: str) -> 'ResultBuilder':
        """Set template used"""
        self.result.template_used = template_name
        return self
    
    def set_config(self, config_name: str) -> 'ResultBuilder':
        """Set config used"""
        self.result.config_used = config_name
        return self
    
    def add_sheet_result(self, sheet_result: SheetResult) -> 'ResultBuilder':
        """Add sheet processing result"""
        self.result.add_sheet_result(sheet_result)
        return self
    
    def add_warning(self, message: str) -> 'ResultBuilder':
        """Add warning message"""
        self.result.add_warning(message)
        return self
    
    def set_error(self, error: ProcessingError) -> 'ResultBuilder':
        """Set error and mark as failed"""
        self.result.set_error(error)
        return self
    
    def build(self) -> InvoiceResult:
        """Build final result"""
        self.result.end_time = time.time()
        
        # Determine final status
        if not self.result.error:
            if any(not sr.success for sr in self.result.sheet_results):
                self.result.status = ProcessingStatus.PARTIAL
            else:
                self.result.status = ProcessingStatus.SUCCESS
        
        return self.result


# Helper functions for creating common errors

def create_template_not_found_error(template_name: str) -> ProcessingError:
    """Create template not found error"""
    return ProcessingError(
        code=ErrorCode.TEMPLATE_NOT_FOUND,
        message=f"Template not found: {template_name}",
        details={'template_name': template_name}
    )


def create_config_not_found_error(config_name: str) -> ProcessingError:
    """Create config not found error"""
    return ProcessingError(
        code=ErrorCode.CONFIG_NOT_FOUND,
        message=f"Configuration not found: {config_name}",
        details={'config_name': config_name}
    )


def create_validation_error(message: str, details: Dict[str, Any] = None) -> ProcessingError:
    """Create validation error"""
    return ProcessingError(
        code=ErrorCode.VALIDATION_ERROR,
        message=message,
        details=details
    )


def create_processing_error(message: str, sheet_name: str = None) -> ProcessingError:
    """Create data processing error"""
    return ProcessingError(
        code=ErrorCode.DATA_PROCESSING_ERROR,
        message=message,
        sheet_name=sheet_name
    )