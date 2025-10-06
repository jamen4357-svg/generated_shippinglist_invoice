#!/usr/bin/env python3
"""
Debug session state during workflow to understand auto-population issue
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def debug_session_state():
    """Debug what happens with session state during workflow"""

    print("=== DEBUGGING SESSION STATE FOR AUTO-POPULATION ===\n")

    # Simulate the scenario where user has uploaded a file and is at overrides step
    mock_session_state = {
        'uploaded_filename': 'TH25555.xlsx',
        'workflow_step': 'overrides',
        'override_inv_no': '',  # Should be empty initially
        'override_inv_ref': '',  # Should be empty initially
    }

    print("Mock Session State:")
    for key, value in mock_session_state.items():
        print(f"  {key}: '{value}'")

    print("\n" + "="*50)
    print("Testing auto-population logic:")

    # Test High Quality Leather inv_no field
    key = 'inv_no'
    config = {"type": "text_input", "label": "Invoice No", "default": "", "auto_populate_filename": True}

    default_val = config.get('default', '')

    # Auto-populate from filename if configured
    if config.get('auto_populate_filename', False):
        uploaded_filename = mock_session_state.get('uploaded_filename', '')
        override_key = f"override_{key}"
        current_field_value = mock_session_state.get(override_key, '')

        print(f"Field: {key}")
        print(f"Config has auto_populate_filename: {config.get('auto_populate_filename', False)}")
        print(f"Uploaded filename: '{uploaded_filename}'")
        print(f"Current field value: '{current_field_value}'")
        print(f"Field is empty: {not current_field_value}")

        if uploaded_filename and not current_field_value:
            # Only auto-populate if field is empty
            default_val = Path(uploaded_filename).stem
            print(f"✅ Auto-populated with: '{default_val}'")
        else:
            print("❌ Did NOT auto-populate")

    print(f"Final default_val: '{default_val}'")

    print("\n" + "="*30)
    print("Possible Issues:")

    issues = []

    # Check if uploaded_filename exists
    if not mock_session_state.get('uploaded_filename'):
        issues.append("❌ uploaded_filename is not set in session state")

    # Check if field already has a value
    if mock_session_state.get('override_inv_no'):
        issues.append("❌ override_inv_no already has a value, preventing auto-population")

    # Check if config has the flag
    if not config.get('auto_populate_filename', False):
        issues.append("❌ auto_populate_filename flag is not set to True")

    if not issues:
        issues.append("✅ No obvious issues found - auto-population should work")

    for issue in issues:
        print(issue)

    print("\n" + "="*30)
    print("Recommendations:")

    recommendations = [
        "1. Verify uploaded_filename is set when file is uploaded",
        "2. Ensure override_inv_no starts empty (not pre-filled)",
        "3. Check that auto_populate_filename flag is True in strategy config",
        "4. Confirm the logic is executed when overrides step is rendered"
    ]

    for rec in recommendations:
        print(rec)

if __name__ == "__main__":
    debug_session_state()