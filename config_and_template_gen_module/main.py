#!/usr/bin/env python3
"""
Main orchestrator for the Automated Invoice Config Generator.

This script automates the two-step process of generating a configuration file
from an Excel invoice file.

1.  **Analyze Excel File**: It first calls the `analyze_excel.py` script to
    analyze the structure, fonts, and data layout of the input Excel file.
    This step produces a JSON file containing the analysis data.

2.  **Generate Configuration**: It then uses the generated analysis JSON file
    as input for the `generate_config_ascii.py` script. This second step
    takes the analysis data and a template configuration file to produce the
    final, ready-to-use invoice configuration file.

This orchestrator simplifies the end-to-end process into a single command,
handling the intermediate data flow and providing a unified command-line
interface.

Example Usage:
  - Generate a configuration from an Excel file with default settings:
    python main.py path/to/your/invoice.xlsx

  - Specify an output file for the final configuration:
    python main.py path/to/your/invoice.xlsx -o path/to/final_config.json

  - Use a custom template for configuration generation:
    python main.py path/to/your/invoice.xlsx -t path/to/custom_template.json

  - Keep the intermediate analysis file:
    python main.py path/to/your/invoice.xlsx --keep-intermediate

  - See detailed output from both scripts:
    python main.py path/to/your/invoice.xlsx -v
"""

import argparse
import subprocess
import sys
import os
import tempfile
import json
from pathlib import Path

# Define the base directory of the project
BASE_DIR = Path(__file__).parent.resolve()

# Define paths to the scripts
ANALYZE_SCRIPT_PATH = BASE_DIR / "config_data_extractor" / "analyze_excel.py"
GENERATE_SCRIPT_PATH = BASE_DIR / "generate_config" / "generate_config_ascii.py"

# Import the XLSX generator
try:
    from xlsx_generator import XLSXGenerator
    XLSX_GENERATOR_AVAILABLE = True
except ImportError:
    XLSX_GENERATOR_AVAILABLE = False


