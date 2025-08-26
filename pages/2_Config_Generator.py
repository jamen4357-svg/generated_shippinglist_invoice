import streamlit as st
import os
import sys
import json
import subprocess
import tempfile
from pathlib import Path
import pandas as pd
import shutil
from datetime import datetime
import traceback
import openpyxl
from auth_wrapper import setup_page_auth

# --- Enhanced Authentication Setup ---
user_info = setup_page_auth(
    page_title="Company Setup Assistant", 
    page_name="Company Setup Assistant",
    layout="wide"
)

st.title("🏢 Company Setup Assistant")
st.markdown("### Set up invoice templates for new companies")

# --- Project Path Configuration ---
try:
    PROJECT_ROOT = Path(__file__).resolve().parent.parent
    CONFIG_MODULE_DIR = PROJECT_ROOT / "config_and_template_gen_module"
    INVOICE_GEN_DIR = PROJECT_ROOT / "invoice_gen"
    CONFIG_DIR = INVOICE_GEN_DIR / "config"
    TEMPLATE_DIR = INVOICE_GEN_DIR / "TEMPLATE"
    
    # Ensure directories exist
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)
    
except Exception as e:
    st.error(f"❌ Error configuring paths: {e}")
    st.stop()

# --- Helper Functions ---
def validate_excel_file(file_path: Path) -> tuple[bool, str]:
    """Validate uploaded Excel file"""
    try:
        workbook = openpyxl.load_workbook(str(file_path))
        sheet_names = workbook.sheetnames
        if not sheet_names:
            return False, "Excel file contains no worksheets"
        return True, f"Valid Excel file with {len(sheet_names)} worksheet(s): {', '.join(sheet_names)}"
    except Exception as e:
        return False, f"Invalid Excel file: {str(e)}"

def run_config_analysis(excel_path: Path, output_dir: Path) -> tuple[bool, str, Path]:
    """Run the config analysis using the existing module"""
    try:
        analyze_script = CONFIG_MODULE_DIR / "config_data_extractor" / "analyze_excel.py"
        output_file = output_dir / f"{excel_path.stem}_analysis.json"
        
        cmd = [
            sys.executable,
            str(analyze_script),
            str(excel_path),
            "--output", str(output_file)
        ]
        
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            cwd=str(CONFIG_MODULE_DIR),
            timeout=120
        )
        
        if result.returncode == 0:
            if output_file.exists():
                return True, "Analysis completed successfully", output_file
            else:
                return False, "Analysis script ran but no output file was created", output_file
        else:
            return False, f"Analysis failed: {result.stderr}", output_file
            
    except subprocess.TimeoutExpired:
        return False, "Analysis timed out (took longer than 2 minutes)", output_file
    except Exception as e:
        return False, f"Error running analysis: {str(e)}", output_file

def run_config_generation(analysis_file: Path, company_name: str, template_type: str, output_dir: Path) -> tuple[bool, str, Path]:
    """Generate configuration using the existing module"""
    try:
        main_script = CONFIG_MODULE_DIR / "main.py"
        config_output = output_dir / f"{company_name}_{template_type}_config.json"
        
        cmd = [
            sys.executable,
            str(main_script),
            str(analysis_file.parent / f"{analysis_file.stem.replace('_analysis', '')}.xlsx"),
            "--output", str(config_output),
            "--generate-xlsx",
            "--xlsx-output", str(output_dir / f"{company_name}_{template_type}_template.xlsx")
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(CONFIG_MODULE_DIR),
            timeout=300
        )
        
        if result.returncode == 0:
            return True, "Configuration generated successfully", config_output
        else:
            return False, f"Configuration generation failed: {result.stderr}", config_output
            
    except subprocess.TimeoutExpired:
        return False, "Configuration generation timed out", config_output
    except Exception as e:
        return False, f"Error generating configuration: {str(e)}", config_output

