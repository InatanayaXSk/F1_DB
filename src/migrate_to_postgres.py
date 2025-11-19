"""
Database Migration Script
Migrates data from SQLite to PostgreSQL
"""

import os
import sys
from datetime import datetime

# Add src to path
sys.path.append(os.path.dirname(__file__))

from database import F1Database
from database_enhanced import F1DatabaseEnhanced
from config import Config


def migrate_sqlite_to_postgres(sqlite_db_path='f1_data.db', verbose=True):
    """
    Migrate all data from SQLite to PostgreSQL
    
    Args:
        sqlite_db_path: Path to SQLite database file
        verbose: Print progress messages
    """
    if verbose:
        print("=" * 60)
        print("SQLite to PostgreSQL Migration")
        print("=" * 60)
        print(f"\nSource: SQLite ({sqlite_db_path})")
        print(f"Target: PostgreSQL ({Config.POSTGRES_HOST}:{Config.POSTGRES_PORT}/{Config.POSTGRES_DB})")
        print()
    
    # Check if SQLite database exists
    if not os.path.isabs(sqlite_db_path):
        sqlite_db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), sqlite_db_path)
    
    if not os.path.exists(sqlite_db_path):
        print(f"❌ Error: SQLite database not found at {sqlite_db_path}")
        return False
    
    try:
        # Initialize both databases
        if verbose:
            print("Initializing databases...")
        
        sqlite_db = F1Database(sqlite_db_path)
        
        # Temporarily set DB_TYPE to postgresql for target
        original_db_type = Config.DB_TYPE
        Config.DB_TYPE = 'postgresql'
        postgres_db = F1DatabaseEnhanced()
        Config.DB_TYPE = original_db_type
        
        # Get all table names from SQLite
        tables_to_migrate = [
            'drivers', 'teams', 'races', 'qualifying_results', 
            'sprint_results', 'race_results', 'predictions',
            'aggregated_laps', 'tyre_stats', 'sessions'
        ]
        
        total_rows_migrated = 0
        
        for table in tables_to_migrate:
            if verbose:
                print(f"\nMigrating table: {table}...")
            
            try:
                # Read data from SQLite
                conn = sqlite_db.connect()
                df = conn.execute(f"SELECT * FROM {table}").fetchall()
                
                # Get column names
                columns = [description[0] for description in conn.description]
                
                if df:
                    # Insert into PostgreSQL
                    session = postgres_db.get_session()
                    
                    for row in df:
                        row_dict = dict(zip(columns, row))
                        
                        # Map to SQLAlchemy model
                        if table == 'drivers':
                            from database_enhanced import Driver
                            obj = Driver(**row_dict)
                        elif table == 'teams':
                            from database_enhanced import Team
                            obj = Team(**row_dict)
                        elif table == 'races':
                            from database_enhanced import Race
                            obj = Race(**row_dict)
                        elif table == 'qualifying_results':
                            from database_enhanced import QualifyingResult
                            obj = QualifyingResult(**row_dict)
                        elif table == 'sprint_results':
                            from database_enhanced import SprintResult
                            obj = SprintResult(**row_dict)
                        elif table == 'race_results':
                            from database_enhanced import RaceResult
                            obj = RaceResult(**row_dict)
                        elif table == 'predictions':
                            from database_enhanced import Prediction
                            obj = Prediction(**row_dict)
                        elif table == 'aggregated_laps':
                            from database_enhanced import AggregatedLap
                            obj = AggregatedLap(**row_dict)
                        elif table == 'tyre_stats':
                            from database_enhanced import TyreStat
                            obj = TyreStat(**row_dict)
                        elif table == 'sessions':
                            from database_enhanced import Session
                            obj = Session(**row_dict)
                        else:
                            continue
                        
                        session.merge(obj)
                    
                    session.commit()
                    session.close()
                    
                    row_count = len(df)
                    total_rows_migrated += row_count
                    if verbose:
                        print(f"  ✓ Migrated {row_count} rows")
                else:
                    if verbose:
                        print(f"  ℹ No data found (empty table)")
                
                sqlite_db.close()
                
            except Exception as e:
                print(f"  ❌ Error migrating {table}: {e}")
                continue
        
        if verbose:
            print("\n" + "=" * 60)
            print(f"Migration completed!")
            print(f"Total rows migrated: {total_rows_migrated}")
            print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_migration(sqlite_db_path='f1_data.db'):
    """
    Verify migration by comparing row counts between SQLite and PostgreSQL
    """
    print("\n" + "=" * 60)
    print("Verifying Migration")
    print("=" * 60)
    
    try:
        # Initialize databases
        if not os.path.isabs(sqlite_db_path):
            sqlite_db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), sqlite_db_path)
        
        sqlite_db = F1Database(sqlite_db_path)
        
        original_db_type = Config.DB_TYPE
        Config.DB_TYPE = 'postgresql'
        postgres_db = F1DatabaseEnhanced()
        Config.DB_TYPE = original_db_type
        
        tables = [
            'drivers', 'teams', 'races', 'qualifying_results',
            'sprint_results', 'race_results', 'predictions',
            'aggregated_laps', 'tyre_stats', 'sessions'
        ]
        
        all_match = True
        
        print(f"\n{'Table':<20} {'SQLite':<15} {'PostgreSQL':<15} {'Status':<10}")
        print("-" * 60)
        
        for table in tables:
            try:
                # Count rows in SQLite
                conn = sqlite_db.connect()
                sqlite_count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                sqlite_db.close()
                
                # Count rows in PostgreSQL
                postgres_count = postgres_db.execute_query(f"SELECT COUNT(*) FROM {table}").iloc[0, 0]
                
                status = "✓ OK" if sqlite_count == postgres_count else "✗ MISMATCH"
                if sqlite_count != postgres_count:
                    all_match = False
                
                print(f"{table:<20} {sqlite_count:<15} {postgres_count:<15} {status:<10}")
                
            except Exception as e:
                print(f"{table:<20} {'ERROR':<15} {'ERROR':<15} {'✗ ERROR':<10}")
                all_match = False
        
        print("\n" + "=" * 60)
        if all_match:
            print("✓ Verification passed! All tables match.")
        else:
            print("⚠ Verification found mismatches. Please review.")
        print("=" * 60)
        
        return all_match
        
    except Exception as e:
        print(f"\n❌ Verification failed: {e}")
        return False


def main():
    """Main migration script"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Migrate F1 database from SQLite to PostgreSQL')
    parser.add_argument('--sqlite-path', default='f1_data.db', help='Path to SQLite database')
    parser.add_argument('--verify-only', action='store_true', help='Only verify migration, do not migrate')
    parser.add_argument('--quiet', action='store_true', help='Suppress verbose output')
    
    args = parser.parse_args()
    
    if Config.DB_TYPE != 'postgresql':
        print("⚠ Warning: DB_TYPE is not set to 'postgresql' in environment.")
        print("  Set DB_TYPE=postgresql in .env file or environment variables.")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            return
    
    if args.verify_only:
        verify_migration(args.sqlite_path)
    else:
        success = migrate_sqlite_to_postgres(args.sqlite_path, verbose=not args.quiet)
        if success:
            print("\n" + "=" * 60)
            print("Running verification...")
            verify_migration(args.sqlite_path)


if __name__ == "__main__":
    main()