def extract_and_log_headers(analysis_file_path: str, output_base_name: str, interactive: bool = False) -> str:
    """
    Extract headers from the analysis JSON file and create a header log file.
    
    Args:
        analysis_file_path: Path to the analysis JSON file
        output_base_name: Base name for the output files
        interactive: If True, prompt user to add missing mappings interactively
        
    Returns:
        Path to the created header log file
    """
    try:
        # Load the analysis data
        with open(analysis_file_path, 'r', encoding='utf-8') as f:
            analysis_data = json.load(f)
        
        # Load current mapping configuration
        mapping_config_path = BASE_DIR / "mapping_config.json"
        current_mappings = {}
        if mapping_config_path.exists():
            try:
                with open(mapping_config_path, 'r', encoding='utf-8') as f:
                    mapping_data = json.load(f)
                    current_mappings = mapping_data.get('header_text_mappings', {}).get('mappings', {})
            except Exception as e:
                print(f"[ORCHESTRATOR] Warning: Could not load mapping config: {e}")
        
        # Create header log file path
        header_log_path = f"{output_base_name}_headers_found.txt"
        
        # Extract and log headers
        with open(header_log_path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("HEADERS FOUND IN EXCEL FILE\n")
            f.write("=" * 80 + "\n")
            f.write(f"Excel File: {analysis_data.get('file_path', 'Unknown')}\n")
            f.write(f"Analysis Time: {analysis_data.get('timestamp', 'Unknown')}\n")
            f.write("=" * 80 + "\n\n")
            
            all_found_headers = []
            missing_headers = []
            
            for sheet in analysis_data.get('sheets', []):
                sheet_name = sheet.get('sheet_name', 'Unknown')
                f.write(f"SHEET: {sheet_name}\n")
                f.write("-" * 40 + "\n")
                f.write(f"Start Row: {sheet.get('start_row', 'Unknown')}\n")
                f.write(f"Header Font: {sheet.get('header_font', {}).get('name', 'Unknown')} {sheet.get('header_font', {}).get('size', 'Unknown')}\n")
                f.write(f"Data Font: {sheet.get('data_font', {}).get('name', 'Unknown')} {sheet.get('data_font', {}).get('size', 'Unknown')}\n")
                f.write("\nHEADERS FOUND:\n")
                
                headers = sheet.get('header_positions', [])
                if headers:
                    for i, header in enumerate(headers, 1):
                        keyword = header.get('keyword', 'Unknown')
                        row = header.get('row', 'Unknown')
                        column = header.get('column', 'Unknown')
                        
                        # Check if this header is in current mappings
                        is_mapped = keyword in current_mappings
                        
                        # If not found, try with normalized newlines
                        if not is_mapped:
                            # Try with escaped newlines (as stored in JSON)
                            normalized_keyword = keyword.replace('\n', '\\n')
                            is_mapped = normalized_keyword in current_mappings
                            if is_mapped:
                                mapped_to = f" → {current_mappings.get(normalized_keyword, 'Unknown')}"
                        
                        mapping_status = "✅ MAPPED" if is_mapped else "❌ MISSING"
                        mapped_to = f" → {current_mappings.get(keyword, 'Unknown')}" if is_mapped and keyword in current_mappings else mapped_to if is_mapped else ""
                        
                        f.write(f"  {i:2d}. '{keyword}' (Row: {row}, Col: {column}) {mapping_status}{mapped_to}\n")
                        
                        all_found_headers.append(keyword)
                        if not is_mapped:
                            missing_headers.append(keyword)
                else:
                    f.write("  No headers found in this sheet.\n")
                
                f.write("\n" + "=" * 80 + "\n\n")
            
            # Add missing headers summary
            if missing_headers:
                f.write("MISSING HEADERS SUMMARY\n")
                f.write("=" * 80 + "\n")
                f.write(f"Found {len(missing_headers)} headers that are not in mapping_config.json:\n\n")
                
                for i, header in enumerate(missing_headers, 1):
                    f.write(f"  {i:2d}. '{header}'\n")
                
                f.write("\n" + "=" * 80 + "\n\n")
            
            # Add mapping suggestions section
            f.write("MAPPING SUGGESTIONS\n")
            f.write("=" * 80 + "\n")
            f.write("To add missing headers to mapping_config.json, use:\n")
            f.write("python generate_config/add_mapping.py --add-header \"HEADER_TEXT:column_id\"\n\n")
            
            f.write("Suggested column IDs based on header content:\n")
            f.write("- col_static: For mark/note columns\n")
            f.write("- col_po: For purchase order columns\n")
            f.write("- col_item: For item number columns\n")
            f.write("- col_desc: For description columns\n")
            f.write("- col_qty_sf: For quantity/square feet columns\n")
            f.write("- col_unit_price: For unit price columns\n")
            f.write("- col_amount: For amount/total columns\n")
            f.write("- col_net: For net weight columns\n")
            f.write("- col_gross: For gross weight columns\n")
            f.write("- col_cbm: For cubic meter columns\n")
            f.write("- col_pallet: For pallet number columns\n")
            f.write("- col_remarks: For remarks/notes columns\n\n")
            
            if missing_headers:
                f.write("Example commands for missing headers:\n")
                for header in missing_headers:
                    # Suggest appropriate column ID based on header content
                    suggested_id = "col_unknown"
                    header_lower = header.lower()
                    
                    if any(word in header_lower for word in ['mark', 'note', 'nº']):
                        suggested_id = "col_static"
                    elif any(word in header_lower for word in ['p.o', 'po']):
                        suggested_id = "col_po"
                    elif any(word in header_lower for word in ['item', 'no.']):
                        suggested_id = "col_item"
                    elif any(word in header_lower for word in ['description', 'desc']):
                        suggested_id = "col_desc"
                    elif any(word in header_lower for word in ['quantity', 'qty']):
                        suggested_id = "col_qty_sf"
                    elif any(word in header_lower for word in ['unit', 'price']):
                        suggested_id = "col_unit_price"
                    elif any(word in header_lower for word in ['amount', 'total', 'value']):
                        suggested_id = "col_amount"
                    elif any(word in header_lower for word in ['n.w', 'net']):
                        suggested_id = "col_net"
                    elif any(word in header_lower for word in ['g.w', 'gross']):
                        suggested_id = "col_gross"
                    elif any(word in header_lower for word in ['cbm']):
                        suggested_id = "col_cbm"
                    elif any(word in header_lower for word in ['pallet']):
                        suggested_id = "col_pallet"
                    elif any(word in header_lower for word in ['remarks', 'notes']):
                        suggested_id = "col_remarks"
                    
                    f.write(f"python generate_config/add_mapping.py --add-header \"{header}:{suggested_id}\"\n")
        
        print(f"[ORCHESTRATOR] Header log created: {header_log_path}")
        
        # Interactive mapping addition
        if interactive and missing_headers:
            print(f"\n[ORCHESTRATOR] Found {len(missing_headers)} missing headers!")
            print("Would you like to add them to the mapping configuration?")
            
            # Show available column IDs
            print("\nAvailable column IDs:")
            column_ids = [
                "col_static", "col_po", "col_item", "col_desc", "col_qty_sf", 
                "col_unit_price", "col_amount", "col_net", "col_gross", 
                "col_cbm", "col_pallet", "col_remarks", "col_qty_pcs", "col_no"
            ]
            for i, col_id in enumerate(column_ids, 1):
                print(f"  {i:2d}. {col_id}")
            
            print("\nInteractive mapping (press Enter to skip, 'q' to quit):")
            
            # Only process headers that are actually missing from mappings
            for header in missing_headers:
                # Check if header is still missing (with normalized newlines)
                is_still_missing = header not in current_mappings
                if not is_still_missing:
                    # Try with escaped newlines (as stored in JSON)
                    normalized_header = header.replace('\n', '\\n')
                    is_still_missing = normalized_header not in current_mappings
                
                if is_still_missing:  # Only process if still missing
                    # Suggest appropriate column ID based on header content
                    suggested_id = "col_unknown"
                    header_lower = header.lower()
                    
                    if any(word in header_lower for word in ['mark', 'note', 'nº']):
                        suggested_id = "col_static"
                    elif any(word in header_lower for word in ['p.o', 'po']):
                        suggested_id = "col_po"
                    elif any(word in header_lower for word in ['item', 'no.']):
                        suggested_id = "col_item"
                    elif any(word in header_lower for word in ['description', 'desc']):
                        suggested_id = "col_desc"
                    elif any(word in header_lower for word in ['quantity', 'qty']):
                        suggested_id = "col_qty_sf"
                    elif any(word in header_lower for word in ['unit', 'price']):
                        suggested_id = "col_unit_price"
                    elif any(word in header_lower for word in ['amount', 'total', 'value']):
                        suggested_id = "col_amount"
                    elif any(word in header_lower for word in ['n.w', 'net']):
                        suggested_id = "col_net"
                    elif any(word in header_lower for word in ['g.w', 'gross']):
                        suggested_id = "col_gross"
                    elif any(word in header_lower for word in ['cbm']):
                        suggested_id = "col_cbm"
                    elif any(word in header_lower for word in ['pallet']):
                        suggested_id = "col_pallet"
                    elif any(word in header_lower for word in ['remarks', 'notes']):
                        suggested_id = "col_remarks"
                    
                    while True:
                        user_input = input(f"Header: '{header}' → col_id [{suggested_id}]: ").strip()
                        
                        if user_input.lower() == 'q':
                            print("[ORCHESTRATOR] Interactive mapping cancelled.")
                            return header_log_path
                        elif user_input == '':
                            # Use suggested ID
                            col_id = suggested_id
                            break
                        elif user_input in column_ids:
                            col_id = user_input
                            break
                        else:
                            print(f"Invalid column ID. Please choose from: {', '.join(column_ids)}")
                            print(f"Or press Enter to use suggested: {suggested_id}")
                    
                    # Add the mapping
                    try:
                        # Directly update the mapping configuration instead of calling external script
                        if mapping_config_path.exists():
                            with open(mapping_config_path, 'r', encoding='utf-8') as f:
                                mapping_data = json.load(f)
                        else:
                            mapping_data = {
                                "sheet_name_mappings": {
                                    "comment": "Map quantity data sheet names to template config sheet names",
                                    "mappings": {}
                                },
                                "header_text_mappings": {
                                    "comment": "Map header texts from quantity data to column IDs in template",
                                    "mappings": {}
                                },
                                "fallback_strategies": {
                                    "comment": "Configuration for handling unrecognized headers and sheets",
                                    "case_insensitive_matching": True,
                                    "partial_matching_threshold": 0.7,
                                    "log_unrecognized_items": True,
                                    "create_suggestions": True
                                }
                            }
                        
                        # Add the new mapping
                        mapping_data["header_text_mappings"]["mappings"][header] = col_id
                        
                        # Save the updated configuration
                        with open(mapping_config_path, 'w', encoding='utf-8') as f:
                            json.dump(mapping_data, f, indent=2, ensure_ascii=False)
                        
                        print(f"✅ Added: '{header}' → {col_id}")
                        
                    except Exception as e:
                        print(f"❌ Error adding mapping: {e}")
            
            print("\n[ORCHESTRATOR] Interactive mapping completed!")
        
        if missing_headers and not interactive:
            print(f"[ORCHESTRATOR] Found {len(missing_headers)} missing headers - check the log for suggestions!")
        return header_log_path
        
    except Exception as e:
        print(f"[ORCHESTRATOR] Warning: Could not create header log: {e}")
        return ""


def run_command(command, verbose=False):
    """
    Executes a command in a subprocess and handles output.

    Args:
        command (list): The command and its arguments to execute.
        verbose (bool): If True, print the command being executed.

    Returns:
        bool: True for success, False for failure.
    """
    if verbose:
        print(f"\n[ORCHESTRATOR] Running command: {' '.join(command)}")

    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding='utf-8',
        errors='replace'
    )

    stdout, stderr = process.communicate()

    if process.returncode != 0:
        print(f"\n--- Error executing: {' '.join(command)} ---", file=sys.stderr)
        if stdout:
            print("--- STDOUT ---", file=sys.stderr)
            print(stdout, file=sys.stderr)
        if stderr:
            print("--- STDERR ---", file=sys.stderr)
            print(stderr, file=sys.stderr)
        print("-------------------------------------------------", file=sys.stderr)
        return False

    if verbose and stdout:
        print(stdout)

    return True


