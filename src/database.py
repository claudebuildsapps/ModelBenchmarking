from clickhouse_driver import Client
import pandas as pd
from typing import Dict, List, Any, Optional

class ClickHouseManager:
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
        self.client = Client(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )
        
    def execute(self, query: str, params: Optional[Dict] = None) -> List:
        """
        Execute a ClickHouse query.
        
        Args:
            query: SQL query to execute
            params: Query parameters
            
        Returns:
            Query result as a list
        """
        return self.client.execute(query, params or {})
    
    def execute_df(self, query: str, params: Optional[Dict] = None) -> pd.DataFrame:
        """
        Execute a query and return the result as a pandas DataFrame.
        
        Args:
            query: SQL query to execute
            params: Query parameters
            
        Returns:
            Query result as a pandas DataFrame
        """
        result = self.execute(query, params)
        columns = [c[0] for c in self.client.execute(f"DESC ({query})", params)]
        return pd.DataFrame(result, columns=columns)
    
    def create_benchmark_table(self) -> None:
        """
        Create the main table for storing benchmark results.
        """
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
        
    def insert_benchmark(self, data: Dict[str, Any]) -> None:
        """
        Insert a benchmark result into the database.
        
        Args:
            data: Benchmark data as a dictionary
        """
        query = """
            INSERT INTO model_benchmarks (
                model_name, model_version, task_type, dataset, 
                metric, score, runtime_ms, memory_usage_mb,
                hardware_config, parameters_count, source_url, metadata
            ) VALUES
        """
        self.execute(query, data)
        
    def get_model_benchmarks(self, model_name: str) -> pd.DataFrame:
        """
        Retrieve all benchmarks for a specific model.
        
        Args:
            model_name: Name of the model to query
            
        Returns:
            Benchmark results as a DataFrame
        """
        query = "SELECT * FROM model_benchmarks WHERE model_name = %(model_name)s"
        return self.execute_df(query, {"model_name": model_name})
    
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
            GROUP BY model_name, model_version
            ORDER BY best_score DESC
            LIMIT %(limit)s
        """
        return self.execute_df(query, {
            "task_type": task_type,
            "limit": limit
        })