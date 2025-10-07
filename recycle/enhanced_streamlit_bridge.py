#!/usr/bin/env python3
"""
Enhanced Streamlit Bridge for Config and Template Generation

This module provides Streamlit-compatible functions that show ALL unmapped headers
at once for user selection, rather than the CLI's one-by-one approach.
"""

import json
import subprocess
import sys
import os
import tempfile
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import streamlit as st

# Define the base directory of the project
BASE_DIR = Path(__file__).parent / "config_template_cli"

# Define paths to the scripts
ANALYZE_SCRIPT_PATH = BASE_DIR / "config_data_extractor" / "analyze_excel.py"
GENERATE_SCRIPT_PATH = BASE_DIR / "generate_config" / "generate_config_ascii.py"

# Available column IDs for mapping with descriptions
COLUMN_ID_OPTIONS = {
    "col_static": "Static/Mark & Note columns",
    "col_po": "Purchase Order columns", 
    "col_item": "Item Number columns",
    "col_desc": "Description columns",
    "col_qty_sf": "Quantity (Square Feet) columns",
    "col_qty_pcs": "Quantity (Pieces) columns", 
    "col_unit_price": "Unit Price columns",
    "col_amount": "Amount/Total columns",
    "col_net": "Net Weight columns",
    "col_gross": "Gross Weight columns",
    "col_cbm": "Cubic Meter columns",
    "col_pallet": "Pallet Number columns",
    "col_remarks": "Remarks/Notes columns",
    "col_no": "Number columns",
    "col_dc": "DC/Document Control columns",
    "col_unknown": "Unknown/Unmapped columns"
}

