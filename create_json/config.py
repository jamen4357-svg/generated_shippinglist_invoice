# --- START OF FULL FILE: config.py ---

# --- File Configuration ---
INPUT_EXCEL_FILE = "JF.xlsx" # Or specific name for this format, e.g., "JF_Data_2024.xlsx"
# Specify sheet name, or None to use the active sheet
SHEET_NAME = None
# OUTPUT_PICKLE_FILE = "invoice_data.pkl" # Example for future use

# --- Sheet Parsing Configuration ---
# Row/Column range to search for the header
# Adjusted to a more realistic range to improve performance and avoid matching stray text.
HEADER_SEARCH_ROW_RANGE = (1, 20)
HEADER_SEARCH_COL_RANGE = (1, 30) # Increased range slightly, adjust if many columns
# A pattern (string or regex) to identify a cell within the header row
# This pattern helps find *any* header row, the mapping below specifies exact matches
HEADER_IDENTIFICATION_PATTERN = r"^(批次号|订单号|物料代码|总张数|净重|毛重|po|item|pcs|net|gross|TTX编号)$" # Broadened slightly


EXPECTED_HEADER_DATA_TYPES = {
    'po': ['string', 'numeric'],
    'item': ['string'], # Production Order is always a string that matches the pattern
    'description': ['string'],
    'pcs': ['numeric'],
    'net': ['numeric'],
    'gross': ['numeric'],
    'unit': ['numeric'],
    'amount': ['numeric'],
    'sqft': ['numeric'],
    'cbm': ['numeric', 'string'], # CBM can be a number or a string like '1*2*3'
    'dc': ['string'],
    'batch_no': ['string'],
    'line_no': ['string'],
    'direction': ['string'],
    'production_date': ['string'],
    'production_order_no': ['string'],
    'reference_code': ['string'],
    'level': ['string'],
    'pallet_count': ['numeric', 'string'],
    'manual_no': ['string'],
    'remarks': ['string'],
    'inv_no': ['string'],
    'inv_date': ['string', 'numeric', 'date'], # Invoice date can be a string or numeric date
    'inv_ref': ['string'],
}

# --- Column Mapping Configuration ---
# Canonical Name -> List containing header variations (case-insensitive match)
TARGET_HEADERS_MAP = {
    # priority first
    "production_order_no": ["production order number", "生产单号", "po", "入库单号", "PO", "PO NO.", "订单号", "TTX编号"], # Primary English: 'production order number', Primary Chinese: '生产单号'
    "unit": ["unit price", "单价", "price", "unit", "USD", "usd", "单价USD", "价格", "单价 USD"],          # Primary English: 'unit price', Primary Chinese: '单价'
    # --- Core Logic Canonical Names ---
    "po": ["PO NO.", "po", "PO", "Po", "订单号", "order number", "order no", "Po Nb", "尺数", "PO NB", "Po Nb", "客户订单号", "订单号"],                 # Primary English: 'po', Primary Chinese: '订单号'
    "item": ["物料代码","item no", "ITEM NO.",  'item', "Item No", "ITEM NO", "Item No", "客户品名", "物料编码", "产品编号"],        # Primary English: 'item no', Primary Chinese: '物料代码'
    "pcs": ["pcs", "总张数", "张数", "PCS"],                # Primary English: 'pcs', Primary Chinese: '总张数'
    "net": ["NW", "net weight", "净重kg", "净重", "net", "净重KG"],          # Primary English: 'net weight', Primary Chinese: '净重'
    "gross": ["GW", "gross weight", "毛重", "gross", "Gross", "gross weight", "Gross Weight", "毛重量KG", "重量KG", "重量", "毛重", "毛重KG"],       # Primary English: 'gross weight', Primary Chinese: '毛重'
    "sqft": ["sqft", "出货数量 (sf)", "尺数", "SF", "出货数量(sf)", "出货数量(SF)", "出货数量 SF", "尺码", "出货数量（SF）"],      # Primary English: 'sqft', Primary Chinese: '出货数量 (sf)' (Assuming this specific text)
    "amount": ["金额 USD","金额USD", "金额", "USD","amount", "总价", "usd", "Amount", "Total Amount", "total", "total amount"],            # Primary English: 'amount', Primary Chinese: '金额' # Ensure this is present and mapped

    # --- Less Certain Canonical Names ---
    "date_recipt": ["入库时间", "入库日期", "date receipt", "Date Receipt", "date receipt", "Date Receipt", "date receipt"],
    "cbm": ["cbm", "材积", "CBM","remarks", "备注", "Remark", 'remark', '低', "REMARKS", "REMARK"],          # Primary English: 'remarks', Primary Chinese: '备注'
    "description": ["description","产品名称", "品名规格", "描述", "desc", "DESCRIPTION"],      # Primary English: 'description', Primary Chinese: '品名规格'
    "inv_no": ["invoice no", "发票号码", "INV NO", "INV NO", "inv no", "INV NO", "inv no", "INVOICE NO"],    # Primary English: 'invoice no', Primary Chinese: '发票号码'
    "inv_date": ["invoice date", "发票日期", "INV DATE", "INV DATE", "inv date", "INV DATE", "inv date", "INVOICE DATE", "invoice date"], # Primary English: 'invoice date', Primary Chinese: '发票日期'
    "inv_ref": ["ref", "invoice ref", "ref no", "REF NO", "REF NO", "ref no", "inv ref", "INV REF", "INVOICE REF"],

    "remarks": ["cbm", "材积", "CBM", "remarks", "备注", "Remark", 'remark', '低', "REMARKS", "REMARK"],          # Primary English: 'remarks', Primary Chinese: '备注'
    # --- Other Found Headers ---
    "dc": ["批次号", "DC", "dc"],
    "batch_no": ["batch number", "批次号"],  # Primary English: 'batch number', Primary Chinese: '批次号'
    "line_no": ["line no", "行号"],           # Primary English: 'line no', Primary Chinese: '行号'
    "direction": ["direction", "内向"],      # Primary English: 'direction', Primary Chinese: '内向' (Meaning still unclear)
    "production_date": ["production date", "生产日期"], # Primary English: 'production date', Primary Chinese: '生产日期'
    "reference_code": ["reference code", "ttx编号", "生产名称"], # Primary English: 'reference code', Primary Chinese: 'ttx编号' (Verify 'ttx编号')
    "level": ["grade", "等级"],              # Primary English: 'grade', Primary Chinese: '等级'
    "pallet_count": ["pallet count", "拖数", "PALLET", "件数", "PALLET COUNT", "pallet count", "托数"],# Primary English: 'pallet count', Primary Chinese: '拖数'
    "manual_no": ["manual number", "手册号"], # Primary English: 'manual number', Primary Chinese: '手册号'
    # 'amount' is already defined above

    # Add any other essential headers here following the variations list format
}

