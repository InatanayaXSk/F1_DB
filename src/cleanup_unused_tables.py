"""
Cleanup Unused Database Tables
Remove sprint_results table and optionally make features_json nullable
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))
from database import F1Database


def check_sprint_usage():
    """Check if sprint_results table has any data"""
    db = F1Database()
    
    print("=== Checking Sprint Results Usage ===\n")
    
    # Check if table exists and has data
    result = db.execute_query("SELECT COUNT(*) as count FROM sprint_results")
    count = result.iloc[0]['count']
    
    print(f"Sprint results count: {count}")
    
    if count == 0:
        print("✓ Sprint results table is empty - safe to remove")
        return True
    else:
        print(f"⚠ Warning: Found {count} sprint results - removal not recommended")
        return False


def remove_sprint_table():
    """Remove sprint_results table"""
    db = F1Database()
    conn = db.connect()
    cursor = conn.cursor()
    
    print("\n=== Removing Sprint Results Table ===\n")
    
    try:
        cursor.execute("DROP TABLE IF EXISTS sprint_results CASCADE")
        conn.commit()
        print("✓ Sprint results table removed successfully")
    except Exception as e:
        print(f"✗ Error removing sprint table: {e}")
        conn.rollback()
    finally:
        db.close()


def make_features_nullable():
    """Make features_json and shap_values_json columns nullable if they aren't already"""
    db = F1Database()
    conn = db.connect()
    cursor = conn.cursor()
    
    print("\n=== Updating Predictions Table ===\n")
    
    try:
        # Make features_json nullable (it might already be)
        cursor.execute("""
            ALTER TABLE predictions 
            ALTER COLUMN features_json DROP NOT NULL
        """)
        print("✓ Made features_json nullable")
        
        cursor.execute("""
            ALTER TABLE predictions 
            ALTER COLUMN shap_values_json DROP NOT NULL
        """)
        print("✓ Made shap_values_json nullable")
        
        conn.commit()
    except Exception as e:
        # If columns are already nullable, this will error - that's OK
        print(f"  Note: {e}")
        conn.rollback()
    finally:
        db.close()


def update_empty_features():
    """Update empty {} features to NULL for cleaner database"""
    db = F1Database()
    conn = db.connect()
    cursor = conn.cursor()
    
    print("\n=== Cleaning Up Empty Features ===\n")
    
    try:
        # Convert empty dict {} to NULL
        cursor.execute("""
            UPDATE predictions 
            SET features_json = NULL 
            WHERE features_json = '{}'
        """)
        
        updated = cursor.rowcount
        conn.commit()
        print(f"✓ Cleaned {updated} empty features_json values")
        
    except Exception as e:
        print(f"✗ Error cleaning features: {e}")
        conn.rollback()
    finally:
        db.close()


def show_table_info():
    """Show information about all tables"""
    db = F1Database()
    
    print("\n=== Database Table Information ===\n")
    
    tables = [
        'drivers', 'teams', 'races', 'qualifying_results', 
        'race_results', 'predictions', 'aggregated_laps', 
        'tyre_stats', 'sessions'
    ]
    
    for table in tables:
        try:
            result = db.execute_query(f"SELECT COUNT(*) as count FROM {table}")
            count = result.iloc[0]['count']
            print(f"  {table:25s} {count:>6} rows")
        except Exception as e:
            print(f"  {table:25s} [Table doesn't exist]")


if __name__ == "__main__":
    print("=" * 60)
    print("Database Cleanup Utility")
    print("=" * 60)
    
    # Show current state
    show_table_info()
    
    # Check sprint usage
    can_remove_sprint = check_sprint_usage()
    
    if can_remove_sprint:
        print("\n" + "=" * 60)
        response = input("Remove sprint_results table? (y/n): ")
        if response.lower() == 'y':
            remove_sprint_table()
    
    # Make features nullable
    print("\n" + "=" * 60)
    response = input("Make features_json and shap_values_json nullable? (y/n): ")
    if response.lower() == 'y':
        make_features_nullable()
    
    # Clean empty features
    print("\n" + "=" * 60)
    response = input("Convert empty {} features to NULL for cleaner database? (y/n): ")
    if response.lower() == 'y':
        update_empty_features()
    
    # Show final state
    show_table_info()
    
    print("\n✓ Cleanup completed!")