def run_excel_analysis(excel_file_path: str, output_path: str, verbose: bool = False) -> bool:
    """
    Run the Excel analysis command and return success status.
    """
    try:
        analyze_command = [
            sys.executable,
            '-X', 'utf8',
            str(ANALYZE_SCRIPT_PATH),
            excel_file_path,
            '--json',
            '--quantity-mode',
            '-o',
            output_path
        ]
        
        if verbose:
            st.write(f"🔍 Running analysis: {' '.join(analyze_command)}")
        
        process = subprocess.Popen(
            analyze_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            st.error(f"❌ Analysis failed: {stderr}")
            return False
            
        if verbose and stdout:
            st.text("Analysis output:")
            st.text(stdout)
            
        return True
        
    except Exception as e:
        st.error(f"❌ Error running analysis: {e}")
        return False

def get_all_unmapped_headers(analysis_file_path: str) -> Tuple[List[Dict], Dict[str, str], bool]:
    """
    Extract ALL unmapped headers from analysis at once for Streamlit display.
    
    Returns:
        Tuple containing:
        - List of unmapped header info dicts
        - Current mappings dictionary  
        - Success boolean
    """
    try:
        # Load analysis data
        with open(analysis_file_path, 'r', encoding='utf-8') as f:
            analysis_data = json.load(f)
        
        # Load current mapping config
        mapping_config_path = BASE_DIR / "mapping_config.json"
        current_mappings = {}
        
        if mapping_config_path.exists():
            try:
                with open(mapping_config_path, 'r', encoding='utf-8') as f:
                    mapping_data = json.load(f)
                    current_mappings = mapping_data.get('header_text_mappings', {}).get('mappings', {})
            except Exception as e:
                st.warning(f"Could not load mapping config: {e}")
        
        # Collect ALL headers and identify unmapped ones
        unmapped_headers = []
        
        for sheet in analysis_data.get('sheets', []):
            sheet_name = sheet.get('sheet_name', 'Unknown')
            headers = sheet.get('header_positions', [])
            
            for header in headers:
                keyword = header.get('keyword', 'Unknown')
                row = header.get('row', 'Unknown')
                column = header.get('column', 'Unknown')
                
                # Check if mapped (including normalized newlines)
                is_mapped = (keyword in current_mappings or 
                           keyword.replace('\n', '\\n') in current_mappings)
                
                if not is_mapped:
                    # Get AI suggestion for column ID
                    suggested_id = suggest_column_id_smart(keyword)
                    
                    # Create a unique key by including the index to avoid duplicates
                    unique_index = len(unmapped_headers)
                    
                    unmapped_headers.append({
                        'keyword': keyword,
                        'sheet_name': sheet_name,
                        'row': row,
                        'column': column,
                        'suggested_id': suggested_id,
                        'display_text': f"'{keyword}' (Sheet: {sheet_name}, Row: {row}, Col: {column})",
                        'unique_key': f"{sheet_name}_{row}_{column}_{keyword}_{unique_index}"  # For Streamlit widget keys with unique index
                    })
        
        return unmapped_headers, current_mappings, True
        
    except Exception as e:
        st.error(f"❌ Error extracting headers: {e}")
        return [], {}, False

def suggest_column_id_smart(header_text: str) -> str:
    """
    Smart column ID suggestion based on header content analysis.
    """
    header_lower = header_text.lower()
    
    # Enhanced pattern matching
    patterns = {
        'col_static': ['mark', 'note', 'nº', 'n°', 'mark & n', 'mark&n'],
        'col_po': ['p.o', 'po', 'purchase order', 'p.o.', 'p.o n'],
        'col_item': ['item', 'no.', 'number', 'hl item', 'item n'],
        'col_desc': ['description', 'desc', 'cargo description', 'cargo desc'],
        'col_qty_sf': ['quantity', 'qty', 'sqft', 'sf', 'square', '(sf)', 'quantity (sf)', 'quantity\n(sf)'],
        'col_qty_pcs': ['pieces', 'pcs', 'piece', 'quantity (pcs)', 'qty (pcs)'],
        'col_unit_price': ['unit price', 'price', 'fca', 'unit price (usd)', 'unit price\n(usd)'],
        'col_amount': ['amount', 'total', 'value', 'total amount', 'amount (usd)'],
        'col_net': ['n.w', 'net', 'net weight', 'net wt'],
        'col_gross': ['g.w', 'gross', 'gross weight', 'gross wt'],
        'col_cbm': ['cbm', 'cubic', 'cubic meter'],
        'col_pallet': ['pallet', 'pallet no', 'pallet number'],
        'col_remarks': ['remarks', 'notes', 'comment', 'remark'],
        'col_no': ['no', 'number', '#', 'serial'],
        'col_dc': ['dc', 'document control', 'doc control', 'document', 'control']
    }
    
    # Find best match
    for col_id, keywords in patterns.items():
        if any(keyword in header_lower for keyword in keywords):
            return col_id
    
    return 'col_unknown'

def save_header_mappings(new_mappings: Dict[str, str]) -> bool:
    """
    Save new header mappings to configuration file.
    """
    try:
        mapping_config_path = BASE_DIR / "mapping_config.json"
        
        # Load or create mapping config
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
        
        # Update mappings
        mapping_data["header_text_mappings"]["mappings"].update(new_mappings)
        
        # Save updated config
        with open(mapping_config_path, 'w', encoding='utf-8') as f:
            json.dump(mapping_data, f, indent=2, ensure_ascii=False)
        
        return True
        
    except Exception as e:
        st.error(f"❌ Error saving mappings: {e}")
        return False

def generate_config_file(analysis_file_path: str, output_path: str, template_path: Optional[str] = None) -> bool:
    """
    Generate configuration JSON file.
    """
    try:
        if template_path is None:
            template_path = str(BASE_DIR / "generate_config" / "sample_config.json")
        
        # Verify input files exist
        if not Path(analysis_file_path).exists():
            st.error(f"❌ Analysis file not found: {analysis_file_path}")
            return False
            
        if not Path(template_path).exists():
            st.error(f"❌ Template file not found: {template_path}")
            return False
        
        generate_command = [
            sys.executable,
            '-X', 'utf8',
            str(GENERATE_SCRIPT_PATH),
            analysis_file_path,
            '-t',
            template_path,
            '-o',
            output_path
        ]
        
        st.write(f"🔧 Running: {' '.join(generate_command)}")
        
        process = subprocess.Popen(
            generate_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            st.error(f"❌ Config generation failed with return code: {process.returncode}")
            st.error(f"STDERR: {stderr}")
            if stdout:
                st.error(f"STDOUT: {stdout}")
            return False
        
        # Verify output file was created
        if not Path(output_path).exists():
            st.error("❌ Config file was not created")
            return False
            
        st.success("✅ Config generation completed successfully")
        if stdout:
            st.text(f"Output: {stdout}")
            
        return True
        
    except Exception as e:
        st.error(f"❌ Error generating config: {e}")
        import traceback
        st.error(f"Full error: {traceback.format_exc()}")
        return False

def generate_config_and_xlsx_using_cli(excel_file_path: str, config_output_path: str, xlsx_output_path: str, verbose: bool = False) -> Tuple[bool, bool]:
    """
    Generate both config JSON and XLSX template using the main.py CLI.
    This is the most reliable approach since the CLI is already proven to work.
    
    Returns:
        Tuple of (config_success, xlsx_success)
    """
    try:
        # Verify input file exists
        if not Path(excel_file_path).exists():
            st.error(f"❌ Input Excel file not found: {excel_file_path}")
            return False, False
        
        # Create output directories if needed
        Path(config_output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(xlsx_output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Path to the main.py CLI
        main_cli_path = BASE_DIR / "main.py"
        
        if not main_cli_path.exists():
            st.error(f"❌ Main CLI not found: {main_cli_path}")
            return False, False
        
        # Build the CLI command - generate both config and XLSX
        cli_command = [
            sys.executable,
            '-X', 'utf8',
            str(main_cli_path),
            excel_file_path,
            '-o', config_output_path,
            '--generate-xlsx',
            '--xlsx-output', xlsx_output_path,
            '--keep-intermediate'  # Keep analysis file for debugging
        ]
        
        if verbose:
            cli_command.append('-v')
        
        st.write(f"🔧 Running CLI command: {' '.join(cli_command)}")
        
        # Execute the CLI command
        process = subprocess.Popen(
            cli_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='replace',
            cwd=str(BASE_DIR)  # Run from the config module directory
        )
        
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            st.error(f"❌ CLI generation failed with return code: {process.returncode}")
            st.error(f"STDERR: {stderr}")
            if stdout:
                st.error(f"STDOUT: {stdout}")
            return False, False
        
        # Check results
        config_success = Path(config_output_path).exists()
        xlsx_success = Path(xlsx_output_path).exists()
        
        if config_success:
            config_size = Path(config_output_path).stat().st_size
            st.success(f"✅ Config JSON generated successfully ({config_size} bytes)")
        else:
            st.error("❌ Config JSON file was not created")
        
        if xlsx_success:
            xlsx_size = Path(xlsx_output_path).stat().st_size
            st.success(f"✅ XLSX template generated successfully ({xlsx_size} bytes)")
        else:
            st.error("❌ XLSX template file was not created")
        
        if verbose and stdout:
            st.text("CLI Output:")
            st.text(stdout)
        
        return config_success, xlsx_success
        
    except Exception as e:
        st.error(f"❌ Error running CLI for generation: {e}")
        import traceback
        st.error(f"Full traceback: {traceback.format_exc()}")
        return False, False
    """
    Generate XLSX template using the existing main.py CLI that works perfectly.
    This uses the --generate-xlsx flag to create the processed template.
    """
    try:
        # Verify input file exists
        if not Path(excel_file_path).exists():
            st.error(f"❌ Input Excel file not found: {excel_file_path}")
            return False
        
        # Create output directory if needed
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Path to the main.py CLI
        main_cli_path = BASE_DIR / "main.py"
        
        if not main_cli_path.exists():
            st.error(f"❌ Main CLI not found: {main_cli_path}")
            return False
        
        # Build the CLI command to generate XLSX
        cli_command = [
            sys.executable,
            '-X', 'utf8',
            str(main_cli_path),
            excel_file_path,
            '--generate-xlsx',
            '--xlsx-output', output_path,
            '--keep-intermediate'  # Keep analysis file for debugging
        ]
        
        if verbose:
            cli_command.append('-v')
        
        st.write(f"🔧 Running CLI command: {' '.join(cli_command)}")
        
        # Execute the CLI command
        process = subprocess.Popen(
            cli_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='replace',
            cwd=str(BASE_DIR)  # Run from the config module directory
        )
        
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            st.error(f"❌ CLI XLSX generation failed with return code: {process.returncode}")
            st.error(f"STDERR: {stderr}")
            if stdout:
                st.error(f"STDOUT: {stdout}")
            return False
        
        # Check if output file was created
        if Path(output_path).exists():
            file_size = Path(output_path).stat().st_size
            st.success(f"✅ XLSX template generated successfully ({file_size} bytes)")
            if verbose and stdout:
                st.text("CLI Output:")
                st.text(stdout)
            return True
        else:
            st.error("❌ XLSX file was not created by CLI")
            if stdout:
                st.text("CLI Output:")
                st.text(stdout)
            return False
        
    except Exception as e:
        st.error(f"❌ Error running CLI for XLSX generation: {e}")
        import traceback
        st.error(f"Full traceback: {traceback.format_exc()}")
        return False
        st.error(f"❌ Error generating XLSX template: {e}")
        return False

def display_header_mapping_interface(unmapped_headers: List[Dict]) -> Dict[str, str]:
    """
    Display Streamlit interface for mapping ALL headers at once.
    
    Returns:
        Dict of header -> column_id mappings selected by user
    """
    st.subheader("🎯 Map Headers to Column Types")
    st.write(f"Found **{len(unmapped_headers)}** headers that need mapping. Please select the appropriate column type for each:")
    
    # Create columns for better layout
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.write("**Headers Found:**")
    with col2:
        st.write("**Column Type:**")
    
    # Dictionary to store user selections
    user_mappings = {}
    
    # Display all headers with dropdowns
    for i, header_info in enumerate(unmapped_headers):
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Display header info
            st.write(f"**{i+1}.** {header_info['display_text']}")
            if header_info['keyword'] != header_info['keyword'].strip():
                st.caption("⚠️ Contains whitespace/newlines")
        
        with col2:
            # Dropdown for column selection
            column_options = list(COLUMN_ID_OPTIONS.keys())
            column_labels = [f"{key} - {desc}" for key, desc in COLUMN_ID_OPTIONS.items()]
            
            # Find suggested option index
            suggested_idx = 0
            if header_info['suggested_id'] in column_options:
                suggested_idx = column_options.index(header_info['suggested_id'])
            
            selected_label = st.selectbox(
                "Column Type",
                column_labels,
                index=suggested_idx,
                key=f"mapping_{header_info['unique_key']}",
                label_visibility="collapsed"
            )
            
            # Extract selected column ID
            selected_column_id = selected_label.split(' - ')[0]
            user_mappings[header_info['keyword']] = selected_column_id
        
        # Add separator
        st.divider()
    
    return user_mappings

def streamlit_show_all_headers_interface(excel_file_path: str, company_name: str) -> Dict:
    """
    Main Streamlit interface that shows ALL unmapped headers at once.
    
    Returns status and file paths for next steps.
    """
    result = {
        'status': 'pending',
        'message': '',
        'analysis_file': '',
        'unmapped_headers': [],
        'mappings_needed': False
    }
    
    try:
        # Create temp directory for analysis
        temp_dir = Path(tempfile.mkdtemp(prefix=f"streamlit_config_{company_name}_"))
        analysis_file = temp_dir / f"{company_name}_analysis.json"
        
        # Step 1: Run analysis
        with st.spinner("🔍 Analyzing Excel file structure..."):
            if not run_excel_analysis(excel_file_path, str(analysis_file)):
                result['status'] = 'error'
                result['message'] = 'Failed to analyze Excel file'
                return result
        
        result['analysis_file'] = str(analysis_file)
        
        # Step 2: Get ALL unmapped headers at once
        with st.spinner("🎯 Extracting headers for mapping..."):
            unmapped_headers, current_mappings, success = get_all_unmapped_headers(str(analysis_file))
            
            if not success:
                result['status'] = 'error'
                result['message'] = 'Failed to extract headers'
                return result
        
        result['unmapped_headers'] = unmapped_headers
        
        if unmapped_headers:
            result['mappings_needed'] = True
            result['status'] = 'needs_mapping'
            result['message'] = f'Found {len(unmapped_headers)} headers that need mapping'
        else:
            result['status'] = 'ready'
            result['message'] = 'All headers are already mapped - ready to generate files!'
        
        return result
        
    except Exception as e:
        result['status'] = 'error'
        result['message'] = f'Error in analysis: {e}'
        return result
