"""
PostgreSQL Database Module
Manages F1 data storage in PostgreSQL database
"""

import psycopg2
import psycopg2.extras
import pandas as pd
import numpy as np
import os
from datetime import datetime
from dotenv import load_dotenv

import json

# Load environment variables from .env file
load_dotenv()


def convert_to_python_type(value):
    """Convert numpy types to Python native types for psycopg2 compatibility"""
    if value is None or pd.isna(value):
        return None
    if isinstance(value, (np.integer, np.int64, np.int32, np.int16, np.int8)):
        return int(value)
    if isinstance(value, (np.floating, np.float64, np.float32)):
        return float(value)
    if isinstance(value, np.bool_):
        return bool(value)
    if isinstance(value, np.ndarray):
        return value.tolist()
    return value


class F1Database:
    """Manages PostgreSQL database for F1 data"""
    
    def __init__(self, db_config=None):
        """Initialize database connection
        
        Args:
            db_config: Dictionary with PostgreSQL connection parameters:
                - host: Database host (default: localhost)
                - port: Database port (default: 5432)
                - database: Database name (default: f1_data)
                - user: Database user (default: postgres)
                - password: Database password (default: postgres)
        """
        if db_config is None:
            db_config = {
                'host': os.getenv('POSTGRES_HOST', 'localhost'),
                'port': os.getenv('POSTGRES_PORT', '5432'),
                'database': os.getenv('POSTGRES_DB', 'f1_data'),
                'user': os.getenv('POSTGRES_USER', 'postgres'),
                'password': os.getenv('POSTGRES_PASSWORD', 'postgres')
            }
        self.db_config = db_config
        self.conn = None
        self.initialize_database()
    
    def connect(self):
        """Create database connection"""
        self.conn = psycopg2.connect(**self.db_config)
        return self.conn
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
    
    def initialize_database(self):
        """Create database tables if they don't exist"""
        conn = self.connect()
        cursor = conn.cursor()
        
        # Drivers table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS drivers (
                driver_id SERIAL PRIMARY KEY,
                driver_number INTEGER,
                abbreviation TEXT,
                full_name TEXT,
                team_name TEXT,
                year INTEGER,
                UNIQUE(driver_number, year)
            )
        ''')
        
        # Teams table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS teams (
                team_id SERIAL PRIMARY KEY,
                team_name TEXT,
                year INTEGER,
                UNIQUE(team_name, year)
            )
        ''')
        
        # Races table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS races (
                race_id SERIAL PRIMARY KEY,
                year INTEGER,
                round_number INTEGER,
                event_name TEXT,
                country TEXT,
                location TEXT,
                event_date TEXT,
                UNIQUE(year, round_number)
            )
        ''')
        
        # Qualifying results table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS qualifying_results (
                result_id SERIAL PRIMARY KEY,
                race_id INTEGER,
                driver_number INTEGER,
                position INTEGER,
                q1_time TEXT,
                q2_time TEXT,
                q3_time TEXT,
                FOREIGN KEY (race_id) REFERENCES races(race_id)
            )
        ''')
        
        # Sprint results table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sprint_results (
                result_id SERIAL PRIMARY KEY,
                race_id INTEGER,
                driver_number INTEGER,
                position INTEGER,
                points REAL,
                status TEXT,
                FOREIGN KEY (race_id) REFERENCES races(race_id)
            )
        ''')
        
        # Race results table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS race_results (
                result_id SERIAL PRIMARY KEY,
                race_id INTEGER,
                driver_number INTEGER,
                position INTEGER,
                points REAL,
                grid_position INTEGER,
                status TEXT,
                fastest_lap_time TEXT,
                FOREIGN KEY (race_id) REFERENCES races(race_id)
            )
        ''')
        
        # Predictions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS predictions (
                prediction_id SERIAL PRIMARY KEY,
                race_id INTEGER,
                session_type TEXT,
                driver_number INTEGER,
                predicted_position INTEGER,
                confidence REAL,
                model_type TEXT,
                prediction_date TEXT,
                FOREIGN KEY (race_id) REFERENCES races(race_id)
            )
        ''')
        
        # Aggregated laps table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS aggregated_laps (
                lap_id SERIAL PRIMARY KEY,
                race_id INTEGER,
                session_type TEXT,
                driver_number INTEGER,
                lap_number INTEGER,
                lap_time REAL,
                sector1_time REAL,
                sector2_time REAL,
                sector3_time REAL,
                compound TEXT,
                tyre_life INTEGER,
                track_status TEXT,
                is_personal_best INTEGER,
                FOREIGN KEY (race_id) REFERENCES races(race_id)
            )
        ''')
        
        # Tyre stats table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tyre_stats (
                tyre_stat_id SERIAL PRIMARY KEY,
                race_id INTEGER,
                session_type TEXT,
                driver_number INTEGER,
                compound TEXT,
                total_laps INTEGER,
                avg_lap_time REAL,
                degradation_slope REAL,
                best_lap_time REAL,
                stint_number INTEGER,
                FOREIGN KEY (race_id) REFERENCES races(race_id)
            )
        ''')
        
        # Sessions table for tracking processed sessions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                session_id SERIAL PRIMARY KEY,
                race_id INTEGER,
                session_type TEXT,
                session_date TEXT,
                weather_conditions TEXT,
                track_temp REAL,
                air_temp REAL,
                UNIQUE(race_id, session_type),
                FOREIGN KEY (race_id) REFERENCES races(race_id)
            )
        ''')
        
        conn.commit()
        self.close()
        print(f"✓ Database initialized: {self.db_config['database']} on {self.db_config['host']}")
        
        # Run migrations
        self.upgrade_database()
    
    def upgrade_database(self):
        """Upgrade existing database schema with new columns (deprecated - columns removed)"""
        # Migration code removed - predicted_time, top10_probability, features_json, 
        # and shap_values_json columns have been removed from predictions table
        pass
    
    def insert_driver(self, driver_number, abbreviation, full_name, team_name, year):
        """Insert driver information (upsert on (driver_number, year))"""
        conn = self.connect()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO drivers (driver_number, abbreviation, full_name, team_name, year)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (driver_number, year)
                DO UPDATE SET
                    abbreviation = EXCLUDED.abbreviation,
                    full_name = EXCLUDED.full_name,
                    team_name = EXCLUDED.team_name
            """, (
                convert_to_python_type(driver_number),
                abbreviation,
                full_name,
                team_name,
                convert_to_python_type(year)
            ))
            conn.commit()
        except Exception as e:
            print(f"Error inserting driver: {e}")
        finally:
            self.close()
    
    def insert_team(self, team_name, year):
        """Insert team information (ignore duplicates on (team_name, year))"""
        conn = self.connect()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO teams (team_name, year)
                VALUES (%s, %s)
                ON CONFLICT (team_name, year) DO NOTHING
            """, (team_name, convert_to_python_type(year)))
            conn.commit()
        except Exception as e:
            print(f"Error inserting team: {e}")
        finally:
            self.close()
    
    def insert_race(self, year, round_number, event_name, country, location, event_date):
        """Insert race information (upsert on (year, round_number)) and return race_id"""
        conn = self.connect()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO races (year, round_number, event_name, country, location, event_date)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (year, round_number)
                DO UPDATE SET
                    event_name = EXCLUDED.event_name,
                    country = EXCLUDED.country,
                    location = EXCLUDED.location,
                    event_date = EXCLUDED.event_date
                RETURNING race_id
            """, (
                convert_to_python_type(year),
                convert_to_python_type(round_number),
                event_name,
                country,
                location,
                str(event_date)
            ))
            race_id = cursor.fetchone()[0]
            conn.commit()
            return race_id
        except Exception as e:
            print(f"Error inserting race: {e}")
            return None
        finally:
            self.close()
    
    def insert_qualifying_result(self, race_id, driver_number, position, q1, q2, q3):
        """Insert qualifying result"""
        conn = self.connect()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO qualifying_results 
                    (race_id, driver_number, position, q1_time, q2_time, q3_time)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                convert_to_python_type(race_id),
                convert_to_python_type(driver_number),
                convert_to_python_type(position),
                str(q1), str(q2), str(q3)
            ))
            conn.commit()
        except Exception as e:
            print(f"Error inserting qualifying result: {e}")
        finally:
            self.close()
    
    def insert_race_result(self, race_id, driver_number, position, points, grid_position, status, fastest_lap):
        """Insert race result"""
        conn = self.connect()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO race_results 
                    (race_id, driver_number, position, points, grid_position, status, fastest_lap_time)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                convert_to_python_type(race_id),
                convert_to_python_type(driver_number),
                convert_to_python_type(position),
                convert_to_python_type(points),
                convert_to_python_type(grid_position),
                status,
                str(fastest_lap) if fastest_lap else None
            ))
            conn.commit()
        except Exception as e:
            print(f"Error inserting race result: {e}")
        finally:
            self.close()
    
    def insert_prediction(self, race_id, session_type, driver_number, predicted_position, 
                          confidence, model_type):
        """Insert prediction result"""
        conn = self.connect()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO predictions 
                    (race_id, session_type, driver_number, predicted_position,
                     confidence, model_type, prediction_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                convert_to_python_type(race_id),
                session_type,
                convert_to_python_type(driver_number),
                convert_to_python_type(predicted_position),
                convert_to_python_type(confidence),
                model_type,
                datetime.now().isoformat()
            ))
            conn.commit()
        except Exception as e:
            print(f"Error inserting prediction: {e}")
        finally:
            self.close()
    
    def insert_aggregated_lap(self, race_id, session_type, driver_number, lap_number,
                              lap_time, sector1, sector2, sector3, compound, tyre_life,
                              track_status, is_personal_best):
        """Insert aggregated lap data"""
        conn = self.connect()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO aggregated_laps 
                    (race_id, session_type, driver_number, lap_number, lap_time,
                     sector1_time, sector2_time, sector3_time, compound, tyre_life,
                     track_status, is_personal_best)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                convert_to_python_type(race_id),
                session_type,
                convert_to_python_type(driver_number),
                convert_to_python_type(lap_number),
                convert_to_python_type(lap_time),
                convert_to_python_type(sector1),
                convert_to_python_type(sector2),
                convert_to_python_type(sector3),
                compound,
                convert_to_python_type(tyre_life),
                track_status,
                convert_to_python_type(is_personal_best)
            ))
            conn.commit()
        except Exception as e:
            print(f"Error inserting aggregated lap: {e}")
        finally:
            self.close()
    
    def insert_tyre_stat(self, race_id, session_type, driver_number, compound,
                         total_laps, avg_lap_time, degradation_slope, best_lap_time, stint_number):
        """Insert tyre statistics"""
        conn = self.connect()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO tyre_stats 
                    (race_id, session_type, driver_number, compound, total_laps,
                     avg_lap_time, degradation_slope, best_lap_time, stint_number)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                convert_to_python_type(race_id),
                session_type,
                convert_to_python_type(driver_number),
                compound,
                convert_to_python_type(total_laps),
                convert_to_python_type(avg_lap_time),
                convert_to_python_type(degradation_slope),
                convert_to_python_type(best_lap_time),
                convert_to_python_type(stint_number)
            ))
            conn.commit()
        except Exception as e:
            print(f"Error inserting tyre stat: {e}")
        finally:
            self.close()
    
    def insert_session(self, race_id, session_type, session_date, weather_conditions=None,
                       track_temp=None, air_temp=None):
        """Insert session information (upsert on (race_id, session_type)) and return session_id"""
        conn = self.connect()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO sessions 
                    (race_id, session_type, session_date, weather_conditions, track_temp, air_temp)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (race_id, session_type)
                DO UPDATE SET
                    session_date = EXCLUDED.session_date,
                    weather_conditions = EXCLUDED.weather_conditions,
                    track_temp = EXCLUDED.track_temp,
                    air_temp = EXCLUDED.air_temp
                RETURNING session_id
            """, (
                convert_to_python_type(race_id),
                session_type,
                str(session_date),
                weather_conditions,
                convert_to_python_type(track_temp),
                convert_to_python_type(air_temp)
            ))
            session_id = cursor.fetchone()[0]
            conn.commit()
            return session_id
        except Exception as e:
            print(f"Error inserting session: {e}")
            return None
        finally:
            self.close()

    def get_all_races(self):
        """Get all races from database"""
        conn = self.connect()
        df = pd.read_sql_query("SELECT * FROM races ORDER BY year DESC, round_number", conn)
        self.close()
        return df

    def get_race_results(self, race_id):
        """Get results for a specific race"""
        conn = self.connect()
        df = pd.read_sql_query(
            "SELECT * FROM race_results WHERE race_id = %s ORDER BY position",
            conn, params=(race_id,)
        )
        self.close()
        return df
    
    def get_predictions(self, race_id=None, session_type=None):
        """Get predictions, optionally filtered"""
        conn = self.connect()
        query = "SELECT * FROM predictions WHERE 1=1"
        params = []
        if race_id is not None:
            query += " AND race_id = %s"
            params.append(race_id)
        if session_type is not None:
            query += " AND session_type = %s"
            params.append(session_type)
        query += " ORDER BY predicted_position"
        df = pd.read_sql_query(query, conn, params=tuple(params) if params else None)
        self.close()
        return df
    
    def execute_query(self, query, params=None):
        """Execute custom SQL query (read-only, sanitized)"""
        ql = query.strip().lower()
        if not ql.startswith('select'):
            raise ValueError("Only SELECT queries are allowed for safety")
        conn = self.connect()
        try:
            df = pd.read_sql_query(query, conn, params=params)
            return df
        finally:
            self.close()
    
    def get_aggregated_laps(self, race_id=None, session_type=None, driver_number=None):
        """Get aggregated lap data with optional filters"""
        conn = self.connect()
        query = "SELECT * FROM aggregated_laps WHERE 1=1"
        params = []
        if race_id is not None:
            query += " AND race_id = %s"
            params.append(race_id)
        if session_type is not None:
            query += " AND session_type = %s"
            params.append(session_type)
        if driver_number is not None:
            query += " AND driver_number = %s"
            params.append(driver_number)
        query += " ORDER BY lap_number"
        df = pd.read_sql_query(query, conn, params=tuple(params) if params else None)
        self.close()
        return df
    
    def get_tyre_stats(self, race_id=None, session_type=None, driver_number=None):
        """Get tyre statistics with optional filters"""
        conn = self.connect()
        query = "SELECT * FROM tyre_stats WHERE 1=1"
        params = []
        if race_id is not None:
            query += " AND race_id = %s"
            params.append(race_id)
        if session_type is not None:
            query += " AND session_type = %s"
            params.append(session_type)
        if driver_number is not None:
            query += " AND driver_number = %s"
            params.append(driver_number)
        df = pd.read_sql_query(query, conn, params=tuple(params) if params else None)
        self.close()
        return df
    
    def get_sessions(self, race_id=None):
        """Get session information"""
        conn = self.connect()
        if race_id is not None:
            df = pd.read_sql_query("SELECT * FROM sessions WHERE race_id = %s", conn, params=(race_id,))
        else:
            df = pd.read_sql_query("SELECT * FROM sessions", conn)
        self.close()
        return df
    
    def get_table_names(self):
        """Get all table names in the database"""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name
        """)
        tables = [row[0] for row in cursor.fetchall()]
        self.close()
        return tables



def main():
    """Main function to demonstrate database operations"""
    db = F1Database()
    
    print("\nF1 Database Manager")
    print("=" * 50)
    print(f"Database: {db.db_config['database']} on {db.db_config['host']}:{db.db_config['port']}")
    
    # Example: Insert sample data
    db.insert_team("Red Bull Racing", 2024)
    db.insert_team("Ferrari", 2024)
    db.insert_team("Mercedes", 2024)
    
    print("\n✓ Sample data inserted")
    
    # Show all tables
    tables = db.get_table_names()
    
    print("\nDatabase tables:")
    for table in tables:
        print(f"  - {table}")


if __name__ == "__main__":
    main()
