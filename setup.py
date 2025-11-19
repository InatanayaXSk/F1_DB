#!/usr/bin/env python3
"""
Setup Script for F1 Prediction System
Helps users set up PostgreSQL and Redis, and initialize the system
"""

import os
import sys
import subprocess
import time


def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(text)
    print("=" * 60)


def check_docker():
    """Check if Docker is installed and running"""
    try:
        result = subprocess.run(
            ["docker", "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        print("✓ Docker is installed:", result.stdout.strip())
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("✗ Docker is not installed or not in PATH")
        return False


def check_docker_compose():
    """Check if Docker Compose is available"""
    try:
        result = subprocess.run(
            ["docker-compose", "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        print("✓ Docker Compose is installed:", result.stdout.strip())
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("✗ Docker Compose is not installed")
        return False


def start_services():
    """Start PostgreSQL and Redis using Docker Compose"""
    print("\nStarting PostgreSQL and Redis...")
    try:
        subprocess.run(
            ["docker-compose", "up", "-d"],
            check=True
        )
        print("✓ Services started successfully")
        print("  - PostgreSQL running on localhost:5432")
        print("  - Redis running on localhost:6379")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to start services: {e}")
        return False


def wait_for_services():
    """Wait for services to be ready"""
    print("\nWaiting for services to be ready...")
    time.sleep(5)
    
    # Check PostgreSQL
    try:
        subprocess.run(
            ["docker", "exec", "f1_postgres", "pg_isready", "-U", "postgres"],
            capture_output=True,
            check=True
        )
        print("✓ PostgreSQL is ready")
    except subprocess.CalledProcessError:
        print("⚠ PostgreSQL might not be ready yet")
    
    # Check Redis
    try:
        subprocess.run(
            ["docker", "exec", "f1_redis", "redis-cli", "ping"],
            capture_output=True,
            check=True
        )
        print("✓ Redis is ready")
    except subprocess.CalledProcessError:
        print("⚠ Redis might not be ready yet")


def install_dependencies():
    """Install Python dependencies"""
    print("\nInstalling Python dependencies...")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            check=True
        )
        print("✓ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install dependencies: {e}")
        return False


def initialize_database():
    """Initialize PostgreSQL database"""
    print("\nInitializing PostgreSQL database...")
    try:
        subprocess.run(
            [sys.executable, "src/database.py"],
            check=True
        )
        print("✓ Database initialized successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to initialize database: {e}")
        return False


def main():
    """Main setup function"""
    print_header("F1 Prediction System - Setup Script")
    
    print("\nThis script will:")
    print("1. Check Docker installation")
    print("2. Start PostgreSQL and Redis containers")
    print("3. Install Python dependencies")
    print("4. Initialize PostgreSQL database")
    
    input("\nPress Enter to continue or Ctrl+C to cancel...")
    
    # Check Docker
    print_header("Checking Docker")
    if not check_docker():
        print("\nPlease install Docker first: https://docs.docker.com/get-docker/")
        sys.exit(1)
    
    if not check_docker_compose():
        print("\nPlease install Docker Compose: https://docs.docker.com/compose/install/")
        sys.exit(1)
    
    # Start services
    print_header("Starting Services")
    if not start_services():
        sys.exit(1)
    
    wait_for_services()
    
    # Install dependencies
    print_header("Installing Dependencies")
    if not install_dependencies():
        sys.exit(1)
    
    # Initialize database
    print_header("Initializing Database")
    if not initialize_database():
        sys.exit(1)
    
    # Success message
    print_header("Setup Complete!")
    print("\n✓ All components are ready!")
    print("\nNext steps:")
    print("1. Cache F1 data: python src/data_fetcher.py")
    print("2. Populate database: python src/populate_database.py")
    print("3. Launch dashboard: python -m streamlit run src/streamlit_app.py")
    print("\nFor more information, see README.md and MIGRATION.md")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        sys.exit(1)
