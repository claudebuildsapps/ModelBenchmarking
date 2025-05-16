# ModelBenchmarking

A comprehensive tool for benchmarking AI models with integrated web scraping and image processing capabilities.

## Overview

ModelBenchmarking is designed to evaluate and compare performance metrics of various AI models. The system collects benchmark data through intelligent web scraping and image reading, storing results in a database (SQLite, ClickHouse, or TimescaleDB) for high-performance analytical processing.

## Architecture

- **Python-first approach** with performance-critical components optimized in Rust
- **Multi-database support**:
  - **ClickHouse** for high-speed analytical queries and massive datasets
  - **TimescaleDB** for time-series optimized benchmarking data
- **Web scraping infrastructure** for collecting model information and results
- **Image processing capabilities** for extracting visual benchmark data

## Quick Start

1. Clone the repository:

```bash
git clone https://github.com/claudebuildsapps/ModelBenchmarking.git
cd ModelBenchmarking
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set up the database (SQLite is default):

```bash
python scripts/setup_database.py
```

5. Run the example benchmark:

```bash
python scripts/example_benchmark.py
```

## Database Configuration

This project supports three database backends:

### SQLite (Default)

The project uses SQLite by default for simplicity. No additional setup is required beyond running:

```bash
python scripts/setup_database.py
```

This creates a SQLite database file at `data/benchmarks.db`.

### ClickHouse

For high-performance analytical workloads with massive datasets:

1. Install ClickHouse
2. Install the Python driver: `pip install clickhouse-driver`
3. Set up the database:

```bash
python scripts/setup_database.py --db-type clickhouse [--host HOSTNAME] [--port PORT]
```

### TimescaleDB

For time-series optimized benchmarking data:

1. Install PostgreSQL with TimescaleDB extension
2. Install the Python driver: `pip install psycopg2-binary`
3. Set up the database:

```bash
python scripts/setup_database.py --db-type timescaledb [--host HOSTNAME] [--port PORT] [--user USERNAME] [--password PASSWORD] [--database DB_NAME]
```

## Usage

### Running a Benchmark

```python
from src.database import get_database_manager
from src.benchmarking import ModelBenchmark

# Initialize with your preferred database backend
db = get_database_manager("sqlite")  # or "clickhouse" or "timescaledb"
benchmark = ModelBenchmark(db_manager=db)

# Define a model function to benchmark
def my_model(inputs):
    # Your model logic here
    return [x * 2 for x in inputs]

# Run the benchmark
result = benchmark.benchmark_model(
    model_name="my-model",
    model_version="1.0.0",
    task_type="classification",
    dataset="test-dataset",
    metric="accuracy",
    model_fn=my_model,
    inputs=test_inputs,
    expected_outputs=expected_outputs
)

print(f"Benchmark result: {result}")
```

### Comparing Multiple Models

```python
models = [
    {
        "name": "model-a",
        "version": "1.0.0",
        "function": model_a_function
    },
    {
        "name": "model-b",
        "version": "1.0.0",
        "function": model_b_function
    }
]

results = benchmark.compare_models(
    models=models,
    task_type="classification",
    dataset="test-dataset",
    metric="accuracy",
    inputs=test_inputs,
    expected_outputs=expected_outputs
)

# Results are sorted by score and runtime
print(f"Best model by score: {results['by_score'][0]['model_name']}")
print(f"Fastest model: {results['by_runtime'][0]['model_name']}")
```

## Web Scraping Features

The system includes web scraping capabilities to collect benchmark data from popular sources:

- **PaperWithCode**: Scrape benchmark results from research papers
- **HuggingFace**: Access model metrics from the Hugging Face model hub

Example:

```python
from src.scrapers import HuggingFaceScraper

# Initialize scraper
scraper = HuggingFaceScraper()

# Get popular models for a specific task
models = scraper.get_popular_models(task="text-classification", limit=5)
for model in models:
    print(f"Model: {model['name']}, Downloads: {model['downloads']}")
```

## Project Structure

```
ModelBenchmarking/
├── config/             # Configuration files
│   └── settings.py     # Settings including database configuration
├── data/               # Data storage directory
├── scripts/            # Utility scripts
│   ├── setup_database.py    # Database setup script
│   └── example_benchmark.py # Example benchmark script  
├── src/                # Source code
│   ├── __init__.py
│   ├── benchmarking.py # Core benchmarking logic
│   ├── database.py     # Database interaction with multiple backends
│   ├── models.py       # Data models
│   └── scrapers.py     # Web scraping functionality
└── tests/              # Test suite
    └── __init__.py
