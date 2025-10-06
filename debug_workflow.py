#!/usr/bin/env python3
"""
Comprehensive debug of auto-population issue in actual workflow
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def simulate_workflow_issue():
    """Simulate the exact workflow issue the user is experiencing"""

    print("=== SIMULATING USER WORKFLOW ISSUE ===\n")

    # Simulate fresh session state (user just started)
    session_state = {
        'uploaded_filename': None,
        'workflow_step': 'select_strategy',
        'override_inv_no': None,  # Not set yet
        'override_inv_ref': None,  # Not set yet
    }

    print("Initial Session State:")
    for k, v in session_state.items():
        print(f"  {k}: {repr(v)}")

    # Step 1: User uploads file
    print("\n" + "="*50)
    print("STEP 1: User uploads 'TH25555.xlsx'")
    session_state['uploaded_filename'] = 'TH25555.xlsx'
    session_state['workflow_step'] = 'validate_excel'

    print("After upload:")
    for k, v in session_state.items():
        print(f"  {k}: {repr(v)}")

    # Step 2: User validates and processes
    print("\n" + "="*50)
    print("STEP 2: User validates Excel and processes file")
    session_state['workflow_step'] = 'process_file'
    # Processing happens here...

    print("After processing:")
    for k, v in session_state.items():
        print(f"  {k}: {repr(v)}")

    # Step 3: User reaches overrides step
    print("\n" + "="*50)
    print("STEP 3: User reaches overrides step")
    session_state['workflow_step'] = 'overrides'

    # This is where auto-population should happen
    print("At overrides step - checking auto-population logic:")

    # Test High Quality Leather inv_no field
    key = 'inv_no'
    config = {"type": "text_input", "label": "Invoice No", "default": "", "auto_populate_filename": True}

    uploaded_filename = session_state.get('uploaded_filename', '')
    current_field_value = session_state.get(f"override_{key}", '')

    print(f"  Field: {key}")
    print(f"  uploaded_filename: {repr(uploaded_filename)}")
    print(f"  current field value: {repr(current_field_value)}")
    print(f"  field is empty: {not current_field_value}")

    default_val = config.get('default', '')

    if config.get('auto_populate_filename', False):
        if uploaded_filename and not current_field_value:
            default_val = Path(uploaded_filename).stem
            print(f"  ✅ Auto-populated with: {repr(default_val)}")
        else:
            print("  ❌ Did NOT auto-populate")
            if not uploaded_filename:
                print("     Reason: uploaded_filename is empty")
            if current_field_value:
                print(f"     Reason: field already has value: {repr(current_field_value)}")

    print(f"  Final default_val: {repr(default_val)}")

    # What would happen in st.text_input?
    final_value = session_state.get(f"override_{key}", default_val)
    print(f"  st.text_input would show: {repr(final_value)}")

    print("\n" + "="*50)
    print("POSSIBLE ISSUES:")

    issues = []

    if session_state.get('uploaded_filename') is None:
        issues.append("❌ uploaded_filename is None - file was never uploaded")

    if session_state.get('override_inv_no') is not None and session_state.get('override_inv_no') != '':
        issues.append("❌ override_inv_no already has a value")

    if not config.get('auto_populate_filename', False):
        issues.append("❌ auto_populate_filename flag not set")

    if not issues:
        issues.append("✅ Logic should work - check if code was actually updated")

    for issue in issues:
        print(issue)

    print("\n" + "="*50)
    print("DEBUGGING STEPS:")

    steps = [
        "1. Check if uploaded_filename is set after file upload",
        "2. Verify override_inv_no starts as None/empty",
        "3. Confirm auto_populate_filename flag is True in strategy",
        "4. Check if render_overrides_step function has the new logic",
        "5. Add debug prints to see what's happening in real time"
    ]

    for step in steps:
        print(step)

if __name__ == "__main__":
    simulate_workflow_issue()