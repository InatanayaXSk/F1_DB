"""
Fix 2026 Driver Numbers and Populate Database
Assigns correct driver numbers for 2026 season and populates drivers table
"""

import pandas as pd
import sys
import os
sys.path.append(os.path.dirname(__file__))
from database import F1Database

# Define 2026 driver lineup with correct numbers
DRIVERS_2026 = [
    # Red Bull Racing
    {'driver_number': 1, 'full_name': 'Max Verstappen', 'abbreviation': 'VER', 'team_name': 'Red Bull / Oracle Red Bull'},
    {'driver_number': 6, 'full_name': 'Isack Hadjar', 'abbreviation': 'HAD', 'team_name': 'Red Bull / Oracle Red Bull'},
    
    # Racing Bulls (AlphaTauri)
    {'driver_number': 30, 'full_name': 'Liam Lawson', 'abbreviation': 'LAW', 'team_name': 'Racing Bulls'},
    {'driver_number': 12, 'full_name': 'Arvid Lindblad', 'abbreviation': 'LIN', 'team_name': 'Racing Bulls'},
    
    # Mercedes
    {'driver_number': 63, 'full_name': 'George Russell', 'abbreviation': 'RUS', 'team_name': 'Mercedes'},
    {'driver_number': 17, 'full_name': 'Kimi Antonelli', 'abbreviation': 'ANT', 'team_name': 'Mercedes'},
    
    # Ferrari
    {'driver_number': 16, 'full_name': 'Charles Leclerc', 'abbreviation': 'LEC', 'team_name': 'Ferrari'},
    {'driver_number': 44, 'full_name': 'Lewis Hamilton', 'abbreviation': 'HAM', 'team_name': 'Ferrari'},
    
    # McLaren
    {'driver_number': 4, 'full_name': 'Lando Norris', 'abbreviation': 'NOR', 'team_name': 'McLaren'},
    {'driver_number': 81, 'full_name': 'Oscar Piastri', 'abbreviation': 'PIA', 'team_name': 'McLaren'},
    
    # Alpine
    {'driver_number': 10, 'full_name': 'Pierre Gasly', 'abbreviation': 'GAS', 'team_name': 'Alpine'},
    {'driver_number': 43, 'full_name': 'Franco Colapinto', 'abbreviation': 'COL', 'team_name': 'Alpine'},
    
    # Aston Martin
    {'driver_number': 14, 'full_name': 'Fernando Alonso', 'abbreviation': 'ALO', 'team_name': 'Aston Martin'},
    {'driver_number': 18, 'full_name': 'Lance Stroll', 'abbreviation': 'STR', 'team_name': 'Aston Martin'},
    
    # Haas
    {'driver_number': 31, 'full_name': 'Esteban Ocon', 'abbreviation': 'OCO', 'team_name': 'Haas / TGR-Haas'},
    {'driver_number': 87, 'full_name': 'Oliver Bearman', 'abbreviation': 'BEA', 'team_name': 'Haas / TGR-Haas'},
    
    # Williams
    {'driver_number': 55, 'full_name': 'Carlos Sainz', 'abbreviation': 'SAI', 'team_name': 'Williams'},
    {'driver_number': 23, 'full_name': 'Alex Albon', 'abbreviation': 'ALB', 'team_name': 'Williams'},
    
    # Audi/Sauber
    {'driver_number': 50, 'full_name': 'Gabriel Bortoleto', 'abbreviation': 'BOR', 'team_name': 'Audi / Sauber'},
    {'driver_number': 27, 'full_name': 'Nico Hülkenberg', 'abbreviation': 'HUL', 'team_name': 'Audi / Sauber'},
    
    # Cadillac
    {'driver_number': 11, 'full_name': 'Sergio Pérez', 'abbreviation': 'PER', 'team_name': 'Cadillac'},
    {'driver_number': 77, 'full_name': 'Valtteri Bottas', 'abbreviation': 'BOT', 'team_name': 'Cadillac'},
]


def populate_2026_drivers():
    """Populate 2026 driver data in database"""
    db = F1Database()
    
    print("=== Populating 2026 Driver Data ===\n")
    
    for driver in DRIVERS_2026:
        try:
            db.insert_driver(
                driver_number=driver['driver_number'],
                abbreviation=driver['abbreviation'],
                full_name=driver['full_name'],
                team_name=driver['team_name'],
                year=2026
            )
            print(f"✓ Added: #{driver['driver_number']:2d} {driver['full_name']:20s} ({driver['team_name']})")
        except Exception as e:
            print(f"✗ Error adding {driver['full_name']}: {e}")
    
    print(f"\n✓ Successfully populated {len(DRIVERS_2026)} drivers for 2026 season")


