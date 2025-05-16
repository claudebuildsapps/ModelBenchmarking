#!/usr/bin/env python3
"""
Set up the database for ModelBenchmarking.
This script creates the necessary database tables based on the configured database type.
"""

import sys
import os
import argparse
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.settings import DATABASE_CONFIG
from src.database import get_database_manager

def setup_database(db_type: str = None, **config) -> bool:
    """
    Set up the database with required tables.
    
    Args:
        db_type: Database type to use (clickhouse or timescaledb)
        config: Additional configuration parameters
        
    Returns:
        True if setup was successful, False otherwise
    """
    # Use configured database type if not specified
    if db_type is None:
        db_type = DATABASE_CONFIG["type"]
    
    print(f"Setting up {db_type.upper()} database...")
    
    # Get the appropriate configuration
    db_config = {**DATABASE_CONFIG.get(db_type, {}), **config}
    
    try:
        # Create database manager
        db_manager = get_database_manager(db_type, **db_config)
        
        # Create tables
        db_manager.create_benchmark_table()
        
        print(f"\n{db_type.upper()} database setup completed successfully!")
        return True
    except ImportError as e:
        print(f"\nError: Required package not installed: {str(e)}")
        
        if db_type == "clickhouse":
            print("\nTo install ClickHouse driver, run: pip install clickhouse-driver")
        elif db_type == "timescaledb":
            print("\nTo install TimescaleDB driver, run: pip install psycopg2-binary")
            
        return False
    except Exception as e:
        print(f"\nError setting up {db_type.upper()} database: {str(e)}")
        return False

def main():
    """Main function to parse arguments and set up the database."""
    parser = argparse.ArgumentParser(description="Set up the ModelBenchmarking database")
    parser.add_argument(
        "--db-type", 
        choices=["clickhouse", "timescaledb"],
        default=DATABASE_CONFIG["type"],
        help="Database type to use"
    )
    parser.add_argument("--host", help="Database host")
    parser.add_argument("--port", type=int, help="Database port")
    parser.add_argument("--user", help="Database user (for access control)")
    parser.add_argument("--password", help="Database password")
    parser.add_argument("--database", help="Database name")
    
    args = parser.parse_args()
    
    # Build configuration from arguments
    config = {}
    if args.host:
        config["host"] = args.host
    if args.port:
        config["port"] = args.port
    if args.user:
        config["user"] = args.user
    if args.password:
        config["password"] = args.password
    if args.database:
        config["database"] = args.database
    
    # Set up the database
    success = setup_database(args.db_type, **config)
    
    if success:
        db_type = args.db_type.upper()
        print(f"\nYou can now use the ModelBenchmarking system with {db_type}.")
        print("\nExample usage:")
        print("\nfrom config.settings import DATABASE_CONFIG")
        print("from src.database import get_database_manager")
        print("from src.benchmarking import ModelBenchmark")
        print("\n# Initialize the database manager")
        
        if args.db_type == "clickhouse":
            print("db = get_database_manager('clickhouse', host='localhost', port=9000)")
        elif args.db_type == "timescaledb":
            print("db = get_database_manager('timescaledb', host='localhost', port=5432)")
            
        print("\n# Initialize the benchmarking system")
        print("benchmark = ModelBenchmark(db_manager=db)")
        print("\n# Run a simple benchmark")
        print("result = benchmark.benchmark_model(...)")
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()