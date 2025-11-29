"""
PostgreSQL Database Module
Manages F1 data storage in PostgreSQL database
"""

import psycopg2
import psycopg2.extras
import pandas as pd
import os
from datetime import datetime
import json
import numpy as np

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
                'password': os.getenv('POSTGRES_PASSWORD', 'hdemus')
            }
        self.db_config = db_config
        self.conn = None
        psycopg2.extensions.register_adapter(np.int64, psycopg2._psycopg.AsIs) 
        psycopg2.extensions.register_adapter(np.float64, psycopg2._psycopg.AsIs)
        self.initialize_database()
    
    def connect(self):
        """Create database connection"""
        # Ensure only one connection is open, or handle a pool in a real application
        if self.conn and not self.conn.closed:
            return self.conn
        self.conn = psycopg2.connect(**self.db_config)
        return self.conn
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None # Set to None after closing
    
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
                predicted_time REAL,
                confidence REAL,
                top10_probability REAL,
                model_type TEXT,
                prediction_date TEXT,
                features_json TEXT,
                shap_values_json TEXT,
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
        """Upgrade existing database schema with new columns"""
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            # Check if predicted_time column exists in predictions table
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'predictions' AND table_schema = 'public'
            """)
            columns = [col[0] for col in cursor.fetchall()]
            
            # Add missing columns to predictions table if needed
            if 'predicted_time' not in columns:
                cursor.execute('ALTER TABLE predictions ADD COLUMN predicted_time REAL')
                print("✓ Added predicted_time column to predictions table")
            
            if 'top10_probability' not in columns:
                cursor.execute('ALTER TABLE predictions ADD COLUMN top10_probability REAL')
                print("✓ Added top10_probability column to predictions table")
            
            if 'shap_values_json' not in columns:
                cursor.execute('ALTER TABLE predictions ADD COLUMN shap_values_json TEXT')
                print("✓ Added shap_values_json column to predictions table")
            
            conn.commit()
        except Exception as e:
            print(f"Migration note: {e}")
        finally:
            self.close()
    
    def insert_driver(self, driver_number, abbreviation, full_name, team_name, year):
        """Insert driver information (uses ON CONFLICT for UPSERT)"""
        conn = self.connect()
        cursor = conn.cursor()
        try:
            # PostgreSQL equivalent of INSERT OR REPLACE is INSERT...ON CONFLICT UPDATE
            # The UNIQUE constraint is (driver_number, year)
            cursor.execute('''
                INSERT INTO drivers 
                (driver_number, abbreviation, full_name, team_name, year)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (driver_number, year) DO UPDATE 
                SET abbreviation = EXCLUDED.abbreviation, 
                    full_name = EXCLUDED.full_name, 
                    team_name = EXCLUDED.team_name;
            ''', (driver_number, abbreviation, full_name, team_name, year))
            conn.commit()
        except Exception as e:
            print(f"Error inserting driver: {e}")
        finally:
            self.close()
    
    def insert_team(self, team_name, year):
        """Insert team information (uses ON CONFLICT DO NOTHING)"""
        conn = self.connect()
        cursor = conn.cursor()
        try:
            # PostgreSQL equivalent of INSERT OR IGNORE
            cursor.execute('''
                INSERT INTO teams (team_name, year)
                VALUES (%s, %s) 
                ON CONFLICT (team_name, year) DO NOTHING;
            ''', (team_name, year))
            conn.commit()
        except Exception as e:
            # Note: You might want to handle psycopg2 specific exceptions here
            print(f"Error inserting team: {e}")
        finally:
            self.close()
    
    def insert_race(self, year, round_number, event_name, country, location, event_date):
        """Insert race information (uses ON CONFLICT UPDATE)"""
        conn = self.connect()
        cursor = conn.cursor()
        try:
            # PostgreSQL equivalent of INSERT OR REPLACE
            # The UNIQUE constraint is (year, round_number)
            cursor.execute('''
                INSERT INTO races 
                (year, round_number, event_name, country, location, event_date)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (year, round_number) DO UPDATE
                SET event_name = EXCLUDED.event_name,
                    country = EXCLUDED.country,
                    location = EXCLUDED.location,
                    event_date = EXCLUDED.event_date
                RETURNING race_id;
            ''', (year, round_number, event_name, country, location, str(event_date)))
            
            race_id = cursor.fetchone()[0] if cursor.rowcount > 0 else None
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
            cursor.execute('''
                INSERT INTO qualifying_results 
                (race_id, driver_number, position, q1_time, q2_time, q3_time)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (race_id, driver_number, position, str(q1), str(q2), str(q3)))
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
            cursor.execute('''
                INSERT INTO race_results 
                (race_id, driver_number, position, points, grid_position, status, fastest_lap_time)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (race_id, driver_number, position, points, grid_position, status, str(fastest_lap)))
            conn.commit()
        except Exception as e:
            print(f"Error inserting race result: {e}")
        finally:
            self.close()
    
    def insert_prediction(self, race_id, session_type, driver_number, predicted_position, 
                          confidence, model_type, features, predicted_time=None, 
                          top10_probability=None, shap_values=None):
        """Insert prediction result"""
        conn = self.connect()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO predictions 
                (race_id, session_type, driver_number, predicted_position, predicted_time,
                 confidence, top10_probability, model_type, prediction_date, features_json, shap_values_json)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (race_id, session_type, driver_number, predicted_position, predicted_time,
                  confidence, top10_probability, model_type, datetime.now().isoformat(), 
                  json.dumps(features), json.dumps(shap_values) if shap_values is not None else None))
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
            cursor.execute('''
                INSERT INTO aggregated_laps 
                (race_id, session_type, driver_number, lap_number, lap_time,
                 sector1_time, sector2_time, sector3_time, compound, tyre_life,
                 track_status, is_personal_best)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (race_id, session_type, driver_number, lap_number, lap_time,
                  sector1, sector2, sector3, compound, tyre_life, track_status, is_personal_best))
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
            cursor.execute('''
                INSERT INTO tyre_stats 
                (race_id, session_type, driver_number, compound, total_laps,
                 avg_lap_time, degradation_slope, best_lap_time, stint_number)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (race_id, session_type, driver_number, compound, total_laps,
                  avg_lap_time, degradation_slope, best_lap_time, stint_number))
            conn.commit()
        except Exception as e:
            print(f"Error inserting tyre stat: {e}")
        finally:
            self.close()
    
    def insert_session(self, race_id, session_type, session_date, weather_conditions=None,
                       track_temp=None, air_temp=None):
        """Insert session information (uses ON CONFLICT UPDATE)"""
        conn = self.connect()
        cursor = conn.cursor()
        try:
            # PostgreSQL equivalent of INSERT OR REPLACE
            # The UNIQUE constraint is (race_id, session_type)
            cursor.execute('''
                INSERT INTO sessions 
                (race_id, session_type, session_date, weather_conditions, track_temp, air_temp)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (race_id, session_type) DO UPDATE
                SET session_date = EXCLUDED.session_date,
                    weather_conditions = EXCLUDED.weather_conditions,
                    track_temp = EXCLUDED.track_temp,
                    air_temp = EXCLUDED.air_temp
                RETURNING session_id;
            ''', (race_id, session_type, str(session_date), weather_conditions, track_temp, air_temp))
            
            session_id = cursor.fetchone()[0] if cursor.rowcount > 0 else None
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
        # pandas.read_sql_query supports ? placeholders by default but for consistency, we'll keep the query simple
        df = pd.read_sql_query("SELECT * FROM races ORDER BY year DESC, round_number", conn)
        self.close()
        return df
    
    def get_race_results(self, race_id):
        """Get results for a specific race"""
        conn = self.connect()
        # pandas.read_sql_query uses psycopg2 adapter when connecting to PostgreSQL, 
        # which can handle the %s in the query, but the params tuple must be correct.
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
        
        # NOTE: Using %s placeholders for read_sql_query with psycopg2 connection
        if race_id:
            query += " AND race_id = %s"
            params.append(race_id)
        if session_type:
            query += " AND session_type = %s"
            params.append(session_type)
        
        query += " ORDER BY predicted_position"
        df = pd.read_sql_query(query, conn, params=params)
        self.close()
        return df
    
    def execute_query(self, query, params=None):
        """Execute custom SQL query (read-only, sanitized)"""
        # Basic sanitization - only allow SELECT queries
        query_lower = query.strip().lower()
        if not query_lower.startswith('select'):
            raise ValueError("Only SELECT queries are allowed for safety")
        
        conn = self.connect()
        try:
            # read_sql_query automatically uses the connection's parameter style (%s)
            df = pd.read_sql_query(query, conn, params=params)
            return df
        finally:
            self.close()
    
    def get_aggregated_laps(self, race_id=None, session_type=None, driver_number=None):
        """Get aggregated lap data with optional filters"""
        conn = self.connect()
        query = "SELECT * FROM aggregated_laps WHERE 1=1"
        params = []
        
        # NOTE: Using %s placeholders for read_sql_query with psycopg2 connection
        if race_id:
            query += " AND race_id = %s"
            params.append(race_id)
        if session_type:
            query += " AND session_type = %s"
            params.append(session_type)
        if driver_number:
            query += " AND driver_number = %s"
            params.append(driver_number)
        
        query += " ORDER BY lap_number"
        df = pd.read_sql_query(query, conn, params=params if params else None)
        self.close()
        return df
    
    def get_tyre_stats(self, race_id=None, session_type=None, driver_number=None):
        """Get tyre statistics with optional filters"""
        conn = self.connect()
        query = "SELECT * FROM tyre_stats WHERE 1=1"
        params = []
        
        # NOTE: Using %s placeholders for read_sql_query with psycopg2 connection
        if race_id:
            query += " AND race_id = %s"
            params.append(race_id)
        if session_type:
            query += " AND session_type = %s"
            params.append(session_type)
        if driver_number:
            query += " AND driver_number = %s"
            params.append(driver_number)
        
        df = pd.read_sql_query(query, conn, params=params if params else None)
        self.close()
        return df
    
    def get_sessions(self, race_id=None):
        """Get session information"""
        conn = self.connect()
        if race_id:
            # NOTE: Using %s placeholders for read_sql_query with psycopg2 connection
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
    
    print("\n✓ Sample data inserted (Teams)")
    
    # Show all tables
    tables = db.get_table_names()
    
    print("\nDatabase tables:")
    for table in tables:
        print(f"  - {table}")


if __name__ == "__main__":
    main()