# --- Header Validation Configuration ---
EXPECTED_HEADER_PATTERNS = {
    'production_order_no': [
        r'^(25|26|27)\d{5}-\d{2}$',
    ],
    'cbm': [
        r'^\d+(\.\d+)?\*\d+(\.\d+)?\*\d+(\.\d+)?$'
    ],
    # This pattern is now a fallback for the specific value check below
    'pallet_count': [
        r'^1$'
    ],
    'remarks': [r'^\D+$'],  # Non-numeric characters only
}

EXPECTED_HEADER_VALUES = {
    # If a column header maps to 'pallet_count', the data value below it MUST be 1.
    # Otherwise, the column will be ignored for the 'pallet_count' mapping.
    'pallet_count': [1]
}

HEADERLESS_COLUMN_PATTERNS = {
    # If an empty header cell has data below it that looks like "number*number*number",
    # map it as the 'cbm' column.
    'cbm': [
        r'^\d+(\.\d+)?\*\d+(\.\d+)?\*\d+(\.\d+)?$',
    ],


    # You can add other rules here in the future, for example:
    # 'serial_no': [r'^[A-Z]{3}-\d{5}$']
}



# --- Data Extraction Configuration ---
# Choose a column likely to be empty *only* when the data rows truly end.
# 'item' is often a good candidate if item codes are always present for data rows.
STOP_EXTRACTION_ON_EMPTY_COLUMN = 'item'
# Safety limit for the number of data rows to read below the header within a table
MAX_DATA_ROWS_TO_SCAN = 1000

# --- Data Processing Configuration ---
# List of canonical header names for columns where values should be distributed
# CBM processing/distribution depends on the 'cbm' mapping above and if the column contains L*W*H strings
COLUMNS_TO_DISTRIBUTE = ["net", "gross", "cbm"] # Include 'cbm' if you want to distribute calculated CBM values

# The canonical header name of the column used for proportional distribution
DISTRIBUTION_BASIS_COLUMN = "pcs"

# --- Aggregation Strategy Configuration ---
# List or Tuple of *workbook filename* prefixes (case-sensitive) that trigger CUSTOM aggregation.
# Custom aggregation sums 'sqft' and 'amount' based ONLY on 'po' and 'item'.
# Standard aggregation sums 'sqft' based on 'po', 'item', and 'unit'.
# Example: If INPUT_EXCEL_FILE is "JF_Report_Q1.xlsx", it will match "JF".
CUSTOM_AGGREGATION_WORKBOOK_PREFIXES = () # Renamed Variable


# --- END OF FULL FILE: config.py ---