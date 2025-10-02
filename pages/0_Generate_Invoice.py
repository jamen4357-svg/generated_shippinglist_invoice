import streamlit as st
import os
import sys
from pathlib import Path
import json
import datetime
import sqlite3
import tempfile
from zoneinfo import ZoneInfo
import time
import re
from auth_wrapper import setup_page_auth
from ui_utils.field_prefiller import render_field_prefiller

# Import our strategy system
from invoice_strategies import (
    STRATEGIES,
    apply_print_settings_to_files,
    create_download_zip,
)

# --- Enhanced Authentication Setup ---
user_info = setup_page_auth(
    page_title="Invoice Generation",
    page_name="Invoice Generation Suite",
    layout="wide"
)

st.title("Unified Invoice Generation Suite ⚙️📄")

# --- Project Path & Directory Configuration ---
try:
    PROJECT_ROOT = Path(__file__).resolve().parent.parent
    CREATE_JSON_DIR = PROJECT_ROOT / "create_json"
    INVOICE_GEN_DIR = PROJECT_ROOT / "invoice_gen"
    DATA_DIR = PROJECT_ROOT / "data"
    JSON_OUTPUT_DIR = DATA_DIR / "invoices_to_process"
    TEMP_UPLOAD_DIR = DATA_DIR / "temp_uploads"
    TEMPLATE_DIR = INVOICE_GEN_DIR / "TEMPLATE"
    CONFIG_DIR = INVOICE_GEN_DIR / "config"
    DATA_DIRECTORY = DATA_DIR / 'Invoice Record'
    DATABASE_FILE = DATA_DIRECTORY / 'master_invoice_data.db'
    TABLE_NAME = 'invoices'

    # Create necessary directories
    for dir_path in [JSON_OUTPUT_DIR, TEMP_UPLOAD_DIR, DATA_DIRECTORY, CONFIG_DIR]:
        dir_path.mkdir(parents=True, exist_ok=True)

except Exception as e:
    st.error(f"Error: Could not configure project paths. Details: {e}")
    st.exception(e)
    st.stop()