def display_analysis_summary(analysis_file: Path):
    """Display analysis results in a user-friendly format"""
    try:
        with open(analysis_file, 'r', encoding='utf-8') as f:
            analysis_data = json.load(f)
        
        st.subheader("📊 Template Analysis Results")
        
        # Basic info
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Sheets", len(analysis_data.get('sheets', [])))
        with col2:
            total_headers = sum(len(sheet.get('header_positions', [])) for sheet in analysis_data.get('sheets', []))
            st.metric("Headers Found", total_headers)
        
        # Sheet details
        st.subheader("📋 Worksheet Details")
        for i, sheet in enumerate(analysis_data.get('sheets', [])):
            with st.expander(f"Sheet: {sheet.get('sheet_name', f'Sheet {i+1}')}"):
                st.write(f"**Headers found:** {len(sheet.get('header_positions', []))}")
                
                if sheet.get('header_positions'):
                    headers_df = pd.DataFrame([
                        {
                            'Position': f"{hp.get('column', 'N/A')}{hp.get('row', 'N/A')}",
                            'Text': hp.get('keyword', 'N/A'),
                            'Font': hp.get('font_name', 'N/A')
                        }
                        for hp in sheet.get('header_positions', [])
                    ])
                    st.dataframe(headers_df, use_container_width=True)
        
        return True
        
    except Exception as e:
        st.error(f"❌ Error displaying analysis: {e}")
        return False

# --- Main Interface ---

# Step 1: Company Information
st.header("Step 1: Company Information")
with st.form("company_info"):
    col1, col2 = st.columns(2)
    with col1:
        company_name = st.text_input(
            "Company Name *", 
            placeholder="Enter the company name (e.g., ABC Manufacturing)",
            help="This will be used to name the configuration files"
        )
    with col2:
        template_type = st.selectbox(
            "Template Type *",
            ["Invoice", "Packing_List", "Combined"],
            help="Select the type of template you're setting up"
        )
    
    submit_info = st.form_submit_button("📝 Continue to Upload", use_container_width=True)

if submit_info and company_name:
    st.session_state['company_name'] = company_name.strip().replace(' ', '_')
    st.session_state['template_type'] = template_type
    st.success(f"✅ Company: {company_name} | Template: {template_type}")

# Step 2: File Upload
if 'company_name' in st.session_state:
    st.header("Step 2: Upload Excel Template")
    
    uploaded_file = st.file_uploader(
        "Upload Excel Invoice Template",
        type=['xlsx'],
        help="Upload the Excel file that you want to use as a template for generating invoices"
    )
    
    if uploaded_file is not None:
        # Save uploaded file
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir_path = Path(temp_dir)
            excel_file_path = temp_dir_path / uploaded_file.name
            
            with open(excel_file_path, 'wb') as f:
                f.write(uploaded_file.getbuffer())
            
            # Validate file
            is_valid, validation_msg = validate_excel_file(excel_file_path)
            
            if is_valid:
                st.success(f"✅ {validation_msg}")
                
                # Step 3: Analysis
                st.header("Step 3: Template Analysis")
                
                if st.button("🔍 Analyze Template Structure", use_container_width=True):
                    with st.spinner("Analyzing template structure... This may take a moment."):
                        success, message, analysis_file = run_config_analysis(excel_file_path, temp_dir_path)
                    
                    if success:
                        st.success(f"✅ {message}")
                        
                        # Display analysis results
                        if display_analysis_summary(analysis_file):
                            st.session_state['analysis_file'] = analysis_file.read_text()
                            st.session_state['excel_file_name'] = uploaded_file.name
                            st.session_state['excel_file_data'] = uploaded_file.getbuffer()
                    else:
                        st.error(f"❌ {message}")
            else:
                st.error(f"❌ {validation_msg}")

