#!/usr/bin/env python3
"""
Example benchmark script to demonstrate basic usage of the ModelBenchmarking system.
"""

import sys
import os
import time
import random
import argparse
import pandas as pd

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.benchmarking import ModelBenchmark
from src.database import get_database_manager
from config.settings import DATABASE_CONFIG

def dummy_model_1(inputs):
    """
    Dummy model that simply multiplies inputs by 2.
    Used for demonstration purposes.
    """
    time.sleep(0.01)  # Simulate some processing time
    return [x * 2 for x in inputs]

def dummy_model_2(inputs):
    """
    Dummy model that adds 5 to inputs.
    Used for demonstration purposes.
    """
    time.sleep(0.02)  # Simulate some processing time
    return [x + 5 for x in inputs]

def dummy_model_3(inputs):
    """
    Dummy model with random errors.
    Used for demonstration purposes.
    """
    time.sleep(0.015)  # Simulate some processing time
    return [x * 2 if random.random() > 0.2 else x * 2 + 1 for x in inputs]

def run_single_benchmark(db_manager):
    """Run a single model benchmark example"""
    print("Running single model benchmark example...")
    
    # Initialize benchmark system
    benchmark = ModelBenchmark(db_manager=db_manager)
    
    # Generate some test data
    test_inputs = list(range(1, 11))
    expected_outputs = [x * 2 for x in test_inputs]
    
    # Run benchmark
    result = benchmark.benchmark_model(
        model_name="dummy-model",
        model_version="0.1.0",
        task_type="basic-math",
        dataset="test-numbers",
        metric="accuracy",
        model_fn=dummy_model_1,
        inputs=test_inputs,
        expected_outputs=expected_outputs,
        parameters_count=10,
        source_url="https://example.com/dummy-model",
        metadata={"description": "A dummy model for testing"}
    )
    
    print(f"Benchmark complete!")
    print(f"Model: {result['model_name']} v{result['model_version']}")
    print(f"Score: {result['score']}")
    print(f"Runtime: {result['runtime_ms']:.2f} ms")
    print(f"Memory usage: {result['memory_usage_mb']:.2f} MB")
    print()
    
    return result

def compare_models(db_manager):
    """Compare multiple models example"""
    print("Running model comparison example...")
    
    # Initialize benchmark system
    benchmark = ModelBenchmark(db_manager=db_manager)
    
    # Generate some test data
    test_inputs = list(range(1, 21))
    expected_outputs = [x * 2 for x in test_inputs]
    
    # Define models to compare
    models = [
        {
            "name": "dummy-model-1",
            "version": "0.1.0",
            "function": dummy_model_1,
            "parameters_count": 10,
            "source_url": "https://example.com/dummy-model-1",
            "metadata": {"description": "Model that multiplies by 2"}
        },
        {
            "name": "dummy-model-2",
            "version": "0.1.0",
            "function": dummy_model_2,
            "parameters_count": 15,
            "source_url": "https://example.com/dummy-model-2",
            "metadata": {"description": "Model that adds 5"}
        },
        {
            "name": "dummy-model-3",
            "version": "0.1.0",
            "function": dummy_model_3,
            "parameters_count": 12,
            "source_url": "https://example.com/dummy-model-3",
            "metadata": {"description": "Model with random errors"}
        }
    ]
    
    # Run comparison
    results = benchmark.compare_models(
        models=models,
        task_type="basic-math",
        dataset="test-numbers",
        metric="accuracy",
        inputs=test_inputs,
        expected_outputs=expected_outputs
    )
    
    print(f"Comparison complete!")
    print(f"\nModels by score (best to worst):")
    for i, model in enumerate(results["by_score"], 1):
        print(f"{i}. {model['model_name']}: Score={model['score']:.2f}, Runtime={model['runtime_ms']:.2f}ms")
    
    print(f"\nModels by runtime (fastest to slowest):")
    for i, model in enumerate(results["by_runtime"], 1):
        print(f"{i}. {model['model_name']}: Runtime={model['runtime_ms']:.2f}ms, Score={model['score']:.2f}")
    
    return results

def retrieve_benchmark_data(db_manager):
    """Retrieve previously stored benchmark data"""
    print("\nRetrieving benchmark data from database...")
    
    # Initialize benchmark system
    benchmark = ModelBenchmark(db_manager=db_manager)
    
    # Get data for dummy model 1
    results = benchmark.get_model_benchmarks("dummy-model-1")
    
    if isinstance(results, pd.DataFrame) and not results.empty:
        print(f"Found {len(results)} benchmark results for dummy-model-1:")
        for i, (_, result) in enumerate(results.iterrows(), 1):
            print(f"{i}. Task: {result['task_type']}, Score: {result['score']:.2f}, Runtime: {result['runtime_ms']:.2f}ms")
    elif isinstance(results, list) and results:
        print(f"Found {len(results)} benchmark results for dummy-model-1:")
        for i, result in enumerate(results, 1):
            print(f"{i}. Task: {result['task_type']}, Score: {result['score']:.2f}, Runtime: {result['runtime_ms']:.2f}ms")
    else:
        print("No results found for dummy-model-1")
    
    # Get top models for basic-math task
    top_models = benchmark.get_top_models("basic-math", "accuracy")
    
    if isinstance(top_models, pd.DataFrame) and not top_models.empty:
        print(f"\nTop models for 'basic-math' task:")
        for i, (_, model) in enumerate(top_models.iterrows(), 1):
            print(f"{i}. {model['model_name']} v{model['model_version']}: Best score={model['best_score']:.2f}")
    elif isinstance(top_models, list) and top_models:
        print(f"\nTop models for 'basic-math' task:")
        for i, model in enumerate(top_models, 1):
            print(f"{i}. {model['model_name']} v{model['model_version']}: Best score={model['best_score']:.2f}")
    else:
        print("\nNo top models found for 'basic-math' task")
        
    return results

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Run example benchmarks")
    parser.add_argument(
        "--db-type", 
        choices=["clickhouse", "timescaledb"],
        default=DATABASE_CONFIG["type"],
        help="Database type to use"
    )
    parser.add_argument("--host", help="Database host")
    parser.add_argument("--port", type=int, help="Database port")
    parser.add_argument("--user", help="Database username")
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
    
    # Get appropriate database configuration
    db_config = {**DATABASE_CONFIG.get(args.db_type, {}), **config}
    
    try:
        # Initialize database manager
        db_manager = get_database_manager(args.db_type, **db_config)
        
        # Make sure database is set up
        from scripts.setup_database import setup_database
        setup_database(args.db_type, **db_config)
        
        # Run examples
        single_result = run_single_benchmark(db_manager)
        comparison_results = compare_models(db_manager)
        stored_results = retrieve_benchmark_data(db_manager)
        
        print("\nAll examples completed successfully!")
    except ImportError as e:
        print(f"\nError: Required package not installed: {str(e)}")
        
        if args.db_type == "clickhouse":
            print("\nTo install ClickHouse driver, run: pip install clickhouse-driver")
        elif args.db_type == "timescaledb":
            print("\nTo install TimescaleDB driver, run: pip install psycopg2-binary")
            
        sys.exit(1)
    except Exception as e:
        print(f"\nError running examples: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()