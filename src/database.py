import sqlite3
import os
import json
import logging
from abc import ABC, abstractmethod
import pandas as pd
from typing import Dict, List, Any, Optional, Union
import uuid
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DatabaseManager(ABC):
    """
    Abstract base class for database managers.
    """
    
    @abstractmethod
    def execute(self, query: str, params: Optional[Dict] = None) -> List:
        """Execute a query."""
        pass
        
    @abstractmethod
    def execute_df(self, query: str, params: Optional[Dict] = None) -> pd.DataFrame:
        """Execute a query and return results as DataFrame."""
        pass
        
    @abstractmethod
    def create_benchmark_table(self) -> None:
        """Create benchmark tables."""
        pass
        
    @abstractmethod
    def insert_benchmark(self, data: Dict[str, Any]) -> None:
        """Insert benchmark data."""
        pass
        
    @abstractmethod
    def get_model_benchmarks(self, model_name: str, limit: int = 100) -> pd.DataFrame:
        """Get benchmark results for a model."""
        pass
        
    @abstractmethod
    def get_top_models(self, task_type: str, metric: str, limit: int = 10) -> pd.DataFrame:
        """Get top models for a task."""
        pass


# SQLite functionality removed as requested


try:
    from clickhouse_driver import Client
    CLICKHOUSE_AVAILABLE = True
except ImportError:
    CLICKHOUSE_AVAILABLE = False
    logger.warning("ClickHouse driver not available. Install with 'pip install clickhouse-driver'")


