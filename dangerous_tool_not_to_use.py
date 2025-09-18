#!/usr/bin/env python3
"""
Database Data Cleaner CLI

A simple CLI tool to clear all data from the application's databases
without destroying the database structure or the CLI itself.

CLEARS ALL USER LOG ACTIVITY:
- Security events (login attempts, authentication events)
- Business activities (invoice operations, user actions)
- Activity logs (if separate database exists)
- Security logs (text file)
"""

import argparse
import sqlite3
import os
import json
import shutil
from pathlib import Path
from datetime import datetime

# Database paths
USER_DB_PATH = "data/user_database.db"
ACTIVITY_LOG_PATH = "data/activity_log.db"
INVOICE_DB_PATH = "data/Invoice Record/master_invoice_data.db"
INVOICE_JSON_PATH = "data/invoice_database.json"

def clear_user_database():
    """Clear all user data but keep the database structure"""
    if not os.path.exists(USER_DB_PATH):
        print(f"❌ User database not found: {USER_DB_PATH}")
        return False

    try:
        conn = sqlite3.connect(USER_DB_PATH)
        cursor = conn.cursor()

        # Clear user data but keep structure
        cursor.execute("DELETE FROM users")
        cursor.execute("DELETE FROM registration_tokens")
        cursor.execute("DELETE FROM security_events")  # Clear security event logs
        cursor.execute("DELETE FROM business_activities")  # Clear business activity logs

        # Reset auto-increment counters
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='users'")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='registration_tokens'")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='security_events'")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='business_activities'")

        conn.commit()
        conn.close()

        print("✅ Cleared all user data (users, registration tokens, security events, and business activities)")
        return True
    except Exception as e:
        print(f"❌ Error clearing user database: {e}")
        return False

def clear_user_activity_logs():
    """Clear only user activity logs (security events and business activities) without removing users"""
    if not os.path.exists(USER_DB_PATH):
        print(f"❌ User database not found: {USER_DB_PATH}")
        return False

    try:
        conn = sqlite3.connect(USER_DB_PATH)
        cursor = conn.cursor()

        # Clear only activity logs, keep users and registration tokens
        cursor.execute("DELETE FROM security_events")
        cursor.execute("DELETE FROM business_activities")

        # Reset auto-increment counters for the cleared tables
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='security_events'")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='business_activities'")

        conn.commit()
        conn.close()

        print("✅ Cleared user activity logs (security events and business activities)")
        print("💡 Users and registration tokens preserved")
        return True
    except Exception as e:
        print(f"❌ Error clearing user activity logs: {e}")
        return False

def clear_activity_logs():
    """Clear all activity logs from both user database and separate activity log database"""
    success_count = 0

    # Clear activity logs from user database (security_events and business_activities are already cleared in clear_user_database)
    # But let's also check for a separate activity_log.db file
    if os.path.exists(ACTIVITY_LOG_PATH):
        try:
            conn = sqlite3.connect(ACTIVITY_LOG_PATH)
            cursor = conn.cursor()

            # Get all table names
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()

            # Clear all tables
            for table in tables:
                table_name = table[0]
                cursor.execute(f"DELETE FROM {table_name}")
                cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table_name}'")

            conn.commit()
            conn.close()

            print("✅ Cleared separate activity log database")
            success_count += 1
        except Exception as e:
            print(f"❌ Error clearing separate activity log database: {e}")
    else:
        print(f"ℹ️  No separate activity log database found: {ACTIVITY_LOG_PATH}")

    return success_count > 0

def clear_invoice_database():
    """Clear all invoice data"""
    success_count = 0

    # Clear SQLite invoice database
    if os.path.exists(INVOICE_DB_PATH):
        try:
            conn = sqlite3.connect(INVOICE_DB_PATH)
            cursor = conn.cursor()

            # Get all table names
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()

            # Clear all tables
            for table in tables:
                table_name = table[0]
                cursor.execute(f"DELETE FROM {table_name}")
                cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table_name}'")

            conn.commit()
            conn.close()

            print("✅ Cleared SQLite invoice database")
            success_count += 1
        except Exception as e:
            print(f"❌ Error clearing SQLite invoice database: {e}")
    else:
        print(f"⚠️  SQLite invoice database not found: {INVOICE_DB_PATH}")

    # Clear JSON invoice database
    if os.path.exists(INVOICE_JSON_PATH):
        try:
            # Create backup
            backup_path = f"{INVOICE_JSON_PATH}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy2(INVOICE_JSON_PATH, backup_path)

            # Clear the JSON file (write empty dict)
            with open(INVOICE_JSON_PATH, 'w') as f:
                json.dump({}, f, indent=2)

            print("✅ Cleared JSON invoice database")
            print(f"📁 Backup created: {backup_path}")
            success_count += 1
        except Exception as e:
            print(f"❌ Error clearing JSON invoice database: {e}")
    else:
        print(f"⚠️  JSON invoice database not found: {INVOICE_JSON_PATH}")

    return success_count > 0

