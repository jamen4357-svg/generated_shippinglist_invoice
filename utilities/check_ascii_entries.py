import sqlite3
conn = sqlite3.connect('data/user_database.db')
cursor = conn.cursor()
cursor.execute('SELECT target_invoice_ref, target_invoice_no, timestamp, activity_type FROM business_activities WHERE target_invoice_ref LIKE "%,%" ORDER BY timestamp DESC LIMIT 10')
results = cursor.fetchall()
conn.close()
if results:
    print('Entries with comma-separated values (potential ASCII codes):')
    for ref, no, ts, act_type in results:
        print(f'{ts}: ref="{ref}" no="{no}" type={act_type}')
else:
    print('No entries with comma-separated values found')
    
# Also check for any unusual entries
conn = sqlite3.connect('data/user_database.db')
cursor = conn.cursor()
cursor.execute('SELECT target_invoice_ref, target_invoice_no, timestamp, activity_type FROM business_activities WHERE LENGTH(target_invoice_ref) > 20 ORDER BY timestamp DESC LIMIT 10')
results = cursor.fetchall()
conn.close()
if results:
    print('\nEntries with unusually long references:')
    for ref, no, ts, act_type in results:
        print(f'{ts}: ref="{ref}" no="{no}" type={act_type}')
else:
    print('No unusually long references found')