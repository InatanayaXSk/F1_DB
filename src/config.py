"""
Configuration Module
Manages database and Redis configuration from environment variables
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)


class Config:
    """Configuration class for database and Redis settings"""
    
    # Database Configuration
    DB_TYPE = os.getenv('DB_TYPE', 'sqlite')  # 'sqlite' or 'postgresql'
    DB_PATH = os.getenv('DB_PATH', 'f1_data.db')
    
    # PostgreSQL Configuration
    POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
    POSTGRES_PORT = int(os.getenv('POSTGRES_PORT', 5432))
    POSTGRES_DB = os.getenv('POSTGRES_DB', 'f1_database')
    POSTGRES_USER = os.getenv('POSTGRES_USER', 'f1_user')
    POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', '')
    
    # Redis Configuration
    REDIS_ENABLED = os.getenv('REDIS_ENABLED', 'false').lower() == 'true'
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_DB = int(os.getenv('REDIS_DB', 0))
    REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)
    REDIS_TTL = int(os.getenv('REDIS_TTL', 3600))  # Default 1 hour
    
    @classmethod
    def get_database_url(cls):
        """Get database connection URL based on DB_TYPE"""
        if cls.DB_TYPE == 'postgresql':
            return f"postgresql://{cls.POSTGRES_USER}:{cls.POSTGRES_PASSWORD}@{cls.POSTGRES_HOST}:{cls.POSTGRES_PORT}/{cls.POSTGRES_DB}"
        else:
            # For SQLite
            if not os.path.isabs(cls.DB_PATH):
                cls.DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), cls.DB_PATH)
            return f"sqlite:///{cls.DB_PATH}"
    
    @classmethod
    def get_redis_url(cls):
        """Get Redis connection URL"""
        if cls.REDIS_PASSWORD:
            return f"redis://:{cls.REDIS_PASSWORD}@{cls.REDIS_HOST}:{cls.REDIS_PORT}/{cls.REDIS_DB}"
        else:
            return f"redis://{cls.REDIS_HOST}:{cls.REDIS_PORT}/{cls.REDIS_DB}"
