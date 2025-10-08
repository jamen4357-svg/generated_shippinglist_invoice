# Invoice Generator - Clean Architecture Plan

## Current Structure Issues:
- generate_invoice.py: 1,435 lines - too big!
- Mixed CLI/API logic
- Complex table processing logic embedded
- Hard to test individual components

## Proposed New Structure:

```
src/
├── invoice_generator/
│   ├── __init__.py              # Main API entry points
│   ├── core/
│   │   ├── __init__.py
│   │   ├── engine.py            # Main invoice generation engine
│   │   ├── config.py            # Configuration management  
│   │   └── result.py            # Result/error handling
│   ├── processors/
│   │   ├── __init__.py
│   │   ├── base_processor.py    # Abstract base processor
│   │   ├── text_processor.py    # Text replacement logic
│   │   ├── table_processor.py   # Table data processing
│   │   └── aggregation_processor.py # Aggregation logic
│   ├── io/
│   │   ├── __init__.py
│   │   ├── data_loader.py       # JSON/PKL data loading
│   │   ├── template_manager.py  # Template file management
│   │   └── excel_writer.py      # Excel file operations
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── path_resolver.py     # Path resolution logic
│   │   ├── validators.py        # Input validation
│   │   └── helpers.py           # Common utilities
│   └── legacy/
│       └── generate_invoice_old.py  # Keep old version for reference
├── api/
│   ├── __init__.py
│   ├── main.py                  # FastAPI application
│   ├── routes/
│   │   ├── __init__.py
│   │   └── invoice_routes.py    # Invoice generation endpoints
│   └── models/
│       ├── __init__.py
│       ├── requests.py          # Request models
│       └── responses.py         # Response models
├── cli/
│   ├── __init__.py
│   └── main.py                  # CLI interface
└── tests/
    ├── unit/
    ├── integration/
    └── fixtures/
```

## Benefits:
1. **Single Responsibility**: Each module has one clear purpose
2. **Testable**: Easy to unit test individual components
3. **Maintainable**: Changes isolated to specific modules
4. **Flexible**: Can swap implementations easily
5. **Clean Dependencies**: Clear import hierarchy