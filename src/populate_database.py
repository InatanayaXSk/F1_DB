"""
Populate Database with FastF1 Data
Extracts cached data from Redis and populates PostgreSQL database
"""

import fastf1
import sys
import os
from datetime import datetime

# Add src to path
sys.path.append(os.path.dirname(__file__))
from database import F1Database
from data_fetcher import F1DataFetcher

# Initialize fetcher with Redis
fetcher = F1DataFetcher(use_redis=True)


def populate_drivers_and_teams(db, year):
    """Populate drivers and teams for a given year"""
    print(f"\n=== Processing {year} season ===")
    
    try:
        schedule = fetcher.fetch_season_schedule(year)
        
        # Get first race with qualifying to extract driver info
        for idx, event in schedule.iterrows():
            event_name = event['EventName']
            
            try:
                print(f"Loading {event_name} qualifying...")
                session = fetcher.fetch_session_data(year, event_name, 'Q')
                
                # Extract driver information
                results = session.results
                
                if results is not None and len(results) > 0:
                    print(f"Found {len(results)} drivers")
                    
                    for _, driver in results.iterrows():
                        driver_number = driver.get('DriverNumber')
                        abbreviation = driver.get('Abbreviation')
                        full_name = driver.get('FullName', driver.get('BroadcastName', abbreviation))
                        team_name = driver.get('TeamName')
                        
                        if driver_number and team_name:
                            # Insert driver
                            db.insert_driver(
                                driver_number=int(driver_number),
                                abbreviation=str(abbreviation),
                                full_name=str(full_name),
                                team_name=str(team_name),
                                year=year
                            )
                            
                            # Insert team
                            db.insert_team(str(team_name), year)
                    
                    print(f"✓ Populated drivers and teams from {event_name}")
                    break  # Only need one race to get all drivers
                    
            except Exception as e:
                print(f"  Skipping {event_name}: {e}")
                continue
        
    except Exception as e:
        print(f"Error processing {year}: {e}")


def populate_races(db, year):
    """Populate race calendar for a given year"""
    print(f"\n=== Populating races for {year} ===")
    
    try:
        schedule = fetcher.fetch_season_schedule(year)
        
        for idx, event in schedule.iterrows():
            event_name = event['EventName']
            country = event.get('Country', 'Unknown')
            location = event.get('Location', 'Unknown')
            event_date = event.get('EventDate')
            round_number = event.get('RoundNumber', idx + 1)
            
            race_id = db.insert_race(
                year=year,
                round_number=int(round_number),
                event_name=str(event_name),
                country=str(country),
                location=str(location),
                event_date=str(event_date)
            )
            
            if race_id:
                print(f"✓ Added race: {event_name}")
        
    except Exception as e:
        print(f"Error populating races for {year}: {e}")


def populate_results(db, year):
    """Populate race and qualifying results"""
    print(f"\n=== Populating results for {year} ===")
    
    try:
        schedule = fetcher.fetch_season_schedule(year)
        
        for idx, event in schedule.iterrows():
            event_name = event['EventName']
            
            # Get race_id
            race_query = f"SELECT race_id FROM races WHERE year={year} AND event_name='{event_name}'"
            race_result = db.execute_query(race_query)
            
            if len(race_result) == 0:
                continue
                
            race_id = race_result.iloc[0]['race_id']
            
            # Qualifying results
            try:
                print(f"Loading {event_name} qualifying results...")
                quali_session = fetcher.fetch_session_data(year, event_name, 'Q')
                quali_results = quali_session.results if quali_session else None
                
                if quali_results is not None and len(quali_results) > 0:
                    for _, driver in quali_results.iterrows():
                        db.insert_qualifying_result(
                            race_id=race_id,
                            driver_number=int(driver.get('DriverNumber', 0)),
                            position=int(driver.get('Position', 0)) if driver.get('Position') else 0,
                            q1=driver.get('Q1', ''),
                            q2=driver.get('Q2', ''),
                            q3=driver.get('Q3', '')
                        )
                    print(f"  ✓ Added qualifying results")
            except Exception as e:
                print(f"  Skipping qualifying: {e}")
            
            # Race results
            try:
                print(f"Loading {event_name} race results...")
                race_session = fetcher.fetch_session_data(year, event_name, 'R')
                race_results = race_session.results if race_session else None
                
                if race_results is not None and len(race_results) > 0:
                    for _, driver in race_results.iterrows():
                        db.insert_race_result(
                            race_id=race_id,
                            driver_number=int(driver.get('DriverNumber', 0)),
                            position=int(driver.get('Position', 0)) if driver.get('Position') else 0,
                            points=float(driver.get('Points', 0)),
                            grid_position=int(driver.get('GridPosition', 0)) if driver.get('GridPosition') else 0,
                            status=str(driver.get('Status', 'Unknown')),
                            fastest_lap=driver.get('FastestLap', '')
                        )
                    print(f"  ✓ Added race results")
            except Exception as e:
                print(f"  Skipping race: {e}")
    
    except Exception as e:
        print(f"Error populating results for {year}: {e}")


def main():
    """Main function to populate database"""
    print("=" * 60)
    print("F1 Database Population Script")
    print("=" * 60)
    
    db = F1Database()
    
    # Populate for 2023-2025
    for year in [2023, 2024, 2025]:
        populate_drivers_and_teams(db, year)
        populate_races(db, year)
        populate_results(db, year)
    
    print("\n" + "=" * 60)
    print("✓ Database population complete!")
    print("=" * 60)
    
    # Show summary
    drivers_count = db.execute_query("SELECT COUNT(*) as count FROM drivers").iloc[0]['count']
    teams_count = db.execute_query("SELECT COUNT(*) as count FROM teams").iloc[0]['count']
    races_count = db.execute_query("SELECT COUNT(*) as count FROM races").iloc[0]['count']
    
    print(f"\nDatabase Summary:")
    print(f"  Drivers: {drivers_count}")
    print(f"  Teams: {teams_count}")
    print(f"  Races: {races_count}")


if __name__ == "__main__":
    main()
