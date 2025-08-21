"""
Unit tests for PositionUpdater component.

Tests the functionality of updating start_row values and column positions
in configuration templates while preserving rowspan/colspan attributes.
"""

import pytest
import copy
from config_generator.position_updater import PositionUpdater
from config_generator.models import QuantityAnalysisData, SheetData, HeaderPosition, FontInfo


class TestPositionUpdater:
    """Test cases for PositionUpdater component."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.updater = PositionUpdater()
        
        # Sample template data
        self.sample_template = {
            'sheets_to_process': ['Invoice', 'Contract', 'Packing list'],
            'data_mapping': {
                'Invoice': {
                    'start_row': 20,
                    'header_to_write': [
                        {'row': 0, 'col': 0, 'text': 'Mark & Nº', 'id': 'col_static', 'rowspan': 1},
                        {'row': 0, 'col': 1, 'text': 'P.O. Nº', 'id': 'col_po', 'rowspan': 1},
                        {'row': 0, 'col': 2, 'text': 'Description', 'id': 'col_desc', 'rowspan': 1},
                        {'row': 0, 'col': 3, 'text': 'ITEM Nº', 'id': 'col_item', 'rowspan': 1},
                        {'row': 0, 'col': 4, 'text': 'Quantity', 'id': 'col_qty_sf'},
                        {'row': 0, 'col': 5, 'text': 'Unit price (USD)', 'id': 'col_unit_price', 'rowspan': 1},
                        {'row': 0, 'col': 6, 'text': 'Amount (USD)', 'id': 'col_amount', 'rowspan': 1}
                    ]
                },
                'Contract': {
                    'start_row': 15,
                    'header_to_write': [
                        {'row': 0, 'col': 0, 'text': 'No.', 'id': 'col_no', 'rowspan': 1},
                        {'row': 0, 'col': 1, 'text': 'ITEM Nº', 'id': 'col_item', 'rowspan': 1},
                        {'row': 0, 'col': 2, 'text': 'Quantity', 'id': 'col_qty_sf'},
                        {'row': 0, 'col': 3, 'text': 'Unit Price(USD)', 'id': 'col_unit_price', 'rowspan': 1},
                        {'row': 0, 'col': 4, 'text': 'Total value(USD)', 'id': 'col_amount', 'rowspan': 1}
                    ]
                },
                'Packing list': {
                    'start_row': 19,
                    'header_to_write': [
                        {'row': 0, 'col': 0, 'text': 'Mark & Nº', 'id': 'col_static', 'rowspan': 2},
                        {'row': 0, 'col': 1, 'text': 'Pallet\nNO.', 'id': 'col_pallet', 'rowspan': 2},
                        {'row': 0, 'col': 2, 'text': 'P.O Nº', 'id': 'col_po', 'rowspan': 2},
                        {'row': 0, 'col': 3, 'text': 'ITEM Nº', 'id': 'col_item', 'rowspan': 2},
                        {'row': 0, 'col': 4, 'text': 'Description', 'id': 'col_desc', 'rowspan': 2},
                        {'row': 0, 'col': 5, 'text': 'Quantity', 'colspan': 2},
                        {'row': 0, 'col': 7, 'text': 'N.W (kgs)', 'id': 'col_net', 'rowspan': 2},
                        {'row': 0, 'col': 8, 'text': 'G.W (kgs)', 'id': 'col_gross', 'rowspan': 2},
                        {'row': 0, 'col': 9, 'text': 'CBM', 'id': 'col_cbm', 'rowspan': 2},
                        {'row': 1, 'col': 5, 'text': 'PCS', 'id': 'col_qty_pcs'},
                        {'row': 1, 'col': 6, 'text': 'SF', 'id': 'col_qty_sf'}
                    ]
                }
            }
        }
        
        # Sample quantity analysis data
        self.sample_quantity_data = QuantityAnalysisData(
            file_path='test.xlsx',
            timestamp='2025-01-01T00:00:00',
            sheets=[
                SheetData(
                    sheet_name='Invoice',
                    header_font=FontInfo(name='Times New Roman', size=12.0),
                    data_font=FontInfo(name='Times New Roman', size=12.0),
                    start_row=21,
                    header_positions=[
                        HeaderPosition(keyword='Mark & N°', row=20, column=1),
                        HeaderPosition(keyword='P.O. N°', row=20, column=2),
                        HeaderPosition(keyword='ITEM N°', row=20, column=3),
                        HeaderPosition(keyword='Description', row=20, column=4),
                        HeaderPosition(keyword='Quantity', row=20, column=5),
                        HeaderPosition(keyword='Unit price (USD)', row=20, column=6),
                        HeaderPosition(keyword='Amount (USD)', row=20, column=7)
                    ]
                ),
                SheetData(
                    sheet_name='Contract',
                    header_font=FontInfo(name='Times New Roman', size=10.0),
                    data_font=FontInfo(name='Times New Roman', size=10.0),
                    start_row=18,
                    header_positions=[
                        HeaderPosition(keyword='Cargo Descprition', row=17, column=1),
                        HeaderPosition(keyword='HL ITEM', row=17, column=2),
                        HeaderPosition(keyword='Quantity', row=17, column=3),
                        HeaderPosition(keyword='Unit', row=17, column=4),
                        HeaderPosition(keyword='FCA\nSVAY RIENG', row=17, column=5),
                        HeaderPosition(keyword='Amount', row=17, column=6)
                    ]
                ),
                SheetData(
                    sheet_name='Packing list',
                    header_font=FontInfo(name='Times New Roman', size=12.0),
                    data_font=FontInfo(name='Times New Roman', size=12.0),
                    start_row=22,
                    header_positions=[
                        HeaderPosition(keyword='Mark & N°', row=20, column=1),
                        HeaderPosition(keyword='P.O N°', row=20, column=2),
                        HeaderPosition(keyword='ITEM N°', row=20, column=3),
                        HeaderPosition(keyword='Description', row=20, column=4),
                        HeaderPosition(keyword='Quantity', row=20, column=5),
                        HeaderPosition(keyword='N.W (kgs)', row=20, column=7),
                        HeaderPosition(keyword='G.W (kgs)', row=20, column=8),
                        HeaderPosition(keyword='CBM', row=20, column=9),
                        HeaderPosition(keyword='PCS', row=21, column=5),
                        HeaderPosition(keyword='SF', row=21, column=6)
                    ]
                )
            ]
        )
    
    def test_update_start_rows_success(self):
        """Test successful start_row updates."""
        result = self.updater.update_start_rows(self.sample_template, self.sample_quantity_data)
        
        # Verify start_row values are updated correctly
        assert result['data_mapping']['Invoice']['start_row'] == 21
        assert result['data_mapping']['Contract']['start_row'] == 18
        assert result['data_mapping']['Packing list']['start_row'] == 22
        
        # Verify original template is not modified
        assert self.sample_template['data_mapping']['Invoice']['start_row'] == 20
        assert self.sample_template['data_mapping']['Contract']['start_row'] == 15
        assert self.sample_template['data_mapping']['Packing list']['start_row'] == 19
    
    def test_update_start_rows_preserves_other_fields(self):
        """Test that start_row updates preserve all other sheet configuration fields."""
        result = self.updater.update_start_rows(self.sample_template, self.sample_quantity_data)
        
        # Verify header_to_write is preserved
        invoice_headers = result['data_mapping']['Invoice']['header_to_write']
        original_headers = self.sample_template['data_mapping']['Invoice']['header_to_write']
        
        assert len(invoice_headers) == len(original_headers)
        assert invoice_headers[0]['text'] == 'Mark & Nº'
        assert invoice_headers[0]['id'] == 'col_static'
        assert invoice_headers[0]['rowspan'] == 1
    
    def test_update_column_positions_success(self):
        """Test successful column position updates."""
        result = self.updater.update_column_positions(self.sample_template, self.sample_quantity_data)
        
        # Check Invoice sheet column positions (convert from 1-based to 0-based)
        invoice_headers = result['data_mapping']['Invoice']['header_to_write']
        
        # Find specific headers and check their column positions
        mark_header = next(h for h in invoice_headers if h['text'] == 'Mark & Nº')
        assert mark_header['col'] == 0  # column 1 -> 0-based index 0
        
        po_header = next(h for h in invoice_headers if h['text'] == 'P.O. Nº')
        assert po_header['col'] == 1  # column 2 -> 0-based index 1
        
        desc_header = next(h for h in invoice_headers if h['text'] == 'Description')
        assert desc_header['col'] == 3  # column 4 -> 0-based index 3
    
    def test_update_column_positions_preserves_spans(self):
        """Test that column position updates preserve rowspan/colspan attributes."""
        result = self.updater.update_column_positions(self.sample_template, self.sample_quantity_data)
        
        # Check Packing list multi-row headers
        packing_headers = result['data_mapping']['Packing list']['header_to_write']
        
        # Find headers with spans
        static_header = next(h for h in packing_headers if h['text'] == 'Mark & Nº')
        assert static_header['rowspan'] == 2  # Preserved
        
        quantity_header = next(h for h in packing_headers if h['text'] == 'Quantity')
        assert quantity_header['colspan'] == 2  # Preserved
        
        # Check sub-headers maintain their row positioning
        pcs_header = next(h for h in packing_headers if h['text'] == 'PCS')
        assert pcs_header['row'] == 1  # Preserved row: 1 positioning
        
        sf_header = next(h for h in packing_headers if h['text'] == 'SF')
        assert sf_header['row'] == 1  # Preserved row: 1 positioning
    
    def test_update_positions_combined(self):
        """Test combined update of both start_row and column positions."""
        result = self.updater.update_positions(self.sample_template, self.sample_quantity_data)
        
        # Verify both start_row and column positions are updated
        assert result['data_mapping']['Invoice']['start_row'] == 21
        assert result['data_mapping']['Contract']['start_row'] == 18
        assert result['data_mapping']['Packing list']['start_row'] == 22
        
        # Verify column positions are also updated
        invoice_headers = result['data_mapping']['Invoice']['header_to_write']
        mark_header = next(h for h in invoice_headers if h['text'] == 'Mark & Nº')
        assert mark_header['col'] == 0
    
    def test_normalize_header_text(self):
        """Test header text normalization for better matching."""
        # Test various normalizations
        assert self.updater._normalize_header_text('Mark & Nº') == 'mark and n°'
        assert self.updater._normalize_header_text('P.O. N°') == 'po n°'
        assert self.updater._normalize_header_text('Unit price\n(USD)') == 'unit price (usd)'
        assert self.updater._normalize_header_text('FCA\nSVAY RIENG') == 'fca svay rieng'
    
    def test_update_start_rows_invalid_template(self):
        """Test error handling for invalid template."""
        from config_generator.position_updater import PositionUpdaterError
        with pytest.raises(PositionUpdaterError, match="Template must be a dictionary"):
            self.updater.update_start_rows("invalid", self.sample_quantity_data)
    
    def test_update_start_rows_invalid_quantity_data(self):
        """Test error handling for invalid quantity data."""
        from config_generator.position_updater import PositionUpdaterError
        with pytest.raises(PositionUpdaterError, match="Quantity data must be QuantityAnalysisData instance"):
            self.updater.update_start_rows(self.sample_template, "invalid")
    
    def test_update_column_positions_invalid_template(self):
        """Test error handling for invalid template."""
        from config_generator.position_updater import PositionUpdaterError
        with pytest.raises(PositionUpdaterError, match="Template must be a dictionary"):
            self.updater.update_column_positions("invalid", self.sample_quantity_data)
    
    def test_update_column_positions_invalid_quantity_data(self):
        """Test error handling for invalid quantity data."""
        from config_generator.position_updater import PositionUpdaterError
        with pytest.raises(PositionUpdaterError, match="Quantity data must be QuantityAnalysisData instance"):
            self.updater.update_column_positions(self.sample_template, "invalid")
    
    def test_update_start_rows_missing_sheet(self):
        """Test handling of sheets not present in template."""
        # Add a sheet that doesn't exist in template
        extra_sheet_data = QuantityAnalysisData(
            file_path='test.xlsx',
            timestamp='2025-01-01T00:00:00',
            sheets=[
                SheetData(
                    sheet_name='NonExistent',
                    header_font=FontInfo(name='Arial', size=10.0),
                    data_font=FontInfo(name='Arial', size=10.0),
                    start_row=25,
                    header_positions=[]
                )
            ]
        )
        
        # Should not raise error, just skip the missing sheet
        result = self.updater.update_start_rows(self.sample_template, extra_sheet_data)
        
        # Original values should be preserved
        assert result['data_mapping']['Invoice']['start_row'] == 20
        assert result['data_mapping']['Contract']['start_row'] == 15
        assert result['data_mapping']['Packing list']['start_row'] == 19
    
    def test_update_column_positions_no_matching_headers(self):
        """Test column position updates when no headers match."""
        # Create quantity data with completely different header names
        different_headers_data = QuantityAnalysisData(
            file_path='test.xlsx',
            timestamp='2025-01-01T00:00:00',
            sheets=[
                SheetData(
                    sheet_name='Invoice',
                    header_font=FontInfo(name='Times New Roman', size=12.0),
                    data_font=FontInfo(name='Times New Roman', size=12.0),
                    start_row=21,
                    header_positions=[
                        HeaderPosition(keyword='Unknown Header 1', row=20, column=1),
                        HeaderPosition(keyword='Unknown Header 2', row=20, column=2)
                    ]
                )
            ]
        )
        
        result = self.updater.update_column_positions(self.sample_template, different_headers_data)
        
        # Column positions should remain unchanged
        invoice_headers = result['data_mapping']['Invoice']['header_to_write']
        mark_header = next(h for h in invoice_headers if h['text'] == 'Mark & Nº')
        assert mark_header['col'] == 0  # Original position preserved
    
    def test_update_column_positions_case_insensitive_matching(self):
        """Test that column position updates work with case-insensitive matching."""
        # Create quantity data with different case
        case_different_data = QuantityAnalysisData(
            file_path='test.xlsx',
            timestamp='2025-01-01T00:00:00',
            sheets=[
                SheetData(
                    sheet_name='Invoice',
                    header_font=FontInfo(name='Times New Roman', size=12.0),
                    data_font=FontInfo(name='Times New Roman', size=12.0),
                    start_row=21,
                    header_positions=[
                        HeaderPosition(keyword='MARK & N°', row=20, column=3),  # Different case and position
                        HeaderPosition(keyword='description', row=20, column=5)  # Different case and position
                    ]
                )
            ]
        )
        
        result = self.updater.update_column_positions(self.sample_template, case_different_data)
        
        # Should match despite case differences
        invoice_headers = result['data_mapping']['Invoice']['header_to_write']
        mark_header = next(h for h in invoice_headers if h['text'] == 'Mark & Nº')
        assert mark_header['col'] == 2  # column 3 -> 0-based index 2
        
        desc_header = next(h for h in invoice_headers if h['text'] == 'Description')
        assert desc_header['col'] == 4  # column 5 -> 0-based index 4
    
    def test_template_not_modified(self):
        """Test that original template is never modified."""
        original_template = copy.deepcopy(self.sample_template)
        
        # Perform all update operations
        self.updater.update_start_rows(self.sample_template, self.sample_quantity_data)
        self.updater.update_column_positions(self.sample_template, self.sample_quantity_data)
        self.updater.update_positions(self.sample_template, self.sample_quantity_data)
        
        # Original template should be unchanged
        assert self.sample_template == original_template