# Step 4: Configuration Generation
if 'analysis_file' in st.session_state:
    st.header("Step 4: Generate Configuration")
    
    st.info("📋 The system will now create the configuration files needed for invoice generation.")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⚙️ Generate Configuration", use_container_width=True):
            with st.spinner("Generating configuration files..."):
                # Recreate files in new temp directory
                with tempfile.TemporaryDirectory() as temp_dir:
                    temp_dir_path = Path(temp_dir)
                    
                    # Restore analysis file
                    analysis_file_path = temp_dir_path / f"{st.session_state['company_name']}_analysis.json"
                    with open(analysis_file_path, 'w') as f:
                        f.write(st.session_state['analysis_file'])
                    
                    # Restore Excel file
                    excel_file_path = temp_dir_path / st.session_state['excel_file_name']
                    with open(excel_file_path, 'wb') as f:
                        f.write(st.session_state['excel_file_data'])
                    
                    success, message, config_file = run_config_generation(
                        analysis_file_path,
                        st.session_state['company_name'],
                        st.session_state['template_type'],
                        temp_dir_path
                    )
                    
                    if success:
                        st.success(f"✅ {message}")
                        
                        # Step 5: Save and Deploy
                        st.header("Step 5: Save Configuration")
                        
                        config_final_path = CONFIG_DIR / config_file.name
                        template_final_path = TEMPLATE_DIR / f"{st.session_state['company_name']}_{st.session_state['template_type']}_template.xlsx"
                        
                        try:
                            # Copy files to final locations
                            shutil.copy2(str(config_file), str(config_final_path))
                            
                            processed_xlsx = temp_dir_path / f"{st.session_state['company_name']}_{st.session_state['template_type']}_template.xlsx"
                            if processed_xlsx.exists():
                                shutil.copy2(str(processed_xlsx), str(template_final_path))
                            
                            st.success("🎉 Configuration successfully saved!")
                            
                            # Show file locations
                            st.subheader("📁 Files Created")
                            st.code(f"Config: {config_final_path}")
                            st.code(f"Template: {template_final_path}")
                            
                            # Download options
                            st.subheader("📥 Download Files")
                            col_dl1, col_dl2 = st.columns(2)
                            
                            with col_dl1:
                                if config_file.exists():
                                    st.download_button(
                                        "📄 Download Config JSON",
                                        data=config_file.read_bytes(),
                                        file_name=config_file.name,
                                        mime="application/json"
                                    )
                            
                            with col_dl2:
                                if processed_xlsx.exists():
                                    st.download_button(
                                        "📊 Download Processed Template",
                                        data=processed_xlsx.read_bytes(),
                                        file_name=processed_xlsx.name,
                                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                                    )
                            
                            # Next steps
                            st.subheader("✅ Next Steps")
                            st.markdown("""
                            Your company template is now ready! You can:
                            
                            1. **Test it**: Go to the Invoice Generation page to test your new configuration
                            2. **Make adjustments**: If needed, you can re-run this process to update the configuration
                            3. **Train users**: Share the company name with users who need to generate invoices
                            
                            **Company identifier for invoice generation:** `{}`
                            """.format(st.session_state['company_name']))
                            
                            # Clear session state
                            if st.button("🔄 Setup Another Company", use_container_width=True):
                                for key in ['company_name', 'template_type', 'analysis_file', 'excel_file_name', 'excel_file_data']:
                                    if key in st.session_state:
                                        del st.session_state[key]
                                st.rerun()
                        
                        except Exception as e:
                            st.error(f"❌ Error saving files: {e}")
                            st.code(traceback.format_exc())
                    
                    else:
                        st.error(f"❌ {message}")
    
    with col2:
        if st.button("🔧 Advanced Options", use_container_width=True):
            st.info("💡 Advanced configuration options will be available in future updates.")

# Help Section
with st.expander("❓ Need Help?"):
    st.markdown("""
    ### Common Issues and Solutions
    
    **Excel file not uploading:**
    - Ensure the file is in .xlsx format (not .xls)
    - File size should be under 200MB
    - Close the file in Excel before uploading
    
    **Analysis failing:**
    - Check if the Excel file has proper headers
    - Ensure the file isn't password protected
    - Try with a simpler template first
    
    **Configuration not working:**
    - Verify the company name doesn't contain special characters
    - Check that the Excel template follows standard invoice format
    - Contact support if issues persist
    
    ### Support
    If you need additional help, please contact the IT support team with:
    - The company name you're trying to set up
    - The Excel file you're using
    - Any error messages you received
    """)

# Display current configurations
with st.expander("📋 View Existing Configurations"):
    st.subheader("Current Company Configurations")
    
    config_files = list(CONFIG_DIR.glob("*.json"))
    if config_files:
        df_configs = pd.DataFrame([
            {
                'Company': f.stem.replace('_config', '').replace('_', ' '),
                'File': f.name,
                'Created': datetime.fromtimestamp(f.stat().st_mtime).strftime('%Y-%m-%d %H:%M'),
                'Size': f"{f.stat().st_size / 1024:.1f} KB"
            }
            for f in config_files
        ])
        st.dataframe(df_configs, use_container_width=True)
    else:
        st.info("No company configurations found. Use this page to create your first one!")
