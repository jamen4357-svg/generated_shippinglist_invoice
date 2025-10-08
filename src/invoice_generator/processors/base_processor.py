#!/usr/bin/env python3
"""
Invoice Generator Processors - Base Processor
Abstract base class for all processors
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseProcessor(ABC):
    """Base class for all processors"""
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
    
    @abstractmethod
    def process(self, *args, **kwargs) -> Any:
        """Process the data - to be implemented by subclasses"""
        pass
    
    def log(self, message: str, level: str = "INFO") -> None:
        """Log message if verbose mode is enabled"""
        if self.verbose:
            print(f"[{level}] {self.__class__.__name__}: {message}")
    
    def validate_input(self, data: Any, expected_type: type = dict) -> bool:
        """Validate input data"""
        if data is None:
            self.log("Input data is None", "ERROR")
            return False
        
        if not isinstance(data, expected_type):
            self.log(f"Expected {expected_type.__name__}, got {type(data).__name__}", "ERROR")
            return False
        
        return True