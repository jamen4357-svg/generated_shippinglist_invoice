#!/usr/bin/env python3
"""
Interactive Header Mapping Tool

This tool provides an interactive mode for mapping unknown headers to column IDs
with user validation. It uses the fuzzy matching and pattern recognition fallbacks
that were removed from the automatic config generation for safety.

Usage:
    python interactive_mapping.py analysis_file.json
    python interactive_mapping.py analysis_file.json --auto-suggest
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Add the config_generator module to path
sys.path.insert(0, str(Path(__file__).parent))

from config_generator.header_text_updater import HeaderTextUpdater
from config_generator.models import HeaderPosition


class InteractiveMappingTool:
    """Interactive tool for mapping headers with user validation."""
    
    def __init__(self):
        self.header_updater = HeaderTextUpdater()
        self.mapping_config_path = Path(__file__).parent / "mapping_config.json"
        self.pending_mappings = {}
        
    def run_interactive_mapping(self, analysis_file: str, auto_suggest: bool = False) -> None:
        """
        Run interactive mapping session for unknown headers.
        
        Args:
            analysis_file: Path to quantity analysis JSON file
            auto_suggest: If True, automatically suggest mappings using fallbacks
        """
        try:
            # Load analysis data
            with open(analysis_file, 'r', encoding='utf-8') as f:
                analysis_data = json.load(f)
            
            print("=" * 80)
            print("INTERACTIVE HEADER MAPPING TOOL")
            print("=" * 80)
            print(f"Analysis file: {analysis_file}")
            print(f"Auto-suggest mode: {'ON' if auto_suggest else 'OFF'}")
            print()
            
            # Find all unmapped headers
            unmapped_headers = self._find_unmapped_headers(analysis_data)
            
            if not unmapped_headers:
                print("✅ All headers are already mapped!")
                return
            
            print(f"Found {len(unmapped_headers)} unmapped headers:")
            print()
            
            # Process each unmapped header
            for i, (sheet_name, header_text) in enumerate(unmapped_headers, 1):
                print(f"\n[{i}/{len(unmapped_headers)}] Processing header from sheet '{sheet_name}':")
                print(f"Header text: '{header_text}'")
                print("-" * 40)
                
                if auto_suggest:
                    self._interactive_mapping_with_suggestions(header_text, sheet_name)
                else:
                    self._interactive_mapping_manual(header_text, sheet_name)
            
            # Save all pending mappings
            if self.pending_mappings:
                self._save_pending_mappings()
                print(f"\n✅ Added {len(self.pending_mappings)} new mappings to mapping_config.json")
            else:
                print(f"\n💭 No new mappings were added")
                
        except Exception as e:
            print(f"❌ Error during interactive mapping: {e}")
            sys.exit(1)
    
    def _find_unmapped_headers(self, analysis_data: Dict) -> List[tuple]:
        """Find all headers that don't have exact mappings."""
        unmapped = []
        
        for sheet in analysis_data.get('sheets', []):
            sheet_name = sheet.get('sheet_name', 'Unknown')
            
            for header_pos in sheet.get('header_positions', []):
                keyword = header_pos.get('keyword', '')
                if keyword:
                    # Check if this header has an exact mapping
                    column_id = self.header_updater.map_header_to_column_id(keyword, strict_mode=True)
                    if not column_id:
                        unmapped.append((sheet_name, keyword))
        
        return unmapped
    
    def _interactive_mapping_with_suggestions(self, header_text: str, sheet_name: str) -> None:
        """Interactive mapping with auto-suggestions using fallback mechanisms."""
        
        # Try to get suggestions using the fallback mechanisms
        suggested_id = self.header_updater.map_header_to_column_id(header_text, strict_mode=False)
        
        if suggested_id:
            print(f"💡 Suggested mapping: {suggested_id}")
            print(f"🤖 Based on fuzzy matching and pattern recognition")
            print()
            
            choice = input("Accept this suggestion? (y/n/m=manual/s=skip): ").lower().strip()
            
            if choice == 'y':
                self.pending_mappings[header_text] = suggested_id
                print(f"✅ Accepted: '{header_text}' → {suggested_id}")
                return
            elif choice == 'm':
                self._interactive_mapping_manual(header_text, sheet_name)
                return
            elif choice == 's':
                print("⏭️ Skipped")
                return
        
        print("❌ No automatic suggestions available")
        self._interactive_mapping_manual(header_text, sheet_name)
    
    def _interactive_mapping_manual(self, header_text: str, sheet_name: str) -> None:
        """Manual interactive mapping with column ID suggestions."""
        
        print("Available column IDs:")
        column_ids = [
            ("col_static", "Mark & note columns"),
            ("col_po", "Purchase order columns"),
            ("col_item", "Item number columns"),
            ("col_desc", "Description columns"),
            ("col_qty_sf", "Quantity/square feet columns"),
            ("col_qty_pcs", "Quantity/pieces columns"),
            ("col_unit_price", "Unit price columns"),
            ("col_amount", "Amount/total columns"),
            ("col_net", "Net weight columns"),
            ("col_gross", "Gross weight columns"),
            ("col_cbm", "Cubic meter columns"),
            ("col_pallet", "Pallet number columns"),
            ("col_remarks", "Remarks/notes columns"),
            ("col_no", "Sequential number columns"),
            ("skip", "Skip this header"),
        ]
        
        print()
        for i, (col_id, description) in enumerate(column_ids, 1):
            print(f"  {i:2d}. {col_id:15s} - {description}")
        
        print()
        
        while True:
            try:
                choice = input("Enter column ID number or type custom ID (or 'skip'): ").strip()
                
                if choice.lower() == 'skip':
                    print("⏭️ Skipped")
                    return
                
                # Try to parse as number
                try:
                    choice_num = int(choice)
                    if 1 <= choice_num <= len(column_ids):
                        selected_id = column_ids[choice_num - 1][0]
                        if selected_id == 'skip':
                            print("⏭️ Skipped")
                            return
                        
                        self.pending_mappings[header_text] = selected_id
                        print(f"✅ Mapped: '{header_text}' → {selected_id}")
                        return
                    else:
                        print(f"❌ Invalid number. Please enter 1-{len(column_ids)}")
                        continue
                except ValueError:
                    # Not a number, treat as custom column ID
                    if choice.startswith('col_') and len(choice) > 4:
                        confirm = input(f"Use custom column ID '{choice}'? (y/n): ").lower().strip()
                        if confirm == 'y':
                            self.pending_mappings[header_text] = choice
                            print(f"✅ Mapped: '{header_text}' → {choice}")
                            return
                    else:
                        print("❌ Invalid input. Enter a number, 'skip', or custom 'col_' ID")
                        continue
                        
            except KeyboardInterrupt:
                print(f"\n🛑 Interrupted by user")
                sys.exit(1)
    
    def _save_pending_mappings(self) -> None:
        """Save all pending mappings to mapping_config.json."""
        try:
            # Load existing config
            if self.mapping_config_path.exists():
                with open(self.mapping_config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            else:
                config = {
                    "header_text_mappings": {"mappings": {}},
                    "sheet_name_mappings": {"mappings": {}},
                    "fallback_strategies": {}
                }
            
            # Add new mappings
            existing_mappings = config.get('header_text_mappings', {}).get('mappings', {})
            existing_mappings.update(self.pending_mappings)
            
            # Update config
            if 'header_text_mappings' not in config:
                config['header_text_mappings'] = {}
            config['header_text_mappings']['mappings'] = existing_mappings
            
            # Save config
            with open(self.mapping_config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Saved mappings to {self.mapping_config_path}")
            
        except Exception as e:
            print(f"❌ Error saving mappings: {e}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Interactive tool for mapping unknown headers to column IDs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic interactive mapping
  python interactive_mapping.py analysis.json
  
  # With auto-suggestions using fallback mechanisms
  python interactive_mapping.py analysis.json --auto-suggest
        """
    )
    
    parser.add_argument(
        'analysis_file',
        help='Path to quantity analysis JSON file'
    )
    
    parser.add_argument(
        '--auto-suggest',
        action='store_true',
        help='Enable auto-suggestions using fuzzy matching and patterns'
    )
    
    args = parser.parse_args()
    
    # Validate input file
    if not Path(args.analysis_file).exists():
        print(f"❌ Analysis file not found: {args.analysis_file}")
        sys.exit(1)
    
    # Run interactive mapping
    tool = InteractiveMappingTool()
    tool.run_interactive_mapping(args.analysis_file, args.auto_suggest)


if __name__ == '__main__':
    main()
