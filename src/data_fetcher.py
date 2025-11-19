"""
FastF1 Data Fetcher Module
Handles downloading and caching F1 data using the FastF1 API
"""

import fastf1
import pandas as pd
import os
import json
from datetime import datetime

# Enable FastF1 cache
CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'cache')
os.makedirs(CACHE_DIR, exist_ok=True)
fastf1.Cache.enable_cache(CACHE_DIR)


class F1DataFetcher:
    """Fetches and caches F1 data from FastF1 API"""
    
    def __init__(self):
        self.cache_dir = CACHE_DIR
        
    def fetch_season_schedule(self, year):
        """Fetch the race schedule for a given season"""
        try:
            schedule = fastf1.get_event_schedule(year)
            print(f"Fetched schedule for {year} season: {len(schedule)} events")
            return schedule
        except Exception as e:
            print(f"Error fetching schedule for {year}: {e}")
            return None
    
    def fetch_session_data(self, year, event, session_type='R'):
        """
        Fetch session data for a specific event
        session_type: 'FP1', 'FP2', 'FP3', 'Q', 'S' (Sprint), 'R' (Race)
        """
        try:
            session = fastf1.get_session(year, event, session_type)
            session.load()
            print(f"Loaded {year} {event} {session_type}")
            return session
        except Exception as e:
            print(f"Error fetching session {year} {event} {session_type}: {e}")
            return None
    
    def fetch_race_results(self, year, event):
        """Fetch race results for a specific event"""
        try:
            session = self.fetch_session_data(year, event, 'R')
            if session is None:
                return None
            
            results = session.results
            return results
        except Exception as e:
            print(f"Error fetching race results for {year} {event}: {e}")
            return None
    
    def fetch_qualifying_results(self, year, event):
        """Fetch qualifying results for a specific event"""
        try:
            session = self.fetch_session_data(year, event, 'Q')
            if session is None:
                return None
            
            results = session.results
            return results
        except Exception as e:
            print(f"Error fetching qualifying results for {year} {event}: {e}")
            return None
    
    def fetch_sprint_results(self, year, event):
        """Fetch sprint results if available"""
        try:
            session = self.fetch_session_data(year, event, 'S')
            if session is None:
                return None
            
            results = session.results
            return results
        except Exception as e:
            print(f"Sprint not available for {year} {event}: {e}")
            return None
    
    def fetch_driver_lap_data(self, year, event, session_type='R'):
        """Fetch lap data for all drivers in a session"""
        try:
            session = self.fetch_session_data(year, event, session_type)
            if session is None:
                return None
            
            laps = session.laps
            return laps
        except Exception as e:
            print(f"Error fetching lap data for {year} {event} {session_type}: {e}")
            return None
    
    def fetch_telemetry_data(self, year, event, driver_number, session_type='R'):
        """Fetch telemetry data for a specific driver"""
        try:
            session = self.fetch_session_data(year, event, session_type)
            if session is None:
                return None
            
            driver_laps = session.laps.pick_driver(driver_number)
            if len(driver_laps) > 0:
                fastest_lap = driver_laps.pick_fastest()
                telemetry = fastest_lap.get_telemetry()
                return telemetry
            return None
        except Exception as e:
            print(f"Error fetching telemetry for driver {driver_number}: {e}")
            return None
    
    def cache_historical_data(self, start_year=2018, end_year=2024):
        """Cache historical F1 data for multiple seasons"""
        print(f"Caching data from {start_year} to {end_year}...")
        
        for year in range(start_year, end_year + 1):
            print(f"\n=== Caching {year} season ===")
            schedule = self.fetch_season_schedule(year)
            
            if schedule is None:
                continue
            
            # Fetch race weekends
            for idx, event in schedule.iterrows():
                event_name = event['EventName']
                print(f"\nProcessing: {event_name}")
                
                # Fetch different session types
                for session_type in ['Q', 'R']:
                    try:
                        self.fetch_session_data(year, event_name, session_type)
                    except Exception as e:
                        print(f"  Skipping {session_type}: {e}")
                
                # Try to fetch sprint if available
                try:
                    self.fetch_session_data(year, event_name, 'S')
                except:
                    pass
        
        print(f"\n✓ Caching complete! Data stored in {self.cache_dir}")


def main():
    """Main function to demonstrate data fetching"""
    fetcher = F1DataFetcher()
    
    print("F1 Data Fetcher")
    print("=" * 50)
    print("\nThis will cache historical F1 data for offline use.")
    print("This may take some time on first run...\n")
    
    # Fetch recent seasons including 2025
    fetcher.cache_historical_data(start_year=2023, end_year=2025)
    
    # Example: Fetch 2025 schedule
    schedule_2025 = fetcher.fetch_season_schedule(2025)
    if schedule_2025 is not None:
        print("\n2025 F1 Calendar:")
        print(schedule_2025[['EventName', 'EventDate', 'Country']].head(10))


if __name__ == "__main__":
    main()
