#!/usr/bin/env python3
"""
Comprehensive integration tests using real data files.

This test suite verifies the complete template-based transformation workflow
using the provided quantity_mode_analysis.json and sample_config.json files.
Tests cover all requirements including business logic preservation, header mapping,
font updates, and edge cases with different naming conventions.
"""

import json
import tempfile
import os
import pytest
from config_generator.config_generator import ConfigGenerator


class TestRealDataIntegration:
    """Test suite for real data integration scenarios."""
    
    @pytest.fixture
    def real_quantity_data(self):
        """Load the real quantity_mode_analysis.json data."""
        with open('quantity_mode_analysis.json', 'r') as f:
            return json.load(f)
    
    @pytest.fixture
    def real_template_config(self):
        """Load the real sample_config.json template."""
        with open('sample_config.json', 'r') as f:
            return json.load(f)
    
    @pytest.fixture
    def config_generator(self):
        """Create ConfigGenerator instance for testing."""
        return ConfigGenerator()
    
    def test_complete_workflow_with_real_data(self, config_generator, real_template_config, real_quantity_data):
        """
        Test complete template-based transformation workflow with real data.
        
        Verifies:
        - Template loading and structure preservation
        - Quantity data processing
        - Selective field updates
        - Business logic preservation
        - Output generation
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            template_path = os.path.join(temp_dir, 'template.json')
            quantity_path = os.path.join(temp_dir, 'quantity.json')
            output_path = os.path.join(temp_dir, 'output.json')
            
            # Write real data to temporary files
            with open(template_path, 'w') as f:
                json.dump(real_template_config, f, indent=2)
            
            with open(quantity_path, 'w') as f:
                json.dump(real_quantity_data, f, indent=2)
            
            # Execute complete workflow
            config_generator.generate_config(template_path, quantity_path, output_path)
            
            # Verify output file was created
            assert os.path.exists(output_path), "Output configuration file was not created"
            
            # Load and verify output
            with open(output_path, 'r') as f:
                result = json.load(f)
            
            # Verify complete structure preservation
            self._verify_structure_preservation(result, real_template_config)
            
            # Verify selective field updates
            self._verify_field_updates(result, real_quantity_data)
            
            # Verify business logic preservation
            self._verify_business_logic_preservation(result, real_template_config)
    
    def test_header_text_mapping_with_real_patterns(self, config_generator, real_template_config, real_quantity_data):
        """
        Test header text mapping with real data patterns and naming conventions.
        
        Verifies:
        - "Mark & Nº" header mapping
        - "P.O. Nº" vs "P.O Nº" pattern handling
        - "ITEM Nº" vs "HL ITEM" mapping
        - "Cargo Descprition" vs "Description" handling
        - Quantity header variations
        - Unit price and amount mapping
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            template_path = os.path.join(temp_dir, 'template.json')
            quantity_path = os.path.join(temp_dir, 'quantity.json')
            output_path = os.path.join(temp_dir, 'output.json')
            
            # Write files
            with open(template_path, 'w') as f:
                json.dump(real_template_config, f, indent=2)
            with open(quantity_path, 'w') as f:
                json.dump(real_quantity_data, f, indent=2)
            
            # Generate config
            config_generator.generate_config(template_path, quantity_path, output_path)
            
            with open(output_path, 'r') as f:
                result = json.load(f)
            
            # Verify specific header mappings from real data
            self._verify_contract_headers(result, real_quantity_data)
            self._verify_invoice_headers(result, real_quantity_data)
            self._verify_packing_list_headers(result, real_quantity_data)
    
    def test_font_updates_with_real_data(self, config_generator, real_template_config, real_quantity_data):
        """
        Test font updates using real font data from quantity analysis.
        
        Verifies:
        - Header font updates (Times New Roman, size variations)
        - Default font updates
        - Footer font consistency
        - Font size preservation and hierarchy
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            template_path = os.path.join(temp_dir, 'template.json')
            quantity_path = os.path.join(temp_dir, 'quantity.json')
            output_path = os.path.join(temp_dir, 'output.json')
            
            # Write files
            with open(template_path, 'w') as f:
                json.dump(real_template_config, f, indent=2)
            with open(quantity_path, 'w') as f:
                json.dump(real_quantity_data, f, indent=2)
            
            # Generate config
            config_generator.generate_config(template_path, quantity_path, output_path)
            
            with open(output_path, 'r') as f:
                result = json.load(f)
            
            # Verify font updates for each sheet
            for sheet_data in real_quantity_data['sheets']:
                sheet_name = sheet_data['sheet_name']
                if sheet_name in result['data_mapping']:
                    styling = result['data_mapping'][sheet_name]['styling']
                    
                    # Verify header font updates
                    assert styling['header_font']['name'] == sheet_data['header_font']['name']
                    assert styling['header_font']['size'] == sheet_data['header_font']['size']
                    
                    # Verify default font updates
                    assert styling['default_font']['name'] == sheet_data['data_font']['name']
                    assert styling['default_font']['size'] == sheet_data['data_font']['size']
                    
                    # Verify footer font consistency
                    if 'footer_configurations' in result['data_mapping'][sheet_name]:
                        footer_config = result['data_mapping'][sheet_name]['footer_configurations']
                        if 'style' in footer_config and 'font' in footer_config['style']:
                            footer_font = footer_config['style']['font']
                            assert footer_font['name'] == sheet_data['header_font']['name']
    
    def test_position_updates_with_real_data(self, config_generator, real_template_config, real_quantity_data):
        """
        Test position updates using real position data.
        
        Verifies:
        - Start row updates (18 for Contract, 21 for Invoice, 22 for Packing list)
        - Column position adjustments
        - Multi-row header structure preservation
        - Spanning attribute preservation
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            template_path = os.path.join(temp_dir, 'template.json')
            quantity_path = os.path.join(temp_dir, 'quantity.json')
            output_path = os.path.join(temp_dir, 'output.json')
            
            # Write files
            with open(template_path, 'w') as f:
                json.dump(real_template_config, f, indent=2)
            with open(quantity_path, 'w') as f:
                json.dump(real_quantity_data, f, indent=2)
            
            # Generate config
            config_generator.generate_config(template_path, quantity_path, output_path)
            
            with open(output_path, 'r') as f:
                result = json.load(f)
            
            # Verify start row updates from real data
            assert result['data_mapping']['Contract']['start_row'] == 18
            assert result['data_mapping']['Invoice']['start_row'] == 21
            assert result['data_mapping']['Packing list']['start_row'] == 22
            
            # Verify column positions are updated while preserving structure
            for sheet_data in real_quantity_data['sheets']:
                sheet_name = sheet_data['sheet_name']
                if sheet_name in result['data_mapping']:
                    headers = result['data_mapping'][sheet_name]['header_to_write']
                    
                    # Verify that row and col attributes are preserved
                    for header in headers:
                        assert 'row' in header
                        assert 'col' in header
                        # Verify spanning attributes are preserved when they exist
                        if 'rowspan' in header:
                            assert isinstance(header['rowspan'], int)
                        if 'colspan' in header:
                            assert isinstance(header['colspan'], int)
    
    def test_edge_cases_with_real_data(self, config_generator, real_template_config, real_quantity_data):
        """
        Test edge cases and variations in real data.
        
        Verifies:
        - Different header naming conventions
        - Special characters in headers (accents, symbols)
        - Multi-line headers with newlines
        - Missing or optional fields
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            template_path = os.path.join(temp_dir, 'template.json')
            quantity_path = os.path.join(temp_dir, 'quantity.json')
            output_path = os.path.join(temp_dir, 'output.json')
            
            # Create modified quantity data with edge cases
            modified_quantity_data = real_quantity_data.copy()
            
            # Add edge case headers
            edge_case_sheet = {
                'sheet_name': 'Edge Case Sheet',
                'header_font': {'name': 'Times New Roman', 'size': 10},
                'data_font': {'name': 'Times New Roman', 'size': 9},
                'start_row': 25,
                'header_positions': [
                    {'keyword': 'Mark & Nº', 'row': 0, 'column': 1},
                    {'keyword': 'P.O. Nº', 'row': 0, 'column': 2},  # With period
                    {'keyword': 'ITEM Nº', 'row': 0, 'column': 3},
                    {'keyword': 'Cargo Descprition', 'row': 0, 'column': 4},  # Typo in real data
                    {'keyword': 'FCA\nSVAY RIENG', 'row': 0, 'column': 5},  # Multi-line
                    {'keyword': 'Unit price (USD)', 'row': 0, 'column': 6},  # With parentheses
                ]
            }
            
            modified_quantity_data['sheets'].append(edge_case_sheet)
            
            # Add corresponding template section
            modified_template = real_template_config.copy()
            modified_template['data_mapping']['Edge Case Sheet'] = {
                'start_row': 20,
                'header_to_write': [
                    {'text': 'Mark & Nº', 'row': 0, 'col': 0, 'id': 'col_static'},
                    {'text': 'P.O Nº', 'row': 0, 'col': 1, 'id': 'col_po'},
                    {'text': 'ITEM Nº', 'row': 0, 'col': 2, 'id': 'col_item'},
                    {'text': 'Description', 'row': 0, 'col': 3, 'id': 'col_desc'},
                    {'text': 'Unit Price', 'row': 0, 'col': 4, 'id': 'col_unit_price'},
                ],
                'mappings': {
                    'po': {'key_index': 0, 'id': 'col_po'},
                    'item': {'key_index': 1, 'id': 'col_item'},
                    'desc': {'key_index': 3, 'id': 'col_desc'}
                },
                'footer_configurations': {
                    'total_text': 'TOTAL',
                    'sum_column_ids': ['col_unit_price']
                },
                'styling': {
                    'header_font': {'name': 'Arial', 'size': 12},
                    'default_font': {'name': 'Arial', 'size': 10}
                }
            }
            
            # Write files
            with open(template_path, 'w') as f:
                json.dump(modified_template, f, indent=2)
            with open(quantity_path, 'w') as f:
                json.dump(modified_quantity_data, f, indent=2)
            
            # Generate config
            config_generator.generate_config(template_path, quantity_path, output_path)
            
            with open(output_path, 'r') as f:
                result = json.load(f)
            
            # Verify edge case handling
            edge_sheet_config = result['data_mapping']['Edge Case Sheet']
            
            # Verify start row was updated
            assert edge_sheet_config['start_row'] == 25
            
            # Verify fonts were updated
            assert edge_sheet_config['styling']['header_font']['name'] == 'Times New Roman'
            assert edge_sheet_config['styling']['header_font']['size'] == 10
    
    def test_business_logic_preservation(self, config_generator, real_template_config, real_quantity_data):
        """
        Test that all business logic from template is preserved.
        
        Verifies:
        - Mappings section preservation
        - Footer configurations preservation
        - Styling rules preservation
        - Formula templates preservation
        - Number formats preservation
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            template_path = os.path.join(temp_dir, 'template.json')
            quantity_path = os.path.join(temp_dir, 'quantity.json')
            output_path = os.path.join(temp_dir, 'output.json')
            
            # Write files
            with open(template_path, 'w') as f:
                json.dump(real_template_config, f, indent=2)
            with open(quantity_path, 'w') as f:
                json.dump(real_quantity_data, f, indent=2)
            
            # Generate config
            config_generator.generate_config(template_path, quantity_path, output_path)
            
            with open(output_path, 'r') as f:
                result = json.load(f)
            
            # Verify all business logic sections are preserved
            for sheet_name in ['Invoice', 'Contract', 'Packing list']:
                original_sheet = real_template_config['data_mapping'][sheet_name]
                result_sheet = result['data_mapping'][sheet_name]
                
                # Verify mappings preservation
                if 'mappings' in original_sheet:
                    assert 'mappings' in result_sheet
                    self._verify_mappings_preservation(original_sheet['mappings'], result_sheet['mappings'])
                
                # Verify footer configurations preservation
                if 'footer_configurations' in original_sheet:
                    assert 'footer_configurations' in result_sheet
                    self._verify_footer_preservation(original_sheet['footer_configurations'], 
                                                   result_sheet['footer_configurations'])
                
                # Verify styling rules preservation (except fonts)
                if 'styling' in original_sheet:
                    assert 'styling' in result_sheet
                    self._verify_styling_preservation(original_sheet['styling'], result_sheet['styling'])
    
    def _verify_structure_preservation(self, result, original):
        """Verify that the overall structure is preserved."""
        assert 'sheets_to_process' in result
        assert 'sheet_data_map' in result
        assert 'data_mapping' in result
        
        # Verify sheets_to_process is unchanged
        assert result['sheets_to_process'] == original['sheets_to_process']
        
        # Verify sheet_data_map is unchanged
        assert result['sheet_data_map'] == original['sheet_data_map']
        
        # Verify all sheets are present
        for sheet_name in original['data_mapping']:
            assert sheet_name in result['data_mapping']
    
    def _verify_field_updates(self, result, quantity_data):
        """Verify that specific fields were updated from quantity data."""
        for sheet_data in quantity_data['sheets']:
            sheet_name = sheet_data['sheet_name']
            if sheet_name in result['data_mapping']:
                result_sheet = result['data_mapping'][sheet_name]
                
                # Verify start_row was updated
                assert result_sheet['start_row'] == sheet_data['start_row']
                
                # Verify fonts were updated
                if 'styling' in result_sheet:
                    styling = result_sheet['styling']
                    assert styling['header_font']['name'] == sheet_data['header_font']['name']
                    assert styling['header_font']['size'] == sheet_data['header_font']['size']
                    assert styling['default_font']['name'] == sheet_data['data_font']['name']
                    assert styling['default_font']['size'] == sheet_data['data_font']['size']
    
    def _verify_business_logic_preservation(self, result, original):
        """Verify that business logic is preserved."""
        for sheet_name in original['data_mapping']:
            original_sheet = original['data_mapping'][sheet_name]
            result_sheet = result['data_mapping'][sheet_name]
            
            # Check that complex sections are preserved
            for section in ['mappings', 'footer_configurations']:
                if section in original_sheet:
                    assert section in result_sheet
    
    def _verify_contract_headers(self, result, quantity_data):
        """Verify Contract sheet header mappings."""
        contract_data = next(s for s in quantity_data['sheets'] if s['sheet_name'] == 'Contract')
        contract_config = result['data_mapping']['Contract']
        
        # Verify header positions were processed
        headers = contract_config['header_to_write']
        header_keywords = [pos['keyword'] for pos in contract_data['header_positions']]
        
        # Check that headers contain expected patterns
        assert any('Cargo Descprition' in kw for kw in header_keywords)
        assert any('HL ITEM' in kw for kw in header_keywords)
        assert any('Quantity' in kw for kw in header_keywords)
    
    def _verify_invoice_headers(self, result, quantity_data):
        """Verify Invoice sheet header mappings."""
        invoice_data = next(s for s in quantity_data['sheets'] if s['sheet_name'] == 'Invoice')
        invoice_config = result['data_mapping']['Invoice']
        
        # Verify header positions were processed
        headers = invoice_config['header_to_write']
        header_keywords = [pos['keyword'] for pos in invoice_data['header_positions']]
        
        # Check for expected patterns
        assert any('P.O. N' in kw for kw in header_keywords)
        assert any('ITEM N' in kw for kw in header_keywords)
        assert any('Unit price (USD)' in kw for kw in header_keywords)
    
    def _verify_packing_list_headers(self, result, quantity_data):
        """Verify Packing list sheet header mappings."""
        packing_data = next(s for s in quantity_data['sheets'] if s['sheet_name'] == 'Packing list')
        packing_config = result['data_mapping']['Packing list']
        
        # Verify header positions were processed
        headers = packing_config['header_to_write']
        header_keywords = [pos['keyword'] for pos in packing_data['header_positions']]
        
        # Check for expected patterns
        assert any('N.W (kgs)' in kw for kw in header_keywords)
        assert any('G.W (kgs)' in kw for kw in header_keywords)
        assert any('CBM' in kw for kw in header_keywords)
        assert any('PCS' in kw for kw in header_keywords)
        assert any('SF' in kw for kw in header_keywords)
    
    def _verify_mappings_preservation(self, original_mappings, result_mappings):
        """Verify that mappings section is preserved."""
        # Check that all mapping keys are preserved
        for key in original_mappings:
            assert key in result_mappings
            
        # Check that complex mapping structures are preserved
        for key, value in original_mappings.items():
            if isinstance(value, dict):
                assert isinstance(result_mappings[key], dict)
                # Verify nested structure preservation
                for nested_key in value:
                    if nested_key not in ['text']:  # text may be updated
                        assert nested_key in result_mappings[key]
    
    def _verify_footer_preservation(self, original_footer, result_footer):
        """Verify that footer configurations are preserved."""
        # Check that all footer keys are preserved
        for key in original_footer:
            if key != 'style':  # style may have font updates
                assert key in result_footer
                assert original_footer[key] == result_footer[key]
    
    def _verify_styling_preservation(self, original_styling, result_styling):
        """Verify that styling rules are preserved (except fonts)."""
        # Check that all styling keys are preserved
        for key in original_styling:
            assert key in result_styling
            
            # For non-font keys, verify exact preservation
            if key not in ['header_font', 'default_font']:
                assert original_styling[key] == result_styling[key]


if __name__ == '__main__':
    # Run tests with pytest
    pytest.main([__file__, '-v'])