def fix_csv_driver_numbers():
    """Fix the 2026 predictions CSV with correct driver numbers"""
    csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                            'models', '2026_predictions_full.csv')
    
    if not os.path.exists(csv_path):
        print(f"CSV file not found: {csv_path}")
        return
    
    print(f"\n=== Fixing CSV Driver Numbers ===\n")
    print(f"Reading: {csv_path}")
    
    df = pd.read_csv(csv_path)
    print(f"Original rows: {len(df)}")
    
    # Create mapping from driver name to correct number
    driver_number_map = {d['full_name']: d['driver_number'] for d in DRIVERS_2026}
    
    # Update driver numbers
    df['driver_number'] = df['driver_name'].map(driver_number_map)
    
    # Check for unmapped drivers
    unmapped = df[df['driver_number'].isna()]['driver_name'].unique()
    if len(unmapped) > 0:
        print(f"\n⚠ Warning: {len(unmapped)} unmapped drivers found:")
        for name in unmapped:
            print(f"  - {name}")
    
    # Remove rows with unmapped drivers
    df = df.dropna(subset=['driver_number'])
    df['driver_number'] = df['driver_number'].astype(int)
    
    print(f"Final rows: {len(df)}")
    print(f"Unique drivers: {df['driver_number'].nunique()}")
    
    # Save fixed CSV
    output_path = csv_path.replace('.csv', '_fixed.csv')
    df.to_csv(output_path, index=False)
    print(f"\n✓ Fixed CSV saved to: {output_path}")
    
    # Show driver number statistics
    print("\nDriver Number Distribution:")
    driver_counts = df.groupby(['driver_number', 'driver_name']).size().reset_index(name='predictions')
    for _, row in driver_counts.iterrows():
        print(f"  #{row['driver_number']:2d} {row['driver_name']:20s} - {row['predictions']} predictions")
    
    return df


def reload_predictions_to_database(df=None):
    """Reload predictions with correct driver numbers into database"""
    if df is None:
        csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                'models', '2026_predictions_full_fixed.csv')
        df = pd.read_csv(csv_path)
    
    print(f"\n=== Reloading Predictions to Database ===\n")
    
    db = F1Database()
    
    # Clear existing 2026 predictions
    conn = db.connect()
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM predictions 
        WHERE race_id IN (SELECT race_id FROM races WHERE year = 2026)
    """)
    conn.commit()
    print("✓ Cleared existing 2026 predictions")
    db.close()
    
    # Insert new predictions
    count = 0
    for _, row in df.iterrows():
        try:
            # Get race_id
            race_query = f"""
                SELECT race_id FROM races 
                WHERE year = 2026 AND round_number = {row['round']}
            """
            race_result = db.execute_query(race_query)
            
            if len(race_result) == 0:
                continue
            
            race_id = race_result.iloc[0]['race_id']
            
            # Insert qualifying prediction
            if pd.notna(row['quali_position']):
                db.insert_prediction(
                    race_id=race_id,
                    session_type='qualifying',
                    driver_number=int(row['driver_number']),
                    predicted_position=int(row['quali_position']),
                    confidence=float(row['quali_confidence']),
                    model_type='Legacy Ensemble (GB/RF/XGB/LGB)'
                )
            
            # Insert race prediction
            if pd.notna(row['race_position']):
                db.insert_prediction(
                    race_id=race_id,
                    session_type='race',
                    driver_number=int(row['driver_number']),
                    predicted_position=int(row['race_position']),
                    confidence=float(row['race_confidence']),
                    model_type='Legacy Ensemble (GB/RF/XGB/LGB)'
                )
            
            count += 1
            if count % 100 == 0:
                print(f"  Processed {count}/{len(df)} predictions...")
                
        except Exception as e:
            print(f"Error inserting prediction for row {count}: {e}")
            continue
    
    print(f"\n✓ Successfully reloaded {count} prediction records")


if __name__ == "__main__":
    print("=" * 60)
    print("2026 F1 Driver Numbers Fix Utility")
    print("=" * 60)
    
    # Step 1: Populate 2026 drivers table
    populate_2026_drivers()
    
    # Step 2: Fix CSV file
    fixed_df = fix_csv_driver_numbers()
    
    # Step 3: Ask if user wants to reload predictions
    print("\n" + "=" * 60)
    response = input("Reload predictions to database? (y/n): ")
    if response.lower() == 'y':
        reload_predictions_to_database(fixed_df)
    
    print("\n✓ All done!")