def main():
    """Main function to orchestrate the analysis and generation process."""
    parser = argparse.ArgumentParser(
        description='Automated Invoice Configuration Generator.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This tool streamlines the process of creating an invoice configuration by:
1. Analyzing an Excel file to extract data positions and styles.
2. Generating a final configuration file based on the analysis and a template.
3. Creating a header log file to help identify missing mappings.
"""
    )

    # --- Arguments for the whole process ---
    parser.add_argument(
        'excel_file',
        help='Path to the input Excel file to be processed.'
    )
    parser.add_argument(
        '-o', '--output',
        help='Path for the final generated configuration file. (Default: result/{excel_file_name}/{excel_file_name}_config.json)',
        metavar='FINAL_CONFIG_PATH'
    )
    parser.add_argument(
        '-t', '--template',
        default=BASE_DIR / "generate_config" / "sample_config.json",
        help='Path to the template configuration file for the generator. (Default: generate_config/sample_config.json)',
        metavar='TEMPLATE_PATH'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output to see detailed processing from all scripts.'
    )
    parser.add_argument(
        '--keep-intermediate',
        action='store_true',
        help='Keep the intermediate JSON file generated by the analysis step.'
    )
    parser.add_argument(
        '--interactive',
        action='store_true',
        help='Enable interactive mode to add missing header mappings.'
    )
    parser.add_argument(
        '--generate-xlsx',
        action='store_true',
        help='Generate processed XLSX file with text replacement and row removal.'
    )
    parser.add_argument(
        '--xlsx-output',
        help='Output path for the generated XLSX file (Default: result/{excel_file_name}/{excel_file_name}_processed.xlsx)'
    )

    args = parser.parse_args()

    # --- Create output directory ---
    excel_file_path = Path(args.excel_file)
    output_dir = BASE_DIR / "result" / excel_file_path.stem
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"[ORCHESTRATOR] Output will be saved in: {output_dir}")

    # --- Step 1: Analyze the Excel File ---
    print("[ORCHESTRATOR] Step 1: Analyzing Excel file...")

    # Use a temporary file for the intermediate analysis result
    temp_analysis_file = tempfile.NamedTemporaryFile(
        mode='w',
        delete=False,
        suffix=".json",
        prefix="analysis_",
        dir=str(output_dir)
    ).name

    analysis_output_path = temp_analysis_file

    analyze_command = [
        sys.executable,
        '-X', 'utf8',
        str(ANALYZE_SCRIPT_PATH),
        args.excel_file,
        '--json',
        '--quantity-mode',
        '-o',
        analysis_output_path
    ]

    if not run_command(analyze_command, args.verbose):
        print("\n[ORCHESTRATOR] Failed during the Excel analysis step. Aborting.", file=sys.stderr)
        # Clean up the temporary file if the script fails
        if not args.keep_intermediate and os.path.exists(analysis_output_path):
            os.remove(analysis_output_path)
        sys.exit(1)

    print(f"[ORCHESTRATOR] Analysis complete. Intermediate data saved to: {analysis_output_path}")

    # --- Step 1.5: Extract and log headers ---
    print("\n[ORCHESTRATOR] Step 1.5: Extracting and logging headers...")
    
    # Determine the output base name for header logging
    output_base_name = output_dir / excel_file_path.stem
    
    header_log_path = extract_and_log_headers(analysis_output_path, str(output_base_name), args.interactive)

    # --- Step 2: Generate the Configuration File ---
    print("\n[ORCHESTRATOR] Step 2: Generating final configuration file...")

    # Determine the final output path
    if args.output:
        final_output_path = output_dir / args.output
    else:
        final_output_path = output_dir / f"{excel_file_path.stem}_config.json"

    generate_command = [
        sys.executable,
        '-X', 'utf8',
        str(GENERATE_SCRIPT_PATH),
        analysis_output_path,
        '-t',
        str(args.template),
        '-o',
        str(final_output_path)
    ]

    if args.verbose:
        generate_command.append('-v')
        
    if args.interactive:
        generate_command.append('--interactive')

    if not run_command(generate_command, args.verbose):
        print("\n[ORCHESTRATOR] Failed during the configuration generation step. Aborting.", file=sys.stderr)
        if not args.keep_intermediate:
            os.remove(analysis_output_path)
        sys.exit(1)

    print("\n[ORCHESTRATOR] Process finished successfully!")
    print(f"✅ Final configuration file generated at: {final_output_path}")
    if header_log_path:
        print(f"📋 Header log file created at: {header_log_path}")
        print(f"💡 Check the header log to identify any missing mappings!")

    # --- Step 3: Generate XLSX file if requested ---
    if args.generate_xlsx and XLSX_GENERATOR_AVAILABLE:
        print("\n[ORCHESTRATOR] Step 3: Generating processed XLSX file...")
        try:
            generator = XLSXGenerator()
            
            if args.xlsx_output:
                xlsx_output_path = output_dir / args.xlsx_output
            else:
                xlsx_output_path = output_dir / f"{excel_file_path.stem}_processed.xlsx"

            xlsx_output = generator.generate_processed_xlsx(
                args.excel_file,
                str(xlsx_output_path),
                enable_text_replacement=True,
                enable_row_removal=True
            )
            print(f"✅ Processed XLSX file generated at: {xlsx_output}")
        except Exception as e:
            print(f"❌ Error generating XLSX file: {e}")
    elif args.generate_xlsx and not XLSX_GENERATOR_AVAILABLE:
        print("❌ XLSX generation requested but xlsx_generator module not available")

    # --- Step 4: Cleanup ---
    if not args.keep_intermediate and os.path.exists(analysis_output_path):
        try:
            os.remove(analysis_output_path)
            if args.verbose:
                print(f"[ORCHESTRATOR] Cleaned up intermediate file: {analysis_output_path}")
        except Exception as e:
            if args.verbose:
                print(f"[ORCHESTRATOR] Warning: Could not clean up intermediate file: {e}")


if __name__ == "__main__":
    # Check if the required script files exist
    if not ANALYZE_SCRIPT_PATH.exists():
        print(f"Error: Analysis script not found at {ANALYZE_SCRIPT_PATH}", file=sys.stderr)
        sys.exit(1)
    if not GENERATE_SCRIPT_PATH.exists():
        print(f"Error: Generation script not found at {GENERATE_SCRIPT_PATH}", file=sys.stderr)
        sys.exit(1)

    main()