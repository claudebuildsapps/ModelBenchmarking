"""
Configuration settings for the ModelBenchmarking application.
"""

import os
from typing import Dict, Any

# Database settings
DATABASE_CONFIG = {
    "type": "clickhouse",  # Options: "clickhouse", "timescaledb"
    "clickhouse": {
        "host": os.environ.get("CLICKHOUSE_HOST", "localhost"),
        "port": int(os.environ.get("CLICKHOUSE_PORT", 9000)),
        "user": os.environ.get("CLICKHOUSE_USER", "default"),
        "password": os.environ.get("CLICKHOUSE_PASSWORD", ""),
        "database": os.environ.get("CLICKHOUSE_DATABASE", "benchmark_db")
    },
    "timescaledb": {
        "host": os.environ.get("TIMESCALEDB_HOST", "localhost"),
        "port": int(os.environ.get("TIMESCALEDB_PORT", 5432)),
        "user": os.environ.get("TIMESCALEDB_USER", "postgres"),
        "password": os.environ.get("TIMESCALEDB_PASSWORD", ""),
        "database": os.environ.get("TIMESCALEDB_DATABASE", "benchmark_db")
    }
}

# Web scraping settings
SCRAPING_CONFIG = {
    "user_agent": "ModelBenchmarking Research Tool/1.0",
    "request_timeout": 15,  # seconds
    "retry_attempts": 3,
    "retry_delay": 2,  # seconds
    "use_selenium": True,
    "headless": True,
    "rate_limit": {
        "requests_per_minute": 20
    }
}

# Benchmarking settings
BENCHMARK_CONFIG = {
    "timeout": 600,  # seconds
    "memory_limit": 8192,  # MB
    "save_outputs": False,
    "parallel_runs": 1
}

# Path settings
PATHS = {
    "data_dir": os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data")),
    "cache_dir": os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "cache")),
    "results_dir": os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "results"))
}

# Ensure directories exist
for dir_path in PATHS.values():
    os.makedirs(dir_path, exist_ok=True)

# Logging settings
LOGGING_CONFIG = {
    "level": os.environ.get("LOG_LEVEL", "INFO"),
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": os.path.join(PATHS["data_dir"], "app.log")
}

# Default language models to benchmark
DEFAULT_MODELS = [
    {
        "name": "gpt-3.5-turbo",
        "source": "openai",
        "tasks": ["text-generation", "summarization", "question-answering"]
    },
    {
        "name": "gpt-4",
        "source": "openai",
        "tasks": ["text-generation", "summarization", "question-answering"]
    },
    {
        "name": "claude-3-opus",
        "source": "anthropic",
        "tasks": ["text-generation", "summarization", "question-answering"]
    },
    {
        "name": "llama-3-70b",
        "source": "meta",
        "tasks": ["text-generation", "summarization", "question-answering"]
    }
]

# Default datasets
DEFAULT_DATASETS = [
    {
        "name": "MMLU",
        "task": "question-answering",
        "metrics": ["accuracy"]
    },
    {
        "name": "HumanEval",
        "task": "code-generation",
        "metrics": ["pass@1", "pass@10"]
    },
    {
        "name": "GSM8K",
        "task": "mathematical-reasoning",
        "metrics": ["accuracy"]
    }
]

def get_settings() -> Dict[str, Any]:
    """
    Get all application settings.
    
    Returns:
        Dictionary with all configuration settings
    """
    return {
        "database": DATABASE_CONFIG,
        "scraping": SCRAPING_CONFIG,
        "benchmark": BENCHMARK_CONFIG,
        "paths": PATHS,
        "logging": LOGGING_CONFIG,
        "default_models": DEFAULT_MODELS,
        "default_datasets": DEFAULT_DATASETS
    }