```

## Command-line Usage

The project includes a convenient run script to perform common operations:

```bash
./scripts/run.sh COMMAND [OPTIONS]
```

Available commands:
- `setup`: Set up the database
- `example`: Run the example benchmark
- `install`: Install dependencies
- `tui`: Run the terminal user interface for database exploration
- `start-db`: Start the ClickHouse database server
- `stop-db`: Stop the ClickHouse database server

For example:
```bash
# Install dependencies
./scripts/run.sh install

# Start the ClickHouse database
./scripts/run.sh start-db

# Set up the database
./scripts/run.sh setup --db-type clickhouse

# Run the Terminal UI
./scripts/run.sh tui
```

Individual scripts support various command-line arguments:

```
python scripts/setup_database.py --help
```

Options:
- `--db-type`: Choose the database backend (sqlite, clickhouse, timescaledb)
- `--host`: Database host for ClickHouse/TimescaleDB
- `--port`: Database port
- `--user`: Database username
- `--password`: Database password
- `--database`: Database name
- `--db-path`: SQLite database file path

Similarly, `example_benchmark.py` and `tui.py` support the same database selection options.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Future Development

- Port performance-critical components to Rust
- Expand scraping capabilities for diverse AI model sources
- Implement parallel benchmarking for increased throughput
- Add visualization and reporting tools

## Implementation Details

### Architecture

The ModelBenchmarking project is designed with a modular architecture that separates core functionality into distinct components:

#### Core Components

1. **Benchmarking Engine** (`src/benchmarking.py`)
   - Provides `ModelBenchmark` class for measuring model performance
   - Captures execution time, memory usage, and accuracy metrics
   - Implements various evaluation metrics (accuracy, precision, recall, F1, MSE)
   - Records hardware configuration for reproducibility

2. **Multi-Database Layer** (`src/database.py`)
   - Abstract `DatabaseManager` interface for database operations
   - Concrete implementations for ClickHouse and TimescaleDB
   - Query functionality for retrieving and analyzing benchmark results
   - Schema design optimized for analytical queries and time-series data

3. **Web Scraping Infrastructure** (`src/scrapers.py`)
   - `BenchmarkScraper` base class with common scraping utilities
   - `PaperWithCodeScraper` for extracting model benchmarks from research papers
   - `HuggingFaceScraper` for collecting model metadata from Hugging Face
   - Support for both static page scraping and JavaScript-rendered content

4. **Data Models** (`src/models.py`)
   - Type-safe dataclasses with serialization/deserialization methods
   - `ModelMetadata` for model information
   - `BenchmarkResult` for storing performance metrics
   - `DatasetMetadata` for dataset information

#### User Interfaces

1. **Command-Line Tools**
   - `setup_database.py` for database initialization
   - `example_benchmark.py` for running sample benchmarks
   - `run.sh` wrapper script for common operations

2. **Terminal User Interface** (`scripts/tui.py`)
   - Curses-based text UI for database navigation
   - Model and benchmark exploration
   - Data scraping functionality
   - Real-time result filtering and sorting

### Database Schema

The system uses a specialized schema designed for efficient storage and querying of benchmark data:

1. **model_benchmarks**: Core table for storing benchmark results
   - Timestamp-indexed for time-series analysis
   - Includes model identifiers, task information, and performance metrics
   - Stores hardware configuration as structured data

2. **model_metadata**: Detailed information about models
   - Version tracking for model evolution
   - Parameter counts and architecture details
   - Source links and licensing information

3. **dataset_metadata**: Information about benchmark datasets
   - Task categorization
   - Citation information
   - Evaluation metrics support

### Performance Considerations

1. **Database Optimizations**
   - ClickHouse: Column-oriented storage for analytical queries
   - TimescaleDB: Time-series optimizations for temporal data
   - Indexing strategies for common query patterns

2. **Scraping Efficiency**
   - Rate limiting to respect website policies
   - Connection pooling and request caching
   - Parallel scraping where appropriate

3. **Benchmark Execution**
   - Resource isolation for accurate measurements
   - Hardware environment detection
   - Statistical aggregation of multiple runs