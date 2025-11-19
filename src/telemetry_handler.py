"""
Telemetry Handler Module
Manages JSON storage for F1 telemetry data
"""

import json
import os
import pandas as pd
from datetime import datetime


class TelemetryHandler:
    """Handles JSON storage and retrieval of telemetry data"""
    
    def __init__(self, telemetry_dir='telemetry_data'):
        """Initialize telemetry handler"""
        if not os.path.isabs(telemetry_dir):
            telemetry_dir = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), 
                telemetry_dir
            )
        self.telemetry_dir = telemetry_dir
        os.makedirs(self.telemetry_dir, exist_ok=True)
    
    def save_telemetry(self, year, event, driver, session_type, telemetry_df):
        """Save telemetry data to JSON file"""
        try:
            # Create year/event directory structure
            event_dir = os.path.join(self.telemetry_dir, str(year), event, session_type)
            os.makedirs(event_dir, exist_ok=True)
            
            # Convert DataFrame to JSON
            filename = f"{driver}_{session_type}_telemetry.json"
            filepath = os.path.join(event_dir, filename)
            
            # Convert telemetry to dictionary
            telemetry_dict = {
                'metadata': {
                    'year': year,
                    'event': event,
                    'driver': driver,
                    'session_type': session_type,
                    'saved_at': datetime.now().isoformat()
                },
                'telemetry': telemetry_df.to_dict(orient='records')
            }
            
            with open(filepath, 'w') as f:
                json.dump(telemetry_dict, f, indent=2, default=str)
            
            print(f"✓ Saved telemetry: {filepath}")
            return filepath
        
        except Exception as e:
            print(f"Error saving telemetry: {e}")
            return None
    
    def load_telemetry(self, year, event, driver, session_type):
        """Load telemetry data from JSON file"""
        try:
            filename = f"{driver}_{session_type}_telemetry.json"
            filepath = os.path.join(
                self.telemetry_dir, str(year), event, session_type, filename
            )
            
            if not os.path.exists(filepath):
                print(f"Telemetry file not found: {filepath}")
                return None
            
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            # Convert back to DataFrame
            telemetry_df = pd.DataFrame(data['telemetry'])
            return telemetry_df, data['metadata']
        
        except Exception as e:
            print(f"Error loading telemetry: {e}")
            return None, None
    
    def save_lap_data(self, year, event, session_type, laps_df):
        """Save lap data to JSON file"""
        try:
            event_dir = os.path.join(self.telemetry_dir, str(year), event, session_type)
            os.makedirs(event_dir, exist_ok=True)
            
            filename = f"lap_data_{session_type}.json"
            filepath = os.path.join(event_dir, filename)
            
            lap_dict = {
                'metadata': {
                    'year': year,
                    'event': event,
                    'session_type': session_type,
                    'saved_at': datetime.now().isoformat()
                },
                'laps': laps_df.to_dict(orient='records')
            }
            
            with open(filepath, 'w') as f:
                json.dump(lap_dict, f, indent=2, default=str)
            
            print(f"✓ Saved lap data: {filepath}")
            return filepath
        
        except Exception as e:
            print(f"Error saving lap data: {e}")
            return None
    
    def load_lap_data(self, year, event, session_type):
        """Load lap data from JSON file"""
        try:
            filename = f"lap_data_{session_type}.json"
            filepath = os.path.join(
                self.telemetry_dir, str(year), event, session_type, filename
            )
            
            if not os.path.exists(filepath):
                print(f"Lap data file not found: {filepath}")
                return None
            
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            laps_df = pd.DataFrame(data['laps'])
            return laps_df, data['metadata']
        
        except Exception as e:
            print(f"Error loading lap data: {e}")
            return None, None
    
    def list_available_telemetry(self):
        """List all available telemetry files"""
        telemetry_files = []
        
        for root, dirs, files in os.walk(self.telemetry_dir):
            for file in files:
                if file.endswith('.json'):
                    filepath = os.path.join(root, file)
                    rel_path = os.path.relpath(filepath, self.telemetry_dir)
                    telemetry_files.append(rel_path)
        
        return telemetry_files
    
    def get_telemetry_summary(self):
        """Get summary of stored telemetry data"""
        files = self.list_available_telemetry()
        
        summary = {
            'total_files': len(files),
            'by_year': {},
            'by_session': {}
        }
        
        for file in files:
            parts = file.split(os.sep)
            if len(parts) >= 3:
                year = parts[0]
                session = parts[2] if len(parts) > 2 else 'unknown'
                
                summary['by_year'][year] = summary['by_year'].get(year, 0) + 1
                summary['by_session'][session] = summary['by_session'].get(session, 0) + 1
        
        return summary


def main():
    """Main function to demonstrate telemetry handling"""
    handler = TelemetryHandler()
    
    print("\nTelemetry Handler")
    print("=" * 50)
    print(f"Telemetry directory: {handler.telemetry_dir}")
    
    # Example: Create sample telemetry data
    sample_telemetry = pd.DataFrame({
        'Time': [0.0, 0.1, 0.2, 0.3],
        'Speed': [250, 260, 270, 280],
        'Throttle': [100, 100, 100, 100],
        'Brake': [0, 0, 0, 0]
    })
    
    handler.save_telemetry(2024, 'Bahrain', 'VER', 'R', sample_telemetry)
    
    # List available telemetry
    files = handler.list_available_telemetry()
    print(f"\nAvailable telemetry files: {len(files)}")
    for file in files[:5]:
        print(f"  - {file}")
    
    # Get summary
    summary = handler.get_telemetry_summary()
    print(f"\nTelemetry Summary:")
    print(f"  Total files: {summary['total_files']}")
    print(f"  By year: {summary['by_year']}")
    print(f"  By session: {summary['by_session']}")


if __name__ == "__main__":
    main()
