"""
SQLite Database Module
Manages F1 data storage in SQLite database
"""

import sqlite3
import pandas as pd
import os
from datetime import datetime
import json


class F1Database:
    """Manages SQLite database for F1 data"""
    
    def __init__(self, db_path='f1_data.db'):
        """Initialize database connection"""
        if not os.path.isabs(db_path):
            db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), db_path)
        self.db_path = db_path
        self.conn = None
        self.initialize_database()
    
    def connect(self):
        """Create database connection"""
        self.conn = sqlite3.connect(self.db_path)
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
                driver_id INTEGER PRIMARY KEY AUTOINCREMENT,
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
                team_id INTEGER PRIMARY KEY AUTOINCREMENT,
                team_name TEXT,
                year INTEGER,
                UNIQUE(team_name, year)
            )
        ''')
        
        # Races table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS races (
                race_id INTEGER PRIMARY KEY AUTOINCREMENT,
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
                result_id INTEGER PRIMARY KEY AUTOINCREMENT,
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
                result_id INTEGER PRIMARY KEY AUTOINCREMENT,
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
                result_id INTEGER PRIMARY KEY AUTOINCREMENT,
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
                prediction_id INTEGER PRIMARY KEY AUTOINCREMENT,
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
                lap_id INTEGER PRIMARY KEY AUTOINCREMENT,
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
                tyre_stat_id INTEGER PRIMARY KEY AUTOINCREMENT,
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
                session_id INTEGER PRIMARY KEY AUTOINCREMENT,
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
        print(f"✓ Database initialized at {self.db_path}")
        
        # Run migrations
        self.upgrade_database()
    
    def upgrade_database(self):
        """Upgrade existing database schema with new columns"""
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            # Check if predicted_time column exists in predictions table
            cursor.execute("PRAGMA table_info(predictions)")
            columns = [col[1] for col in cursor.fetchall()]
            
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
        """Insert driver information"""
        conn = self.connect()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO drivers 
                (driver_number, abbreviation, full_name, team_name, year)
                VALUES (?, ?, ?, ?, ?)
            ''', (driver_number, abbreviation, full_name, team_name, year))
            conn.commit()
        except Exception as e:
            print(f"Error inserting driver: {e}")
        finally:
            self.close()
    
    def insert_team(self, team_name, year):
        """Insert team information"""
        conn = self.connect()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO teams (team_name, year)
                VALUES (?, ?)
            ''', (team_name, year))
            conn.commit()
        except Exception as e:
            print(f"Error inserting team: {e}")
        finally:
            self.close()
    
    def insert_race(self, year, round_number, event_name, country, location, event_date):
        """Insert race information"""
        conn = self.connect()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO races 
                (year, round_number, event_name, country, location, event_date)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (year, round_number, event_name, country, location, str(event_date)))
            conn.commit()
            return cursor.lastrowid
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
                VALUES (?, ?, ?, ?, ?, ?)
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
                VALUES (?, ?, ?, ?, ?, ?, ?)
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
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (race_id, session_type, driver_number, predicted_position, predicted_time,
                  confidence, top10_probability, model_type, datetime.now().isoformat(), 
                  json.dumps(features), json.dumps(shap_values) if shap_values else None))
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
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (race_id, session_type, driver_number, compound, total_laps,
                  avg_lap_time, degradation_slope, best_lap_time, stint_number))
            conn.commit()
        except Exception as e:
            print(f"Error inserting tyre stat: {e}")
        finally:
            self.close()
    
    def insert_session(self, race_id, session_type, session_date, weather_conditions=None,
                      track_temp=None, air_temp=None):
        """Insert session information"""
        conn = self.connect()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO sessions 
                (race_id, session_type, session_date, weather_conditions, track_temp, air_temp)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (race_id, session_type, str(session_date), weather_conditions, track_temp, air_temp))
            conn.commit()
            return cursor.lastrowid
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
            "SELECT * FROM race_results WHERE race_id = ? ORDER BY position", 
            conn, params=(race_id,)
        )
        self.close()
        return df
    
    def get_predictions(self, race_id=None, session_type=None):
        """Get predictions, optionally filtered"""
        conn = self.connect()
        query = "SELECT * FROM predictions WHERE 1=1"
        params = []
        
        if race_id:
            query += " AND race_id = ?"
            params.append(race_id)
        if session_type:
            query += " AND session_type = ?"
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
            if params:
                df = pd.read_sql_query(query, conn, params=params)
            else:
                df = pd.read_sql_query(query, conn)
            return df
        finally:
            self.close()
    
    def get_aggregated_laps(self, race_id=None, session_type=None, driver_number=None):
        """Get aggregated lap data with optional filters"""
        conn = self.connect()
        query = "SELECT * FROM aggregated_laps WHERE 1=1"
        params = []
        
        if race_id:
            query += " AND race_id = ?"
            params.append(race_id)
        if session_type:
            query += " AND session_type = ?"
            params.append(session_type)
        if driver_number:
            query += " AND driver_number = ?"
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
        
        if race_id:
            query += " AND race_id = ?"
            params.append(race_id)
        if session_type:
            query += " AND session_type = ?"
            params.append(session_type)
        if driver_number:
            query += " AND driver_number = ?"
            params.append(driver_number)
        
        df = pd.read_sql_query(query, conn, params=params if params else None)
        self.close()
        return df
    
    def get_sessions(self, race_id=None):
        """Get session information"""
        conn = self.connect()
        if race_id:
            df = pd.read_sql_query("SELECT * FROM sessions WHERE race_id = ?", conn, params=(race_id,))
        else:
            df = pd.read_sql_query("SELECT * FROM sessions", conn)
        self.close()
        return df
    
    def get_table_names(self):
        """Get all table names in the database"""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [row[0] for row in cursor.fetchall()]
        self.close()
        return tables



def main():
    """Main function to demonstrate database operations"""
    db = F1Database('f1_data.db')
    
    print("\nF1 Database Manager")
    print("=" * 50)
    print(f"Database location: {db.db_path}")
    
    # Example: Insert sample data
    db.insert_team("Red Bull Racing", 2024)
    db.insert_team("Ferrari", 2024)
    db.insert_team("Mercedes", 2024)
    
    print("\n✓ Sample data inserted")
    
    # Show all tables
    conn = db.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    db.close()
    
    print("\nDatabase tables:")
    for table in tables:
        print(f"  - {table[0]}")


if __name__ == "__main__":
    main()