class ClickHouseManager(DatabaseManager):
    """
    Manager for interacting with the ClickHouse database.
    """
    
    def __init__(self, host: str = 'localhost', port: int = 9000, 
                 user: str = 'default', password: str = '',
                 database: str = 'default'):
        """
        Initialize the ClickHouse database connection.
        
        Args:
            host: ClickHouse server host
            port: ClickHouse server port
            user: Username for authentication
            password: Password for authentication
            database: Default database to use
        """
        if not CLICKHOUSE_AVAILABLE:
            raise ImportError("ClickHouse driver not installed. Run: pip install clickhouse-driver")
            
        self.client = Client(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )
        
        logger.info(f"Connected to ClickHouse at {host}:{port}, database: {database}")
        
    def execute(self, query: str, params: Optional[Dict] = None) -> List:
        """
        Execute a ClickHouse query.
        
        Args:
            query: SQL query to execute
            params: Query parameters
            
        Returns:
            Query result as a list
        """
        try:
            result = self.client.execute(query, params or {})
            
            # For SELECT queries, convert to list of dicts
            if query.strip().upper().startswith("SELECT"):
                columns = [c[0] for c in self.client.execute(f"DESC ({query})", params or {})]
                return [dict(zip(columns, row)) for row in result]
            return result
        except Exception as e:
            logger.error(f"ClickHouse query error: {e}")
            raise
    
    def execute_df(self, query: str, params: Optional[Dict] = None) -> pd.DataFrame:
        """
        Execute a query and return the result as a pandas DataFrame.
        
        Args:
            query: SQL query to execute
            params: Query parameters
            
        Returns:
            Query result as a pandas DataFrame
        """
        try:
            result = self.client.execute(query, params or {})
            columns = [c[0] for c in self.client.execute(f"DESC ({query})", params or {})]
            return pd.DataFrame(result, columns=columns)
        except Exception as e:
            logger.error(f"ClickHouse DataFrame query error: {e}")
            if "Empty result" in str(e):
                return pd.DataFrame()
            raise
    
    def create_benchmark_table(self) -> None:
        """
        Create the main table for storing benchmark results.
        """
        # Create database if it doesn't exist
        self.client.execute("CREATE DATABASE IF NOT EXISTS benchmark_db")
        self.client.execute("USE benchmark_db")
        
        # Create model benchmarks table
        self.execute("""
            CREATE TABLE IF NOT EXISTS model_benchmarks (
                id UUID DEFAULT generateUUIDv4(),
                timestamp DateTime DEFAULT now(),
                model_name String,
                model_version String,
                task_type String,
                dataset String,
                metric String,
                score Float64,
                runtime_ms UInt32,
                memory_usage_mb Float32,
                hardware_config String,
                parameters_count UInt64,
                source_url String,
                metadata String
            ) ENGINE = MergeTree()
            ORDER BY (model_name, timestamp)
        """)
        
        # Create model metadata table
        self.execute("""
            CREATE TABLE IF NOT EXISTS model_metadata (
                name String,
                version String,
                created_date Nullable(DateTime),
                authors Array(String),
                description String,
                source_url String,
                license String,
                parameters_count UInt64,
                architecture_type String,
                tags Array(String),
                framework String,
                additional_info String,
                PRIMARY KEY (name, version)
            ) ENGINE = MergeTree()
            ORDER BY (name, version)
        """)
        
        # Create dataset metadata table
        self.execute("""
            CREATE TABLE IF NOT EXISTS dataset_metadata (
                name String,
                version String,
                task_type String,
                size UInt64,
                source_url String,
                license String,
                description String,
                citation String,
                metrics Array(String),
                additional_info String,
                PRIMARY KEY name
            ) ENGINE = MergeTree()
            ORDER BY name
        """)
        
        logger.info("ClickHouse tables created successfully")
        
    def insert_benchmark(self, data: Dict[str, Any]) -> None:
        """
        Insert a benchmark result into the database.
        
        Args:
            data: Benchmark data as a dictionary
        """
        # Ensure required fields are present
        required_fields = ['model_name', 'model_version', 'task_type', 
                          'dataset', 'metric']
        
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field '{field}'")
        
        # Convert dictionary fields to JSON strings
        if 'hardware_config' in data and isinstance(data['hardware_config'], dict):
            data['hardware_config'] = json.dumps(data['hardware_config'])
            
        if 'metadata' in data and isinstance(data['metadata'], dict):
            data['metadata'] = json.dumps(data['metadata'])
        
        # Convert timestamp to ClickHouse DateTime format if needed
        if 'timestamp' in data and isinstance(data['timestamp'], str):
            try:
                dt = datetime.fromisoformat(data['timestamp'])
                data['timestamp'] = dt
            except ValueError:
                # If not a valid ISO format, just use current time
                data['timestamp'] = datetime.now()
        elif 'timestamp' not in data:
            data['timestamp'] = datetime.now()
        
        # Prepare field lists
        fields = list(data.keys())
        values = [data[field] for field in fields]
        
        # Build the query
        query = f"""
            INSERT INTO model_benchmarks ({', '.join(fields)})
            VALUES ({', '.join(['%s'] * len(fields))})
        """
        
        self.client.execute(query, values)
        logger.info(f"Inserted benchmark data for {data['model_name']} v{data['model_version']}")
        
    def get_model_benchmarks(self, model_name: str, limit: int = 100) -> pd.DataFrame:
        """
        Retrieve all benchmarks for a specific model.
        
        Args:
            model_name: Name of the model to query
            limit: Maximum number of rows to return
            
        Returns:
            Benchmark results as a DataFrame
        """
        query = """
            SELECT * FROM model_benchmarks 
            WHERE model_name = %(model_name)s
            ORDER BY timestamp DESC
            LIMIT %(limit)s
        """
        
        return self.execute_df(query, {
            "model_name": model_name,
            "limit": limit
        })
    
    def get_top_models(self, task_type: str, metric: str, 
                      limit: int = 10) -> pd.DataFrame:
        """
        Get the top-performing models for a specific task and metric.
        
        Args:
            task_type: Type of task (e.g., 'image_classification')
            metric: Performance metric to sort by
            limit: Maximum number of results to return
            
        Returns:
            Top models as a DataFrame
        """
        query = """
            SELECT 
                model_name, 
                model_version,
                MAX(score) as best_score,
                AVG(runtime_ms) as avg_runtime_ms,
                MAX(timestamp) as last_benchmark
            FROM model_benchmarks 
            WHERE task_type = %(task_type)s
              AND metric = %(metric)s
            GROUP BY model_name, model_version
            ORDER BY best_score DESC
            LIMIT %(limit)s
        """
        
        return self.execute_df(query, {
            "task_type": task_type,
            "metric": metric,
            "limit": limit
        })


