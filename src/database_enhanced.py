"""
Enhanced Database Module with PostgreSQL and Redis Support
Manages F1 data storage with SQLAlchemy ORM and Redis caching
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from sqlalchemy.pool import StaticPool
import pandas as pd
from datetime import datetime
import json
from typing import Optional

try:
    from .config import Config
    from .redis_cache import RedisCache, cache_query
except ImportError:
    from config import Config
    from redis_cache import RedisCache, cache_query


Base = declarative_base()


# SQLAlchemy Models
class Driver(Base):
    __tablename__ = 'drivers'
    
    driver_id = Column(Integer, primary_key=True, autoincrement=True)
    driver_number = Column(Integer)
    abbreviation = Column(String)
    full_name = Column(String)
    team_name = Column(String)
    year = Column(Integer)
    
    __table_args__ = (UniqueConstraint('driver_number', 'year', name='_driver_year_uc'),)


class Team(Base):
    __tablename__ = 'teams'
    
    team_id = Column(Integer, primary_key=True, autoincrement=True)
    team_name = Column(String)
    year = Column(Integer)
    
    __table_args__ = (UniqueConstraint('team_name', 'year', name='_team_year_uc'),)


class Race(Base):
    __tablename__ = 'races'
    
    race_id = Column(Integer, primary_key=True, autoincrement=True)
    year = Column(Integer)
    round_number = Column(Integer)
    event_name = Column(String)
    country = Column(String)
    location = Column(String)
    event_date = Column(String)
    
    __table_args__ = (UniqueConstraint('year', 'round_number', name='_year_round_uc'),)


class QualifyingResult(Base):
    __tablename__ = 'qualifying_results'
    
    result_id = Column(Integer, primary_key=True, autoincrement=True)
    race_id = Column(Integer, ForeignKey('races.race_id'))
    driver_number = Column(Integer)
    position = Column(Integer)
    q1_time = Column(String)
    q2_time = Column(String)
    q3_time = Column(String)


class SprintResult(Base):
    __tablename__ = 'sprint_results'
    
    result_id = Column(Integer, primary_key=True, autoincrement=True)
    race_id = Column(Integer, ForeignKey('races.race_id'))
    driver_number = Column(Integer)
    position = Column(Integer)
    points = Column(Float)
    status = Column(String)


class RaceResult(Base):
    __tablename__ = 'race_results'
    
    result_id = Column(Integer, primary_key=True, autoincrement=True)
    race_id = Column(Integer, ForeignKey('races.race_id'))
    driver_number = Column(Integer)
    position = Column(Integer)
    points = Column(Float)
    grid_position = Column(Integer)
    status = Column(String)
    fastest_lap_time = Column(String)


class Prediction(Base):
    __tablename__ = 'predictions'
    
    prediction_id = Column(Integer, primary_key=True, autoincrement=True)
    race_id = Column(Integer, ForeignKey('races.race_id'))
    session_type = Column(String)
    driver_number = Column(Integer)
    predicted_position = Column(Integer)
    predicted_time = Column(Float)
    confidence = Column(Float)
    top10_probability = Column(Float)
    model_type = Column(String)
    prediction_date = Column(String)
    features_json = Column(Text)
    shap_values_json = Column(Text)


class AggregatedLap(Base):
    __tablename__ = 'aggregated_laps'
    
    lap_id = Column(Integer, primary_key=True, autoincrement=True)
    race_id = Column(Integer, ForeignKey('races.race_id'))
    session_type = Column(String)
    driver_number = Column(Integer)
    lap_number = Column(Integer)
    lap_time = Column(Float)
    sector1_time = Column(Float)
    sector2_time = Column(Float)
    sector3_time = Column(Float)
    compound = Column(String)
    tyre_life = Column(Integer)
    track_status = Column(String)
    is_personal_best = Column(Integer)


class TyreStat(Base):
    __tablename__ = 'tyre_stats'
    
    tyre_stat_id = Column(Integer, primary_key=True, autoincrement=True)
    race_id = Column(Integer, ForeignKey('races.race_id'))
    session_type = Column(String)
    driver_number = Column(Integer)
    compound = Column(String)
    total_laps = Column(Integer)
    avg_lap_time = Column(Float)
    degradation_slope = Column(Float)
    best_lap_time = Column(Float)
    stint_number = Column(Integer)


class Session(Base):
    __tablename__ = 'sessions'
    
    session_id = Column(Integer, primary_key=True, autoincrement=True)
    race_id = Column(Integer, ForeignKey('races.race_id'))
    session_type = Column(String)
    session_date = Column(String)
    weather_conditions = Column(String)
    track_temp = Column(Float)
    air_temp = Column(Float)
    
    __table_args__ = (UniqueConstraint('race_id', 'session_type', name='_race_session_uc'),)


class F1DatabaseEnhanced:
    """Enhanced database manager with PostgreSQL and Redis support"""
    
    def __init__(self, db_url: Optional[str] = None):
        """Initialize database connection with SQLAlchemy"""
        self.db_url = db_url or Config.get_database_url()
        
        # Special handling for SQLite
        if self.db_url.startswith('sqlite'):
            self.engine = create_engine(
                self.db_url,
                connect_args={'check_same_thread': False},
                poolclass=StaticPool
            )
        else:
            self.engine = create_engine(self.db_url, pool_pre_ping=True)
        
        self.Session = sessionmaker(bind=self.engine)
        self._cache = RedisCache()
        
        # Create tables
        Base.metadata.create_all(self.engine)
        print(f"✓ Database initialized: {Config.DB_TYPE}")
    
    def get_session(self):
        """Get database session"""
        return self.Session()
    
    def insert_driver(self, driver_number, abbreviation, full_name, team_name, year):
        """Insert driver information"""
        session = self.get_session()
        try:
            driver = session.query(Driver).filter_by(
                driver_number=driver_number, year=year
            ).first()
            
            if driver:
                driver.abbreviation = abbreviation
                driver.full_name = full_name
                driver.team_name = team_name
            else:
                driver = Driver(
                    driver_number=driver_number,
                    abbreviation=abbreviation,
                    full_name=full_name,
                    team_name=team_name,
                    year=year
                )
                session.add(driver)
            
            session.commit()
            self._cache.delete_pattern('drivers:*')
        except Exception as e:
            session.rollback()
            print(f"Error inserting driver: {e}")
        finally:
            session.close()
    
    def insert_team(self, team_name, year):
        """Insert team information"""
        session = self.get_session()
        try:
            team = session.query(Team).filter_by(team_name=team_name, year=year).first()
            if not team:
                team = Team(team_name=team_name, year=year)
                session.add(team)
                session.commit()
                self._cache.delete_pattern('teams:*')
        except Exception as e:
            session.rollback()
            print(f"Error inserting team: {e}")
        finally:
            session.close()
    
    def insert_race(self, year, round_number, event_name, country, location, event_date):
        """Insert race information"""
        session = self.get_session()
        try:
            race = session.query(Race).filter_by(
                year=year, round_number=round_number
            ).first()
            
            if race:
                race.event_name = event_name
                race.country = country
                race.location = location
                race.event_date = str(event_date)
            else:
                race = Race(
                    year=year,
                    round_number=round_number,
                    event_name=event_name,
                    country=country,
                    location=location,
                    event_date=str(event_date)
                )
                session.add(race)
            
            session.commit()
            race_id = race.race_id
            self._cache.delete_pattern('races:*')
            return race_id
        except Exception as e:
            session.rollback()
            print(f"Error inserting race: {e}")
            return None
        finally:
            session.close()
    
    def insert_prediction(self, race_id, session_type, driver_number, predicted_position,
                         confidence, model_type, features, predicted_time=None,
                         top10_probability=None, shap_values=None):
        """Insert prediction result"""
        session = self.get_session()
        try:
            prediction = Prediction(
                race_id=race_id,
                session_type=session_type,
                driver_number=driver_number,
                predicted_position=predicted_position,
                predicted_time=predicted_time,
                confidence=confidence,
                top10_probability=top10_probability,
                model_type=model_type,
                prediction_date=datetime.now().isoformat(),
                features_json=json.dumps(features),
                shap_values_json=json.dumps(shap_values) if shap_values else None
            )
            session.add(prediction)
            session.commit()
            self._cache.delete_pattern(f'predictions:*')
            self._cache.invalidate_race_cache(race_id)
        except Exception as e:
            session.rollback()
            print(f"Error inserting prediction: {e}")
        finally:
            session.close()
    
    @cache_query('races', ttl=7200)
    def get_all_races(self):
        """Get all races from database (cached)"""
        query = "SELECT * FROM races ORDER BY year DESC, round_number"
        return pd.read_sql_query(query, self.engine)
    
    @cache_query('race_results', ttl=3600)
    def get_race_results(self, race_id):
        """Get results for a specific race (cached)"""
        query = "SELECT * FROM race_results WHERE race_id = ? ORDER BY position"
        return pd.read_sql_query(query, self.engine, params=(race_id,))
    
    @cache_query('predictions', ttl=1800)
    def get_predictions(self, race_id=None, session_type=None):
        """Get predictions, optionally filtered (cached)"""
        query = "SELECT * FROM predictions WHERE 1=1"
        params = []
        
        if race_id:
            query += " AND race_id = ?"
            params.append(race_id)
        if session_type:
            query += " AND session_type = ?"
            params.append(session_type)
        
        query += " ORDER BY predicted_position"
        
        if params:
            return pd.read_sql_query(query, self.engine, params=tuple(params))
        else:
            return pd.read_sql_query(query, self.engine)
    
    def execute_query(self, query, params=None):
        """Execute custom SQL query (read-only, cached if beneficial)"""
        # Basic sanitization - only allow SELECT queries
        query_lower = query.strip().lower()
        if not query_lower.startswith('select'):
            raise ValueError("Only SELECT queries are allowed for safety")
        
        if params:
            return pd.read_sql_query(query, self.engine, params=params)
        else:
            return pd.read_sql_query(query, self.engine)
    
    def get_table_names(self):
        """Get all table names in the database"""
        return Base.metadata.tables.keys()
    
    def flush_cache(self):
        """Flush all Redis cache"""
        self._cache.flush_all()
    
    def get_cache_stats(self):
        """Get Redis cache statistics"""
        return self._cache.get_stats()


def main():
    """Main function to demonstrate database operations"""
    db = F1DatabaseEnhanced()
    
    print("\nF1 Enhanced Database Manager")
    print("=" * 50)
    print(f"Database type: {Config.DB_TYPE}")
    print(f"Redis enabled: {Config.REDIS_ENABLED}")
    
    # Example: Insert sample data
    db.insert_team("Red Bull Racing", 2024)
    db.insert_team("Ferrari", 2024)
    db.insert_team("Mercedes", 2024)
    
    print("\n✓ Sample data inserted")
    
    # Show cache stats
    stats = db.get_cache_stats()
    print("\nCache statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Show all tables
    print("\nDatabase tables:")
    for table in db.get_table_names():
        print(f"  - {table}")


if __name__ == "__main__":
    main()
