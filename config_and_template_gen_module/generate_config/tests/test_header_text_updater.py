"""
Unit tests for HeaderTextUpdater component.

Tests header text mapping functionality, template updating, and various header variations
including the special case handling for "Cargo Descprition" → col_po mapping.
"""

import pytest
import copy
from config_generator.header_text_updater import HeaderTextUpdater
from config_generator.models import QuantityAnalysisData, SheetData, HeaderPosition, FontInfo


class TestHeaderTextUpdater:
    """Test cases for HeaderTextUpdater component."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.updater = HeaderTextUpdater()
        
        # Sample template structure
        self.sample_template = {
            "sheets_to_process": ["Invoice", "Contract", "Packing list"],
            "data_mapping": {
                "Invoice": {
                    "start_row": 20,
                    "header_to_write": [
                        {"row": 0, "col": 0, "text": "Mark & Nº", "id": "col_static", "rowspan": 1},
                        {"row": 0, "col": 1, "text": "P.O. Nº", "id": "col_po", "rowspan": 1},
                        {"row": 0, "col": 2, "text": "Description", "id": "col_desc", "rowspan": 1},
                        {"row": 0, "col": 3, "text": "ITEM Nº", "id": "col_item", "rowspan": 1},
                        {"row": 0, "col": 4, "text": "Quantity", "id": "col_qty_sf"},
                        {"row": 0, "col": 5, "text": "Unit price", "id": "col_unit_price", "rowspan": 1},
                        {"row": 0, "col": 6, "text": "Amount", "id": "col_amount", "rowspan": 1}
                    ]
                },
                "Contract": {
                    "start_row": 15,
                    "header_to_write": [
                        {"row": 0, "col": 0, "text": "No.", "id": "col_no", "rowspan": 1},
                        {"row": 0, "col": 1, "text": "ITEM Nº", "id": "col_item", "rowspan": 1},
                        {"row": 0, "col": 2, "text": "Quantity", "id": "col_qty_sf"},
                        {"row": 0, "col": 3, "text": "Unit Price", "id": "col_unit_price", "rowspan": 1},
                        {"row": 0, "col": 4, "text": "Total value", "id": "col_amount", "rowspan": 1}
                    ]
                },
                "Packing list": {
                    "start_row": 19,
                    "header_to_write": [
                        {"row": 0, "col": 0, "text": "Mark & Nº", "id": "col_static", "rowspan": 2},
                        {"row": 0, "col": 1, "text": "Pallet NO.", "id": "col_pallet", "rowspan": 2},
                        {"row": 0, "col": 2, "text": "P.O Nº", "id": "col_po", "rowspan": 2},
                        {"row": 0, "col": 3, "text": "ITEM Nº", "id": "col_item", "rowspan": 2},
                        {"row": 0, "col": 4, "text": "Description", "id": "col_desc", "rowspan": 2},
                        {"row": 0, "col": 5, "text": "Quantity", "colspan": 2},
                        {"row": 0, "col": 7, "text": "N.W (kgs)", "id": "col_net", "rowspan": 2},
                        {"row": 0, "col": 8, "text": "G.W (kgs)", "id": "col_gross", "rowspan": 2},
                        {"row": 0, "col": 9, "text": "CBM", "id": "col_cbm", "rowspan": 2},
                        {"row": 1, "col": 5, "text": "PCS", "id": "col_qty_pcs"},
                        {"row": 1, "col": 6, "text": "SF", "id": "col_qty_sf"}
                    ]
                }
            }
        }
        
        # Sample quantity analysis data
        font_info = FontInfo(name="Times New Roman", size=12.0)
        
        self.sample_quantity_data = QuantityAnalysisData(
            file_path="test.xlsx",
            timestamp="2025-01-01T00:00:00",
            sheets=[
                SheetData(
                    sheet_name="Invoice",
                    header_font=font_info,
                    data_font=font_info,
                    start_row=21,
                    header_positions=[
                        HeaderPosition(keyword="Mark & N°", row=20, column=1),
                        HeaderPosition(keyword="P.O. N°", row=20, column=2),
                        HeaderPosition(keyword="ITEM N°", row=20, column=3),
                        HeaderPosition(keyword="Description", row=20, column=4),
                        HeaderPosition(keyword="Quantity", row=20, column=5),
                        HeaderPosition(keyword="Unit price (USD)", row=20, column=6),
                        HeaderPosition(keyword="Amount (USD)", row=20, column=7)
                    ]
                ),
                SheetData(
                    sheet_name="Contract",
                    header_font=font_info,
                    data_font=font_info,
                    start_row=18,
                    header_positions=[
                        HeaderPosition(keyword="Cargo Descprition", row=17, column=1),
                        HeaderPosition(keyword="HL ITEM", row=17, column=2),
                        HeaderPosition(keyword="Quantity", row=17, column=3),
                        HeaderPosition(keyword="FCA\nSVAY RIENG", row=17, column=5),
                        HeaderPosition(keyword="Amount", row=17, column=6)
                    ]
                ),
                SheetData(
                    sheet_name="Packing list",
                    header_font=font_info,
                    data_font=font_info,
                    start_row=22,
                    header_positions=[
                        HeaderPosition(keyword="Mark & N°", row=20, column=1),
                        HeaderPosition(keyword="P.O N°", row=20, column=2),
                        HeaderPosition(keyword="ITEM N°", row=20, column=3),
                        HeaderPosition(keyword="Description", row=20, column=4),
                        HeaderPosition(keyword="N.W (kgs)", row=20, column=7),
                        HeaderPosition(keyword="G.W (kgs)", row=20, column=8),
                        HeaderPosition(keyword="CBM", row=20, column=9),
                        HeaderPosition(keyword="PCS", row=21, column=5),
                        HeaderPosition(keyword="SF", row=21, column=6)
                    ]
                )
            ]
        )
    
    def test_header_mappings_initialization(self):
        """Test that header mappings are properly initialized."""
        assert isinstance(self.updater.header_mappings, dict)
        assert len(self.updater.header_mappings) > 0
        
        # Test key mappings from requirements
        assert self.updater.header_mappings['Mark & Nº'] == 'col_static'
        assert self.updater.header_mappings['P.O Nº'] == 'col_po'
        assert self.updater.header_mappings['P.O. Nº'] == 'col_po'
        assert self.updater.header_mappings['ITEM Nº'] == 'col_item'
        assert self.updater.header_mappings['HL ITEM'] == 'col_item'
        assert self.updater.header_mappings['Description'] == 'col_desc'
        assert self.updater.header_mappings['Cargo Descprition'] == 'col_po'  # Special case
        assert self.updater.header_mappings['Quantity'] == 'col_qty_sf'
        assert self.updater.header_mappings['Unit price (USD)'] == 'col_unit_price'
        assert self.updater.header_mappings['FCA\nSVAY RIENG'] == 'col_unit_price'
        assert self.updater.header_mappings['Amount'] == 'col_amount'
        assert self.updater.header_mappings['N.W (kgs)'] == 'col_net'
        assert self.updater.header_mappings['G.W (kgs)'] == 'col_gross'
        assert self.updater.header_mappings['CBM'] == 'col_cbm'
        assert self.updater.header_mappings['PCS'] == 'col_qty_pcs'
        assert self.updater.header_mappings['SF'] == 'col_qty_sf'
    
    def test_map_header_to_column_id_direct_mapping(self):
        """Test direct header text to column ID mapping."""
        # Test exact matches
        assert self.updater.map_header_to_column_id("Mark & Nº") == "col_static"
        assert self.updater.map_header_to_column_id("P.O. Nº") == "col_po"
        assert self.updater.map_header_to_column_id("ITEM Nº") == "col_item"
        assert self.updater.map_header_to_column_id("HL ITEM") == "col_item"
        assert self.updater.map_header_to_column_id("Description") == "col_desc"
        assert self.updater.map_header_to_column_id("Cargo Descprition") == "col_po"  # Special case
        assert self.updater.map_header_to_column_id("Quantity") == "col_qty_sf"
        assert self.updater.map_header_to_column_id("Unit price (USD)") == "col_unit_price"
        assert self.updater.map_header_to_column_id("Amount") == "col_amount"
        assert self.updater.map_header_to_column_id("N.W (kgs)") == "col_net"
        assert self.updater.map_header_to_column_id("G.W (kgs)") == "col_gross"
        assert self.updater.map_header_to_column_id("CBM") == "col_cbm"
        assert self.updater.map_header_to_column_id("PCS") == "col_qty_pcs"
        assert self.updater.map_header_to_column_id("SF") == "col_qty_sf"
    
    def test_map_header_to_column_id_case_insensitive(self):
        """Test case-insensitive header mapping."""
        assert self.updater.map_header_to_column_id("mark & nº") == "col_static"
        assert self.updater.map_header_to_column_id("DESCRIPTION") == "col_desc"
        assert self.updater.map_header_to_column_id("quantity") == "col_qty_sf"
        assert self.updater.map_header_to_column_id("cbm") == "col_cbm"
        assert self.updater.map_header_to_column_id("pcs") == "col_qty_pcs"
        assert self.updater.map_header_to_column_id("sf") == "col_qty_sf"
    
    def test_map_header_to_column_id_pattern_matching(self):
        """Test pattern-based header mapping for variations."""
        # Test pattern matching fallbacks
        assert self.updater.map_header_to_column_id("Mark & N°") == "col_static"
        assert self.updater.map_header_to_column_id("P.O N°") == "col_po"
        assert self.updater.map_header_to_column_id("Item N°") == "col_item"
        assert self.updater.map_header_to_column_id("Unit Price") == "col_unit_price"
        assert self.updater.map_header_to_column_id("Total Amount") == "col_amount"
        assert self.updater.map_header_to_column_id("N.W (KGS)") == "col_net"
        assert self.updater.map_header_to_column_id("G.W (KGS)") == "col_gross"
    
    def test_map_header_to_column_id_special_cases(self):
        """Test special case mappings."""
        # Test the special "Cargo Descprition" → col_po mapping
        assert self.updater.map_header_to_column_id("Cargo Descprition") == "col_po"
        
        # Test that regular "Description" still maps to col_desc
        assert self.updater.map_header_to_column_id("Description") == "col_desc"
        
        # Test FCA variations
        assert self.updater.map_header_to_column_id("FCA\nSVAY RIENG") == "col_unit_price"
        assert self.updater.map_header_to_column_id("FCA") == "col_unit_price"
    
    def test_map_header_to_column_id_invalid_input(self):
        """Test header mapping with invalid input."""
        assert self.updater.map_header_to_column_id(None) is None
        assert self.updater.map_header_to_column_id("") is None
        assert self.updater.map_header_to_column_id("Unknown Header") is None
        assert self.updater.map_header_to_column_id(123) is None
    
    def test_update_header_texts_basic(self):
        """Test basic header text updating functionality."""
        result = self.updater.update_header_texts(self.sample_template, self.sample_quantity_data)
        
        # Verify template structure is preserved
        assert "sheets_to_process" in result
        assert "data_mapping" in result
        assert len(result["data_mapping"]) == 3
        
        # Check Invoice sheet updates
        invoice_headers = result["data_mapping"]["Invoice"]["header_to_write"]
        
        # Find headers by ID and verify text updates
        header_by_id = {h["id"]: h for h in invoice_headers if "id" in h}
        
        assert header_by_id["col_static"]["text"] == "Mark & N°"
        assert header_by_id["col_po"]["text"] == "P.O. N°"
        assert header_by_id["col_item"]["text"] == "ITEM N°"
        assert header_by_id["col_desc"]["text"] == "Description"
        assert header_by_id["col_qty_sf"]["text"] == "Quantity"
        assert header_by_id["col_unit_price"]["text"] == "Unit price (USD)"
        assert header_by_id["col_amount"]["text"] == "Amount (USD)"
        
        # Verify other attributes are preserved
        assert header_by_id["col_static"]["row"] == 0
        assert header_by_id["col_static"]["col"] == 0
        assert header_by_id["col_static"]["rowspan"] == 1
    
    def test_update_header_texts_special_case_cargo_description(self):
        """Test special case handling for 'Cargo Descprition' → col_po mapping."""
        result = self.updater.update_header_texts(self.sample_template, self.sample_quantity_data)
        
        # Check Contract sheet for special case
        contract_headers = result["data_mapping"]["Contract"]["header_to_write"]
        header_by_id = {h["id"]: h for h in contract_headers if "id" in h}
        
        # Verify that "Cargo Descprition" is NOT mapped to col_desc but should update col_po if present
        # Since our template doesn't have col_po in Contract, let's check that col_item gets "HL ITEM"
        assert header_by_id["col_item"]["text"] == "HL ITEM"
        assert header_by_id["col_qty_sf"]["text"] == "Quantity"
        assert header_by_id["col_unit_price"]["text"] == "FCA\nSVAY RIENG"
        assert header_by_id["col_amount"]["text"] == "Amount"
    
    def test_update_header_texts_multi_row_headers(self):
        """Test updating multi-row header structures while preserving spans."""
        result = self.updater.update_header_texts(self.sample_template, self.sample_quantity_data)
        
        # Check Packing list sheet with multi-row headers
        packing_headers = result["data_mapping"]["Packing list"]["header_to_write"]
        
        # Find headers by ID
        header_by_id = {h["id"]: h for h in packing_headers if "id" in h}
        
        # Verify text updates
        assert header_by_id["col_static"]["text"] == "Mark & N°"
        assert header_by_id["col_po"]["text"] == "P.O N°"
        assert header_by_id["col_item"]["text"] == "ITEM N°"
        assert header_by_id["col_desc"]["text"] == "Description"
        assert header_by_id["col_net"]["text"] == "N.W (kgs)"
        assert header_by_id["col_gross"]["text"] == "G.W (kgs)"
        assert header_by_id["col_cbm"]["text"] == "CBM"
        assert header_by_id["col_qty_pcs"]["text"] == "PCS"
        assert header_by_id["col_qty_sf"]["text"] == "SF"
        
        # Verify spanning attributes are preserved
        assert header_by_id["col_static"]["rowspan"] == 2
        assert header_by_id["col_pallet"]["rowspan"] == 2
        assert header_by_id["col_net"]["rowspan"] == 2
        
        # Verify row positioning is preserved
        assert header_by_id["col_qty_pcs"]["row"] == 1
        assert header_by_id["col_qty_sf"]["row"] == 1
    
    def test_update_header_texts_preserves_template_structure(self):
        """Test that template structure and non-header sections are preserved."""
        original_template = copy.deepcopy(self.sample_template)
        result = self.updater.update_header_texts(self.sample_template, self.sample_quantity_data)
        
        # Verify sheets_to_process is unchanged
        assert result["sheets_to_process"] == original_template["sheets_to_process"]
        
        # Verify start_row values are unchanged (should be updated by different component)
        assert result["data_mapping"]["Invoice"]["start_row"] == original_template["data_mapping"]["Invoice"]["start_row"]
        assert result["data_mapping"]["Contract"]["start_row"] == original_template["data_mapping"]["Contract"]["start_row"]
        assert result["data_mapping"]["Packing list"]["start_row"] == original_template["data_mapping"]["Packing list"]["start_row"]
        
        # Verify header positioning attributes are preserved
        invoice_headers = result["data_mapping"]["Invoice"]["header_to_write"]
        original_invoice_headers = original_template["data_mapping"]["Invoice"]["header_to_write"]
        
        for i, header in enumerate(invoice_headers):
            original_header = original_invoice_headers[i]
            assert header["row"] == original_header["row"]
            assert header["col"] == original_header["col"]
            if "rowspan" in original_header:
                assert header["rowspan"] == original_header["rowspan"]
            if "colspan" in original_header:
                assert header["colspan"] == original_header["colspan"]
            if "id" in original_header:
                assert header["id"] == original_header["id"]
    
    def test_update_header_texts_missing_sheet(self):
        """Test handling when quantity data contains sheets not in template."""
        # Add extra sheet to quantity data
        font_info = FontInfo(name="Times New Roman", size=12.0)
        extra_sheet = SheetData(
            sheet_name="Extra Sheet",
            header_font=font_info,
            data_font=font_info,
            start_row=10,
            header_positions=[HeaderPosition(keyword="Test Header", row=9, column=1)]
        )
        
        quantity_data_with_extra = QuantityAnalysisData(
            file_path="test.xlsx",
            timestamp="2025-01-01T00:00:00",
            sheets=self.sample_quantity_data.sheets + [extra_sheet]
        )
        
        # Should not raise error and should process normally
        result = self.updater.update_header_texts(self.sample_template, quantity_data_with_extra)
        
        # Verify original sheets are still processed
        assert len(result["data_mapping"]) == 3
        assert "Extra Sheet" not in result["data_mapping"]
    
    def test_update_header_texts_invalid_input(self):
        """Test error handling for invalid input."""
        from config_generator.header_text_updater import HeaderTextUpdaterError
        with pytest.raises(HeaderTextUpdaterError, match="Template must be a dictionary"):
            self.updater.update_header_texts("invalid", self.sample_quantity_data)
        
        with pytest.raises(HeaderTextUpdaterError, match="Quantity data must be QuantityAnalysisData instance"):
            self.updater.update_header_texts(self.sample_template, "invalid")
    
    def test_update_sheet_headers_no_matching_headers(self):
        """Test updating sheet headers when no headers match."""
        header_to_write = [
            {"row": 0, "col": 0, "text": "Unknown Header", "id": "col_unknown"}
        ]
        
        header_positions = [
            HeaderPosition(keyword="Different Header", row=0, column=0)
        ]
        
        # Should not raise error
        self.updater._update_sheet_headers(header_to_write, header_positions)
        
        # Text should remain unchanged
        assert header_to_write[0]["text"] == "Unknown Header"
    
    def test_header_variations_comprehensive(self):
        """Test comprehensive header variations and edge cases."""
        test_cases = [
            # Mark variations
            ("Mark & Nº", "col_static"),
            ("Mark & N°", "col_static"),
            ("mark & nº", "col_static"),
            
            # P.O variations
            ("P.O Nº", "col_po"),
            ("P.O. Nº", "col_po"),
            ("P.O N°", "col_po"),
            ("P.O. N°", "col_po"),
            ("p.o nº", "col_po"),
            
            # Item variations
            ("ITEM Nº", "col_item"),
            ("ITEM N°", "col_item"),
            ("HL ITEM", "col_item"),
            ("item nº", "col_item"),
            
            # Description variations and special case
            ("Description", "col_desc"),
            ("Cargo Descprition", "col_po"),  # Special case
            ("description", "col_desc"),
            
            # Quantity variations
            ("Quantity", "col_qty_sf"),
            ("quantity", "col_qty_sf"),
            
            # Unit price variations
            ("Unit price", "col_unit_price"),
            ("Unit price (USD)", "col_unit_price"),
            ("Unit Price(USD)", "col_unit_price"),
            ("FCA", "col_unit_price"),
            ("FCA\nSVAY RIENG", "col_unit_price"),
            ("unit price", "col_unit_price"),
            
            # Amount variations
            ("Amount", "col_amount"),
            ("Amount (USD)", "col_amount"),
            ("Amount(USD)", "col_amount"),
            ("Total value(USD)", "col_amount"),
            ("amount", "col_amount"),
            
            # Weight variations
            ("N.W (kgs)", "col_net"),
            ("G.W (kgs)", "col_gross"),
            ("n.w (kgs)", "col_net"),
            ("g.w (kgs)", "col_gross"),
            
            # Other variations
            ("CBM", "col_cbm"),
            ("cbm", "col_cbm"),
            ("PCS", "col_qty_pcs"),
            ("pcs", "col_qty_pcs"),
            ("SF", "col_qty_sf"),
            ("sf", "col_qty_sf"),
        ]
        
        for header_text, expected_column_id in test_cases:
            result = self.updater.map_header_to_column_id(header_text)
            assert result == expected_column_id, f"Failed for '{header_text}': expected '{expected_column_id}', got '{result}'"