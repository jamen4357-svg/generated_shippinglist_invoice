"""
Example demonstrating the enhanced footer config functionality.

ALL footer fields now support both column IDs and raw indices:
- start_column_id (merge rules)
- total_text_column_id (footer text placement)
- pallet_count_column_id (pallet count placement)

IMPORTANT: Raw indices use 0-based indexing like programming languages!
- 0 = Column A, 1 = Column B, 2 = Column C, etc.
"""

# Example footer configuration showing different ways to use enhanced fields
footer_config_examples = {
    "column_id_format": {
        "total_text": "TOTAL:",
        "total_text_column_id": "col_po",  # Column ID string (traditional)
        "pallet_count_column_id": "col_item",  # Column ID string
        "merge_rules": [
            {
                "start_column_id": "col_po",  # Column ID string (traditional)
                "colspan": 3
            }
        ]
    },
    
    "raw_index_integer": {
        "total_text": "TOTAL:",
        "total_text_column_id": 1,  # Raw column index (0-based) -> Column B
        "pallet_count_column_id": 2,  # Raw column index (0-based) -> Column C
        "merge_rules": [
            {
                "start_column_id": 1,  # Raw column index (0-based) -> Column B
                "colspan": 3
            }
        ]
    },
    
    "raw_index_string": {
        "total_text": "TOTAL:",
        "total_text_column_id": "1",  # Raw column index as string (0-based) -> Column B
        "pallet_count_column_id": "2",  # Raw column index as string (0-based) -> Column C
        "merge_rules": [
            {
                "start_column_id": "1",  # Raw column index as string (0-based) -> Column B
                "colspan": 3
            }
        ]
    },
    
    "mixed_formats": {
        "total_text": "TOTAL:",
        "total_text_column_id": "col_po",  # Column ID
        "pallet_count_column_id": 2,  # Raw index (0-based) -> Column C
        "merge_rules": [
            {
                "start_column_id": "col_po",  # Column ID
                "colspan": 2
            },
            {
                "start_column_id": 3,  # Raw index (0-based) -> Column D
                "colspan": 3
            },
            {
                "start_column_id": "5",  # Raw index (0-based string) -> Column F
                "colspan": 2
            }
        ]
    }
}

def explain_merge_logic():
    """
    Explains how the enhanced footer logic works.
    """
    print("Enhanced Footer Configuration System:")
    print("===================================")
    print()
    print("🚨 CRITICAL: Raw indices use 0-based indexing like programming languages!")
    print("  0 = Column A, 1 = Column B, 2 = Column C, etc.")
    print()
    print("ALL footer fields now support multiple value types:")
    print("- total_text_column_id (where to place 'TOTAL:' text)")
    print("- pallet_count_column_id (where to place pallet count)")
    print("- start_column_id (merge rules for cell merging)")
    print()
    print("FORMAT OPTIONS:")
    print('   "total_text_column_id": "col_po"      # Column ID string')
    print('   "total_text_column_id": 1             # Raw column index (0-based) -> Column B')
    print('   "total_text_column_id": "1"           # Raw column index as string (0-based) -> Column B')
    print()
    print("DETECTION LOGIC:")
    print("- If isinstance(value, int) -> use as 0-based index, convert to Excel 1-based")
    print("- If isinstance(value, str):")
    print("  - Try int(value) -> use as 0-based index, convert to Excel 1-based")
    print("  - Except ValueError -> use as column ID for lookup")
    print()
    print("INDEXING CONVERSION:")
    print("- Your 0-based index is automatically converted to Excel's 1-based system")
    print("- total_text_column_id: 0 → Excel Column A (index 1)")
    print("- pallet_count_column_id: 1 → Excel Column B (index 2)")
    print("- start_column_id: 2 → Excel Column C (index 3)")
    print()
    print("BENEFITS:")
    print("- Consistent behavior across ALL footer fields")
    print("- Single field supports all formats")
    print("- Backward compatibility maintained")
    print("- Familiar 0-based indexing for developers")
    print("- Type-based automatic detection")

if __name__ == "__main__":
    explain_merge_logic()
    print("\nExample configurations:")
    print("======================")
    for name, config in footer_config_examples.items():
        print(f"\n{name.upper()}:")
        for rule in config["merge_rules"]:
            print(f"  {rule}")