# --- Database Initialization ---
def initialize_database(db_file: Path):
    """Initialize the database with required tables"""
    try:
        with sqlite3.connect(db_file) as conn:
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT, inv_no TEXT, inv_date TEXT,
                inv_ref TEXT UNIQUE, po TEXT, item TEXT, description TEXT, pcs TEXT,
                sqft TEXT, pallet_count TEXT, unit TEXT, amount TEXT, net TEXT,
                gross TEXT, cbm TEXT, production_order_no TEXT, creating_date TEXT,
                status TEXT DEFAULT 'active'
            );
            """)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS invoice_containers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                inv_ref TEXT NOT NULL,
                container_description TEXT NOT NULL,
                FOREIGN KEY (inv_ref) REFERENCES invoices (inv_ref)
            );
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_invoices_lower_inv_ref ON invoices (LOWER(inv_ref));")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_invoices_lower_inv_no ON invoices (LOWER(inv_no));")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_inv_ref ON invoice_containers (inv_ref);")
            conn.commit()
        return True
    except sqlite3.Error as e:
        st.error(f"Database Initialization Failed: {e}")
        return False

DB_ENABLED = initialize_database(DATABASE_FILE)
if not DB_ENABLED:
    st.error("Database connection could not be established.")
    st.stop()

# --- Session State Initialization ---
if 'workflow_step' not in st.session_state:
    st.session_state.workflow_step = 'select_strategy'
if 'selected_strategy' not in st.session_state:
    st.session_state.selected_strategy = None
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None
if 'validation_complete' not in st.session_state:
    st.session_state.validation_complete = False
if 'json_path' not in st.session_state:
    st.session_state.json_path = None
if 'identifier' not in st.session_state:
    st.session_state.identifier = None
if 'overrides' not in st.session_state:
    st.session_state.overrides = {}
if 'generation_options' not in st.session_state:
    st.session_state.generation_options = []
if 'excel_validation_passed' not in st.session_state:
    st.session_state.excel_validation_passed = False
if 'excel_validation_warnings' not in st.session_state:
    st.session_state.excel_validation_warnings = []
if 'temp_file_path' not in st.session_state:
    st.session_state.temp_file_path = None
if 'uploaded_filename' not in st.session_state:
    st.session_state.uploaded_filename = None

def reset_workflow():
    """Reset the workflow to initial state"""
    # Cleanup temp files
    if 'temp_file_path' in st.session_state and st.session_state.temp_file_path and st.session_state.temp_file_path.exists():
        try:
            st.session_state.temp_file_path.unlink()
        except:
            pass  # Ignore cleanup errors

    st.session_state.workflow_step = 'select_strategy'
    st.session_state.selected_strategy = None
    st.session_state.uploaded_file = None
    st.session_state.temp_file_path = None
    st.session_state.uploaded_filename = None
    st.session_state.validation_complete = False
    st.session_state.excel_validation_passed = False
    st.session_state.excel_validation_warnings = []
    st.session_state.json_path = None
    st.session_state.identifier = None
    st.session_state.overrides = {}
    st.session_state.generation_options = []

def cleanup_old_files(directories: list, max_age_seconds: int = 3600):
    """Deletes files older than a specified age in a list of directories."""
    cutoff_time = time.time() - max_age_seconds
    for directory in directories:
        if not directory.exists(): continue
        try:
            for filepath in directory.iterdir():
                if filepath.is_file() and filepath.stat().st_mtime < cutoff_time:
                    try:
                        filepath.unlink()
                    except OSError:
                        pass # Ignore if file is locked
        except Exception:
            pass # Ignore directory-level errors

def get_suggested_inv_ref():
    """
    Efficiently suggests the next invoice reference number for the current year
    by querying the database for the maximum existing number.
    """
    # Use Cambodia timezone for current year
    cambodia_tz = ZoneInfo("Asia/Phnom_Penh")
    current_year = datetime.datetime.now(cambodia_tz).strftime('%Y')
    prefix = "INV"
    suggestion = f"{prefix}{current_year}-1"
    if not DB_ENABLED: return suggestion
    try:
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()
            query = f"""
                SELECT inv_ref FROM {TABLE_NAME}
                WHERE inv_ref LIKE ?
                ORDER BY CAST(SUBSTR(inv_ref, INSTR(inv_ref, '-') + 1) AS INTEGER) DESC
                LIMIT 1
            """
            pattern = f"_%{current_year}-%"
            cursor.execute(query, (pattern,))
            last_ref = cursor.fetchone()

            if not last_ref: return suggestion

            match = re.match(r"([a-zA-Z]+)(\d{4})-(\d+)", last_ref[0])
            if match:
                prefix, _, last_num = match.groups()
                return f"{prefix}{current_year}-{int(last_num) + 1}"
            return suggestion
    except sqlite3.Error as e:
        st.warning(f"DB error suggesting Invoice Ref: {e}")
        return suggestion

def check_existing_identifiers(inv_no: str = None, inv_ref: str = None) -> dict:
    """
    Checks for the existence of an invoice number and/or reference in a single,
    fast, indexed database query.
    """
    results = {}
    if not DB_ENABLED or (not inv_no and not inv_ref): return results
    try:
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()
            if inv_no:
                cursor.execute(f"SELECT 1 FROM {TABLE_NAME} WHERE LOWER(inv_no) = LOWER(?) LIMIT 1", (inv_no,))
                if cursor.fetchone(): results['inv_no'] = True
            if inv_ref:
                cursor.execute(f"SELECT 1 FROM {TABLE_NAME} WHERE LOWER(inv_ref) = LOWER(?) LIMIT 1", (inv_ref,))
                if cursor.fetchone(): results['inv_ref'] = True
    except sqlite3.Error as e:
        st.warning(f"DB error checking for existing values: {e}")
    return results

# --- Helper Functions for Rendering Steps ---
def render_upload_step(strategy):
    """Renders the file upload UI and handles the logic for that step."""
    st.subheader(f"2. Upload File for {strategy.name}")
    st.info(strategy.description)

    # File uploader
    file_key = f"upload_{strategy.name.lower().replace(' ', '_')}"
    uploaded_file = st.file_uploader(
        f"Choose an Excel file for {strategy.name}",
        type="xlsx",
        key=file_key
    )

    if uploaded_file:
        st.session_state.uploaded_file = uploaded_file

        # Process button
        if st.button("Validate & Process File", use_container_width=True, type="primary"):
            temp_file_path = None
            try:
                # Save uploaded file
                temp_file_path = TEMP_UPLOAD_DIR / uploaded_file.name
                with open(temp_file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                st.session_state.temp_file_path = temp_file_path
                st.session_state.uploaded_filename = uploaded_file.name # Store the filename
                st.session_state.workflow_step = 'validate_excel'
                st.rerun()

            except Exception as e:
                st.error(f"❌ File upload failed: {e}")
                st.exception(e)
                # Cleanup temp file only on error
                if temp_file_path and temp_file_path.exists():
                    temp_file_path.unlink()

    # Navigation
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Back to Selection", use_container_width=True):
            st.session_state.workflow_step = 'select_strategy'
            st.rerun()
    with col2:
        if st.button("🔄 Reset Workflow", use_container_width=True):
            reset_workflow()


def render_validate_excel_step(strategy):
    """Renders the Excel validation UI and handles the logic for that step."""
    temp_file_path = st.session_state.temp_file_path

    st.subheader(f"3. Validate Excel Data for {strategy.name}")

    # Run Excel validation
    is_valid, warnings = strategy.validate_excel_data(temp_file_path)

    st.session_state.excel_validation_passed = is_valid
    st.session_state.excel_validation_warnings = warnings

    # Display file name
    if st.session_state.uploaded_file:
        st.info(f"📄 **File:** {st.session_state.uploaded_file.name}")

    # Display validation results
    if is_valid:
        st.success("✅ Excel validation passed!")
    else:
        st.error("❌ Excel validation failed!")

    # Show warnings/details
    if warnings:
        with st.expander("📋 Validation Details", expanded=True):
            for warning in warnings:
                if "❌" in warning:
                    st.error(warning)
                elif "⚠️" in warning:
                    st.warning(warning)
                else:
                    st.info(warning)

    # Action buttons
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("⬅️ Back to Upload", use_container_width=True):
            # Cleanup temp file when going back
            if st.session_state.temp_file_path and st.session_state.temp_file_path.exists():
                try:
                    st.session_state.temp_file_path.unlink()
                except:
                    pass
            st.session_state.temp_file_path = None
            st.session_state.workflow_step = 'upload'
            st.rerun()

    with col2:
        if is_valid and st.button("⚠️ Continue Anyway", use_container_width=True, type="secondary"):
            st.session_state.workflow_step = 'process_file'
            st.rerun()

    with col3:
        if is_valid and st.button("✅ Process File", use_container_width=True, type="primary"):
            # For 2nd Layer Leather, collect inputs first
            if strategy.name == "2nd Layer Leather":
                st.session_state.workflow_step = 'collect_inputs'
            else:
                st.session_state.workflow_step = 'process_file'
            st.rerun()


def render_collect_inputs_step(strategy):
    """Renders the UI for collecting required inputs for certain strategies."""
    st.subheader(f"4. Enter Invoice Details for {strategy.name}")

    # Only show for 2nd Layer Leather
    if strategy.name == "2nd Layer Leather":
        ui_config = strategy.get_override_ui_config()

        # Collect required inputs
        inputs = {}

        col1, col2 = st.columns(2)

        with col1:
            # Invoice Reference
            suggested_inv_ref = get_suggested_inv_ref()
            render_field_prefiller(
                field_label="Invoice Reference",
                session_key="input_inv_ref",
                suggested_value=st.session_state.get('uploaded_filename', suggested_inv_ref),
                help_text="Click 'Use Filename' to use the uploaded file's name as the Invoice Reference."
            )
            inputs['inv_ref'] = st.session_state.get("input_inv_ref", "")


            # Unit Price
            inputs['unit_price'] = st.number_input(
                "Unit Price",
                min_value=0.0,
                value=0.61,
                step=0.01,
                key="input_unit_price"
            )

        with col2:
            # Invoice Date
            inputs['inv_date'] = st.date_input(
                "Invoice Date",
                value=datetime.date.today(),
                format="DD/MM/YYYY",
                key="input_inv_date"
            )

        # Store inputs in session state
        st.session_state.required_inputs = inputs

        # Process button
        if st.button("✅ Process with These Details", use_container_width=True, type="primary"):
            # Validate inputs
            if not inputs['inv_ref'].strip():
                st.error("❌ Invoice Reference is required")
            elif inputs['unit_price'] <= 0:
                st.error("❌ Unit Price must be greater than 0")
            else:
                # All inputs valid, proceed to processing
                st.session_state.workflow_step = 'process_file'
                st.rerun()

    else:
        # For other strategies, skip to processing
        st.session_state.workflow_step = 'process_file'
        st.rerun()

    # Navigation
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Back to Validation", use_container_width=True):
            st.session_state.workflow_step = 'validate_excel'
            st.rerun()


def render_process_file_step(strategy):
    """Handles the backend processing of the file (Excel to JSON)."""
    temp_file_path = st.session_state.temp_file_path

    st.subheader(f"5. Process File for {strategy.name}")

    # Process Excel to JSON
    with st.spinner("Processing Excel file..."):
        try:
            # For 2nd Layer Leather, use collected inputs
            if strategy.name == "2nd Layer Leather":
                required_inputs = st.session_state.get('required_inputs', {})
                inv_ref = required_inputs.get('inv_ref', get_suggested_inv_ref())
                inv_date = required_inputs.get('inv_date', datetime.date.today())
                unit_price = required_inputs.get('unit_price', 0.61)

                # Convert date to string format
                if hasattr(inv_date, 'strftime'):
                    inv_date_str = inv_date.strftime("%d/%m/%Y")
                else:
                    inv_date_str = str(inv_date)

                # Step 1: Process Excel to create initial JSON
                json_path, identifier = strategy.process_excel_to_json(
                    temp_file_path,
                    JSON_OUTPUT_DIR,
                    inv_ref=inv_ref,
                    inv_date=inv_date_str,
                    unit_price=unit_price,
                    create_json_dir=CREATE_JSON_DIR,
                    invoice_gen_dir=INVOICE_GEN_DIR
                )

                # Step 2: Update JSON with invoice details and calculate totals
                summary_data = strategy._update_and_aggregate_json(
                    json_path,
                    identifier,  # po_number
                    inv_ref=inv_ref,
                    inv_date=inv_date_str,
                    unit_price=unit_price
                )

                if summary_data:
                    st.session_state.summary_data = summary_data
                    st.success("✅ JSON updated with invoice details and totals calculated!")
                else:
                    st.error("❌ Failed to update JSON with invoice details")
                    st.stop()

            else:
                # For other strategies, use default processing
                json_path, identifier = strategy.process_excel_to_json(
                    temp_file_path,
                    JSON_OUTPUT_DIR,
                    create_json_dir=CREATE_JSON_DIR,
                    invoice_gen_dir=INVOICE_GEN_DIR
                )

            # Validate JSON
            missing_fields = strategy.validate_json_data(json_path)

            if missing_fields:
                st.error(f"❌ JSON validation failed. Missing fields: {', '.join(missing_fields)}")
                st.stop()

            # Success
            st.session_state.json_path = json_path
            st.session_state.identifier = identifier
            st.session_state.validation_complete = True
            st.session_state.workflow_step = 'overrides'
            
            # Cleanup temp file after successful processing
            if st.session_state.temp_file_path and st.session_state.temp_file_path.exists():
                try:
                    st.session_state.temp_file_path.unlink()
                except:
                    pass
            st.session_state.temp_file_path = None
            
            st.success("✅ File processed and validated successfully!")
            st.rerun()

        except Exception as e:
            st.error(f"❌ File processing failed: {e}")
            st.exception(e)
            # Ensure temp file is cleaned up on failure
            if st.session_state.get('temp_file_path') and st.session_state.temp_file_path.exists():
                try:
                    st.session_state.temp_file_path.unlink()
                except:
                    pass
            st.session_state.temp_file_path = None
            # Offer a way to go back
            if st.button("⬅️ Back to Upload"):
                st.session_state.workflow_step = 'upload'
                st.rerun()


def render_overrides_step(strategy):
    """Renders the UI for manual overrides and generation options."""
    st.subheader(f"6. Manual Overrides for {strategy.name}")

    ui_config = strategy.get_override_ui_config()

    # Dynamic UI based on strategy
    overrides = {}

    for key, config in ui_config.items():
        # --- START: feature_field_prefiller ---
        if config.get('prefill_from_filename', False):
            suggested_value = st.session_state.get('uploaded_filename', '')
            # Clean up the filename to be more suitable for an invoice number
            if suggested_value:
                suggested_value = Path(suggested_value).stem # Remove extension
            
            render_field_prefiller(
                field_label=config['label'],
                session_key=f"override_{key}",
                suggested_value=suggested_value,
                help_text="Click 'Use Filename' to use the uploaded file's name."
            )
            overrides[key] = st.session_state.get(f"override_{key}", "")
        elif key == 'inv_no':  # Special handling for invoice number with filename suggestion
            suggested_filename = st.session_state.get('uploaded_filename', '')
            # Clean up the filename to be more suitable for an invoice number
            if suggested_filename:
                suggested_filename = Path(suggested_filename).stem  # Remove extension
            
            render_field_prefiller(
                field_label=config['label'],
                session_key=f"override_{key}",
                suggested_value=suggested_filename,
                help_text="Click 'Use Filename' to use the uploaded file's name as the invoice number."
            )
            overrides[key] = st.session_state.get(f"override_{key}", "")
        # --- END: feature_field_prefiller ---
        elif config['type'] == 'text_input':
            default_val = config.get('default', '')
            if default_val == 'auto':
                default_val = get_suggested_inv_ref()
            overrides[key] = st.text_input(
                config['label'],
                value=default_val,
                key=f"override_{key}"
            )

        elif config['type'] == 'date_input':
            default_val = config.get('default', 'today')
            if default_val == 'today':
                default_date = datetime.date.today()
            elif default_val == 'tomorrow':
                default_date = datetime.date.today() + datetime.timedelta(days=1)
            else:
                default_date = datetime.date.today()

            overrides[key] = st.date_input(
                config['label'],
                value=default_date,
                format="DD/MM/YYYY",
                key=f"override_{key}"
            )

        elif config['type'] == 'number_input':
            overrides[key] = st.number_input(
                config['label'],
                min_value=config.get('min', 0.0),
                value=config.get('default', 0.0),
                step=config.get('step', 0.01),
                key=f"override_{key}"
            )

        elif config['type'] == 'text_area':
            overrides[key] = st.text_area(
                config['label'],
                value=config.get('default', ''),
                height=150,
                key=f"override_{key}"
            )

    # For 2nd Layer Leather, show current values (read-only) and summary
    if strategy.name == "2nd Layer Leather":
        st.info("📝 **Current Invoice Details:**")
        required_inputs = st.session_state.get('required_inputs', {})
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Invoice Reference:** {required_inputs.get('inv_ref', 'N/A')}")
            st.write(f"**Unit Price:** {required_inputs.get('unit_price', 'N/A')}")
        with col2:
            st.write(f"**Invoice Date:** {required_inputs.get('inv_date', 'N/A')}")

        # Show summary data if available
        summary_data = st.session_state.get('summary_data')
        if summary_data:
            st.markdown("---")
            st.subheader("📊 Invoice Summary")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("PO Number", summary_data.get("po_number", "N/A"))
                st.metric("Total Amount", f"${summary_data.get('amount', 0):,.2f}")
            with col2:
                st.metric("Total PCS", f"{summary_data.get('pcs', 0):,}")
                st.metric("Net Weight", f"{summary_data.get('net', 0):,.0f}")
            with col3:
                st.metric("Pallets", summary_data.get("pallet_count", 0))
                st.metric("Gross Weight", f"{summary_data.get('gross', 0):,.0f}")
            with col4:
                st.metric("CBM", f"{summary_data.get('cbm', 0):.2f}")
                st.metric("Item", summary_data.get("item", "N/A"))

    st.session_state.overrides = overrides

    # Navigation
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("⬅️ Back to Upload", use_container_width=True):
            st.session_state.workflow_step = 'upload'
            st.rerun()
    with col2:
        if st.button("Apply Overrides & Continue", use_container_width=True, type="primary"):
            # Apply overrides to JSON
            if strategy.apply_overrides(st.session_state.json_path, overrides):
                st.session_state.workflow_step = 'generate'
                st.success("✅ Overrides applied successfully!")
                st.rerun()
            else:
                st.error("❌ Failed to apply overrides")
    with col3:
        if st.button("🔄 Reset Workflow", use_container_width=True):
            reset_workflow()


def render_generate_step(strategy):
    """Renders the final generation options and download button."""
    st.subheader(f"7. Generation Options for {strategy.name}")

    generation_options = strategy.get_generation_options()

    # Display available options
    selected_options = []
    for option in generation_options:
        if st.checkbox(option['name'], value=True, key=f"gen_{option['key']}"):
            selected_options.append(option['key'])

    st.session_state.generation_options = selected_options

    if not selected_options:
        st.warning("Please select at least one generation option.")

    # Navigation
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("⬅️ Back to Overrides", use_container_width=True):
            st.session_state.workflow_step = 'overrides'
            st.rerun()
    with col2:
        if st.button("🚀 Generate Invoices", use_container_width=True, type="primary", disabled=not selected_options):
            try:
                # Generate documents
                with st.spinner("Generating invoice documents..."):
                    generated_files = strategy.generate_documents(
                        st.session_state.json_path,
                        Path(tempfile.mkdtemp()),
                        selected_options,
                        identifier=st.session_state.identifier,
                        invoice_gen_dir=INVOICE_GEN_DIR,
                        template_dir=TEMPLATE_DIR,
                        config_dir=CONFIG_DIR
                    )

                if generated_files:
                    # Apply print settings
                    st.info("📄 Applying print settings to generated files...")
                    files_processed, sheets_processed = apply_print_settings_to_files(
                        generated_files,
                        INVOICE_GEN_DIR
                    )

                    st.success(f"✅ Generated {len(generated_files)} files with print settings applied to {sheets_processed} sheets!")

                    # Prepare download
                    files_to_zip = [
                        {"name": st.session_state.json_path.name, "data": st.session_state.json_path.read_bytes()}
                    ]

                    for file_path in generated_files:
                        files_to_zip.append({
                            "name": file_path.name,
                            "data": file_path.read_bytes()
                        })

                    zip_buffer = create_download_zip(files_to_zip)

                    st.subheader("5. Download Generated Files")
                    st.download_button(
                        label="📥 Download All as ZIP",
                        data=zip_buffer,
                        file_name=f"{st.session_state.identifier}_invoice_pack.zip",
                        mime="application/zip",
                        use_container_width=True
                    )

                    # Final navigation
                    st.button("🎉 Start New Workflow", on_click=reset_workflow, use_container_width=True)

                else:
                    st.error("❌ Document generation failed. No files were created.")
                    if st.button("⬅️ Back to Overrides"):
                        st.session_state.workflow_step = 'overrides'
                        st.rerun()

            except Exception as e:
                st.error(f"An unexpected error occurred during generation: {e}")
                st.exception(e)
                if st.button("⬅️ Back to Overrides"):
                    st.session_state.workflow_step = 'overrides'
                    st.rerun()

# --- Main Workflow ---
st.header("Invoice Generation Workflow")

# Step 1: Strategy Selection
if st.session_state.workflow_step == 'select_strategy':
    st.subheader("1. Select Invoice Type")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🏭 High-Quality Leather", use_container_width=True, type="primary"):
            st.session_state.selected_strategy = STRATEGIES['high_quality']
            st.session_state.workflow_step = 'upload'
            st.rerun()

    with col2:
        if st.button("📦 2nd Layer Leather", use_container_width=True, type="primary"):
            st.session_state.selected_strategy = STRATEGIES['second_layer']
            st.session_state.workflow_step = 'upload'
            st.rerun()

    st.markdown("---")
    if st.button("🔄 Reset Workflow", use_container_width=True):
        reset_workflow()

# Step 2: File Upload
elif st.session_state.workflow_step == 'upload':
    strategy = st.session_state.selected_strategy
    render_upload_step(strategy)

# Step 3: Excel Validation
elif st.session_state.workflow_step == 'validate_excel':
    strategy = st.session_state.selected_strategy
    render_validate_excel_step(strategy)

# Step 4: Input Collection (for 2nd Layer Leather)
elif st.session_state.workflow_step == 'collect_inputs':
    strategy = st.session_state.selected_strategy
    render_collect_inputs_step(strategy)

# Step 5: File Processing
elif st.session_state.workflow_step == 'process_file':
    strategy = st.session_state.selected_strategy
    render_process_file_step(strategy)

# Step 6: Manual Overrides
elif st.session_state.workflow_step == 'overrides':
    strategy = st.session_state.selected_strategy
    render_overrides_step(strategy)

# Step 7: Generation
elif st.session_state.workflow_step == 'generate':
    strategy = st.session_state.selected_strategy
    render_generate_step(strategy)

# --- Footer ---
st.markdown("---")
st.markdown("*Unified Invoice Generation Suite - Powered by Strategy Pattern*")