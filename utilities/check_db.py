import sqlite3
import pandas as pd

conn = sqlite3.connect('data/user_database.db')
df = pd.read_sql_query('SELECT timestamp, target_invoice_ref, target_invoice_no, activity_type, description FROM business_activities ORDER BY timestamp DESC LIMIT 10', conn)
conn.close()

print('Recent database entries:')
for i, row in df.iterrows():
    ref = row['target_invoice_ref']
    no = row['target_invoice_no']
    print(f'{row["timestamp"]}: ref="{ref}" no="{no}" type={row["activity_type"]}')
    if ref and ',' in str(ref):
        print(f'  ⚠️ This looks like ASCII codes: {ref}')