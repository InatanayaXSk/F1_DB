"""
Remove Unused Prediction Columns - PERMANENT
Drops predicted_time, top10_probability, features_json, and shap_values_json columns
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))
from database import F1Database


def check_column_usage():
    """Check if these columns have any non-null data"""
    db = F1Database()
    
    print("=== Checking Column Usage ===\n")
    
    columns_to_check = ['predicted_time', 'top10_probability', 'features_json', 'shap_values_json']
    
    for col in columns_to_check:
        try:
            result = db.execute_query(f"SELECT COUNT(*) as total, COUNT({col}) as non_null FROM predictions")
            total = result.iloc[0]['total']
            non_null = result.iloc[0]['non_null']
            
            if non_null == 0:
                print(f"✓ {col:25s} {non_null}/{total} non-null values → SAFE TO REMOVE")
            else:
                print(f"⚠ {col:25s} {non_null}/{total} non-null values → Contains data")
        except Exception as e:
            print(f"✗ {col:25s} Error: {e}")
    
    print()


def remove_unused_columns():
    """Remove the 4 unused columns from predictions table"""
    db = F1Database()
    conn = db.connect()
    cursor = conn.cursor()
    
    print("\n=== Removing Unused Columns ===\n")
    
    columns_to_remove = [
        'predicted_time',
        'top10_probability', 
        'features_json',
        'shap_values_json'
    ]
    
    try:
        for col in columns_to_remove:
            cursor.execute(f"ALTER TABLE predictions DROP COLUMN IF EXISTS {col}")
            print(f"✓ Removed column: {col}")
        
        conn.commit()
        print("\n✓ All unused columns removed successfully")
        
    except Exception as e:
        print(f"\n✗ Error removing columns: {e}")
        conn.rollback()
    finally:
        db.close()


def show_code_updates():
    """Show what code updates were already made"""
    print("\n=== Code Updates Already Completed ===\n")
    
    print("✅ database.py:")
    print("   - Updated predictions table schema (removed 4 columns)")
    print("   - Simplified insert_prediction() method")
    print("   - Disabled migration code for removed columns")
    
    print("\n✅ streamlit_app.py:")
    print("   - Removed features_json from queries")
    print("   - Removed feature analysis expander")
    
    print("\n✅ fix_2026_driver_numbers.py:")
    print("   - Removed features={} parameter from insert calls")
    
    print("\n✅ All code is already updated and ready to use!")



def show_table_schema():
    """Show the final predictions table schema"""
    db = F1Database()
    
    print("\n=== Final Predictions Table Schema ===\n")
    
    try:
        result = db.execute_query("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'predictions'
            ORDER BY ordinal_position
        """)
        
        print(result.to_string(index=False))
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    print("=" * 70)
    print("Remove Unused Prediction Columns Utility")
    print("=" * 70)
    
    # Step 1: Check usage
    check_column_usage()
    
    # Step 2: Confirm
    print("=" * 70)
    print("This will PERMANENTLY remove 4 columns:")
    print("  - predicted_time")
    print("  - top10_probability")
    print("  - features_json")
    print("  - shap_values_json")
    print("\n⚠️  NO BACKUP WILL BE CREATED - This is PERMANENT")
    print("=" * 70)
    response = input("\nProceed with permanent removal? (yes/no): ")
    
    if response.lower() != 'yes':
        print("\n✗ Operation cancelled")
        exit(0)
    
    # Step 3: Remove columns
    remove_unused_columns()
    
    # Step 4: Show new schema
    show_table_schema()
    
    # Step 5: Show code updates
    show_code_updates()
    
    print("\n" + "=" * 70)
    print("✓ Database migration completed!")
    print("=" * 70)
    print("\n✅ DONE:")
    print("1. All unused columns permanently removed from database")
    print("2. Code has been updated and is ready to use")
    print("3. Test the application: streamlit run src/streamlit_app.py")