try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    TIMESCALEDB_AVAILABLE = True
except ImportError:
    TIMESCALEDB_AVAILABLE = False
    logger.warning("psycopg2 not available. Install with 'pip install psycopg2-binary'")


class TimescaleDBManager(DatabaseManager):
    """
    Manager for interacting with the TimescaleDB.
    """
    
    def __init__(self, host: str = 'localhost', port: int = 5432, 
                 user: str = 'postgres', password: str = '',
                 database: str = 'benchmark_db'):
        """
        Initialize the TimescaleDB database connection.
        
        Args:
            host: TimescaleDB server host
            port: TimescaleDB server port
            user: Username for authentication
            password: Password for authentication
            database: Database to use
        """
        if not TIMESCALEDB_AVAILABLE:
            raise ImportError("psycopg2 not installed. Run: pip install psycopg2-binary")
            
        self.conn_params = {
            'host': host,
            'port': port,
            'user': user,
            'password': password,
            'database': database
        }
        
        self.conn = psycopg2.connect(**self.conn_params)
        logger.info(f"Connected to TimescaleDB at {host}:{port}, database: {database}")
        
    def __del__(self):
        """Close the connection when the object is deleted."""
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()
            
    def _get_connection(self):
        """Get a new connection if the current one is closed."""
        if self.conn.closed:
            self.conn = psycopg2.connect(**self.conn_params)
        return self.conn
        
    def execute(self, query: str, params: Optional[Dict] = None) -> List:
        """
        Execute a TimescaleDB query.
        
        Args:
            query: SQL query to execute
            params: Query parameters
            
        Returns:
            Query result as a list of dictionaries
        """
        conn = self._get_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            try:
                cursor.execute(query, params or {})
                conn.commit()
                
                if query.strip().upper().startswith("SELECT"):
                    return cursor.fetchall()
                return []
            except Exception as e:
                conn.rollback()
                logger.error(f"TimescaleDB query error: {e}")
                raise
    
    def execute_df(self, query: str, params: Optional[Dict] = None) -> pd.DataFrame:
        """
        Execute a query and return the result as a pandas DataFrame.
        
        Args:
            query: SQL query to execute
            params: Query parameters
            
        Returns:
            Query result as a pandas DataFrame
        """
        conn = self._get_connection()
        try:
            return pd.read_sql_query(query, conn, params=params)
        except Exception as e:
            logger.error(f"TimescaleDB DataFrame query error: {e}")
            return pd.DataFrame()
    
    def create_benchmark_table(self) -> None:
        """
        Create the main tables for storing benchmark results.
        """
        conn = self._get_connection()
        with conn.cursor() as cursor:
            # Check if TimescaleDB extension is installed
            cursor.execute("SELECT EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'timescaledb')")
            has_timescaledb = cursor.fetchone()[0]
            
            if not has_timescaledb:
                logger.warning("TimescaleDB extension not found. Creating regular PostgreSQL tables.")
            
            # Create model benchmarks table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS model_benchmarks (
                    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
                    timestamp TIMESTAMPTZ DEFAULT NOW(),
                    model_name TEXT NOT NULL,
                    model_version TEXT NOT NULL,
                    task_type TEXT NOT NULL,
                    dataset TEXT NOT NULL,
                    metric TEXT NOT NULL,
                    score DOUBLE PRECISION,
                    runtime_ms INTEGER,
                    memory_usage_mb REAL,
                    hardware_config JSONB,
                    parameters_count BIGINT,
                    source_url TEXT,
                    metadata JSONB
                )
            """)
            
            # Convert to hypertable if TimescaleDB is available
            if has_timescaledb:
                try:
                    cursor.execute("SELECT create_hypertable('model_benchmarks', 'timestamp', if_not_exists => TRUE)")
                    logger.info("Created TimescaleDB hypertable for model_benchmarks")
                except Exception as e:
                    logger.error(f"Failed to create hypertable: {e}")
            
            # Create model metadata table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS model_metadata (
                    name TEXT,
                    version TEXT,
                    created_date TIMESTAMPTZ,
                    authors TEXT[],
                    description TEXT,
                    source_url TEXT,
                    license TEXT,
                    parameters_count BIGINT,
                    architecture_type TEXT,
                    tags TEXT[],
                    framework TEXT,
                    additional_info JSONB,
                    PRIMARY KEY (name, version)
                )
            """)
            
            # Create dataset metadata table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS dataset_metadata (
                    name TEXT PRIMARY KEY,
                    version TEXT,
                    task_type TEXT,
                    size BIGINT,
                    source_url TEXT,
                    license TEXT,
                    description TEXT,
                    citation TEXT,
                    metrics TEXT[],
                    additional_info JSONB
                )
            """)
            
            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_model_benchmarks_model ON model_benchmarks (model_name, model_version)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_model_benchmarks_task ON model_benchmarks (task_type, metric)")
            
            conn.commit()
            logger.info("TimescaleDB tables created successfully")
        
    def insert_benchmark(self, data: Dict[str, Any]) -> None:
        """
        Insert a benchmark result into the database.
        
        Args:
            data: Benchmark data as a dictionary
        """
        # Ensure required fields are present
        required_fields = ['model_name', 'model_version', 'task_type', 
                          'dataset', 'metric']
        
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field '{field}'")
        
        # Convert timestamp to datetime if it's a string
        if 'timestamp' in data and isinstance(data['timestamp'], str):
            try:
                data['timestamp'] = datetime.fromisoformat(data['timestamp'])
            except ValueError:
                data['timestamp'] = datetime.now()
        elif 'timestamp' not in data:
            data['timestamp'] = datetime.now()
        
        # Generate UUID if not provided
        if 'id' not in data:
            data['id'] = str(uuid.uuid4())
        
        # Prepare fields and placeholders
        fields = []
        placeholders = []
        values = {}
        
        for k, v in data.items():
            fields.append(k)
            placeholders.append(f"%({k})s")
            
            # Convert dict objects to JSONB
            if k in ('hardware_config', 'metadata') and isinstance(v, dict):
                values[k] = json.dumps(v)
            else:
                values[k] = v
        
        # Build query
        query = f"""
            INSERT INTO model_benchmarks ({', '.join(fields)})
            VALUES ({', '.join(placeholders)})
        """
        
        self.execute(query, values)
        logger.info(f"Inserted benchmark data for {data['model_name']} v{data['model_version']}")
        
    def get_model_benchmarks(self, model_name: str, limit: int = 100) -> pd.DataFrame:
        """
        Retrieve all benchmarks for a specific model.
        
        Args:
            model_name: Name of the model to query
            limit: Maximum number of rows to return
            
        Returns:
            Benchmark results as a DataFrame
        """
        query = """
            SELECT * FROM model_benchmarks 
            WHERE model_name = %(model_name)s
            ORDER BY timestamp DESC
            LIMIT %(limit)s
        """
        
        return self.execute_df(query, {
            "model_name": model_name,
            "limit": limit
        })
    
    def get_top_models(self, task_type: str, metric: str, 
                      limit: int = 10) -> pd.DataFrame:
        """
        Get the top-performing models for a specific task and metric.
        
        Args:
            task_type: Type of task (e.g., 'image_classification')
            metric: Performance metric to sort by
            limit: Maximum number of results to return
            
        Returns:
            Top models as a DataFrame
        """
        query = """
            SELECT 
                model_name, 
                model_version,
                MAX(score) as best_score,
                AVG(runtime_ms) as avg_runtime_ms,
                MAX(timestamp) as last_benchmark
            FROM model_benchmarks 
            WHERE task_type = %(task_type)s
              AND metric = %(metric)s
            GROUP BY model_name, model_version
            ORDER BY best_score DESC
            LIMIT %(limit)s
        """
        
        return self.execute_df(query, {
            "task_type": task_type,
            "metric": metric,
            "limit": limit
        })
        

def get_database_manager(db_type: str = 'clickhouse', **config) -> DatabaseManager:
    """
    Factory function to get the appropriate database manager.
    
    Args:
        db_type: Type of database ('clickhouse' or 'timescaledb')
        config: Configuration parameters for the database
        
    Returns:
        Database manager instance
    """
    if db_type == 'clickhouse':
        return ClickHouseManager(**config)
    elif db_type == 'timescaledb':
        return TimescaleDBManager(**config)
    else:
        raise ValueError(f"Unsupported database type: {db_type}. Please use 'clickhouse' or 'timescaledb'.")