def clear_data_directories():
    """Clear data from various directories"""
    directories_to_clear = [
        "data/invoices_to_process",
        "data/temp_uploads",
        "data/failed_invoices"
    ]

    success_count = 0
    for dir_path in directories_to_clear:
        if os.path.exists(dir_path):
            try:
                # Remove all files but keep directory structure
                for file_path in Path(dir_path).glob("*"):
                    if file_path.is_file():
                        file_path.unlink()
                    elif file_path.is_dir():
                        shutil.rmtree(file_path)

                print(f"✅ Cleared directory: {dir_path}")
                success_count += 1
            except Exception as e:
                print(f"❌ Error clearing directory {dir_path}: {e}")
        else:
            print(f"⚠️  Directory not found: {dir_path}")

    return success_count > 0

def clear_security_log():
    """Clear the security.log file"""
    security_log_path = "data/security.log"
    if os.path.exists(security_log_path):
        try:
            # Create backup
            backup_path = f"{security_log_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy2(security_log_path, backup_path)

            # Clear the log file
            with open(security_log_path, 'w') as f:
                f.write("")

            print("✅ Cleared security log")
            print(f"📁 Backup created: {backup_path}")
            return True
        except Exception as e:
            print(f"❌ Error clearing security log: {e}")
            return False
    else:
        print(f"⚠️  Security log not found: {security_log_path}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description="Clear database data without destroying database structure",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python clear_database_data.py --all
  python clear_database_data.py --users --logs
  python clear_database_data.py --invoices --confirm "yes i want to delete everything"
  python clear_database_data.py --all --confirm "yes i want to delete everything"
        """
    )

    parser.add_argument('--all', action='store_true',
                       help='Clear all data from all databases and directories')
    parser.add_argument('--users', action='store_true',
                       help='Clear user database (users, registration tokens, security events, business activities)')
    parser.add_argument('--activity-logs', action='store_true',
                       help='Clear only user activity logs (security events, business activities) - keeps users intact')
    parser.add_argument('--invoices', action='store_true',
                       help='Clear invoice databases (SQLite and JSON)')
    parser.add_argument('--logs', action='store_true',
                       help='Clear activity logs and security logs')
    parser.add_argument('--directories', action='store_true',
                       help='Clear data directories (invoices_to_process, temp_uploads, etc.)')
    parser.add_argument('--confirm', type=str,
                       help='Confirmation phrase required for --all or destructive operations')

    args = parser.parse_args()

    # Validate arguments
    if not any([args.all, args.users, args.activity_logs, args.invoices, args.logs, args.directories]):
        parser.error("Must specify at least one data type to clear (--all, --users, --activity-logs, --invoices, --logs, or --directories)")

    # Check confirmation for dangerous operations
    dangerous_ops = args.all or (args.users and args.invoices)
    if dangerous_ops and args.confirm != "yes i want to delete everything":
        print("❌ For safety, --all or combined --users --invoices requires confirmation:")
        print("   --confirm \"yes i want to delete everything\"")
        return 1

    print("🗑️  Database Data Cleaner")
    print("=" * 50)

    success_count = 0
    total_operations = 0

    # Execute clearing operations
    if args.all or args.users:
        total_operations += 1
        if clear_user_database():
            success_count += 1

    if args.activity_logs:
        total_operations += 1
        if clear_user_activity_logs():
            success_count += 1

    if args.all or args.logs:
        total_operations += 1
        logs_cleared = clear_activity_logs()
        logs_cleared = clear_security_log() or logs_cleared
        if logs_cleared:
            success_count += 1

    if args.all or args.invoices:
        total_operations += 1
        if clear_invoice_database():
            success_count += 1

    if args.all or args.directories:
        total_operations += 1
        if clear_data_directories():
            success_count += 1

    print("=" * 50)
    print(f"📊 Results: {success_count}/{total_operations} operations successful")

    if success_count == total_operations:
        print("✅ All requested data clearing operations completed successfully!")
        print("💡 Note: Database structures are preserved - only data was removed.")
        return 0
    else:
        print("⚠️  Some operations failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    exit(main())