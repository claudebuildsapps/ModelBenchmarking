# ModelBenchmarking

A comprehensive tool for benchmarking AI models with integrated web scraping and image processing capabilities.

## Overview

ModelBenchmarking is designed to evaluate and compare performance metrics of various AI models. The system collects benchmark data through intelligent web scraping and image reading, storing results in a ClickHouse database for high-performance analytical processing.

## Architecture

- **Python-first approach** with performance-critical components optimized in Rust
- **ClickHouse database** for high-performance analytical queries
- **Web scraping infrastructure** for collecting model information and results
- **Image processing capabilities** for extracting visual benchmark data

## Database Setup

### ClickHouse Installation

1. Install ClickHouse:

```bash
# For macOS with Homebrew
brew install clickhouse

# For Ubuntu
sudo apt-get install apt-transport-https ca-certificates
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv E0C56BD4
echo "deb https://packages.clickhouse.com/deb stable main" | sudo tee /etc/apt/sources.list.d/clickhouse.list
sudo apt-get update
sudo apt-get install clickhouse-server clickhouse-client
```

2. Start ClickHouse server:

```bash
# For macOS with Homebrew
clickhouse start

# For Ubuntu
sudo service clickhouse-server start
```

3. Verify installation:

```bash
clickhouse-client --query "SELECT 1"
```

### Connecting with Python

1. Install the required packages:

```bash
pip install clickhouse-driver pandas
```

2. Basic connection example:

```python
from clickhouse_driver import Client

client = Client(host='localhost')
result = client.execute('SHOW DATABASES')
print(result)
```

## Development Setup

1. Clone the repository:

```bash
git clone https://github.com/yourusername/ModelBenchmarking.git
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

4. Configure database connection in `config/settings.py`

## Project Structure

```
ModelBenchmarking/
├── config/             # Configuration files
│   └── settings.py     # Settings including database connection
├── data/               # Data storage directory
├── scripts/            # Utility scripts
├── src/                # Source code
│   ├── __init__.py
│   ├── benchmarking.py # Core benchmarking logic
│   ├── database.py     # Database interaction 
│   ├── models.py       # Data models
│   └── scrapers.py     # Web scraping functionality
└── tests/              # Test suite
    └── __init__.py
```

## Future Development

- Port performance-critical components to Rust
- Expand scraping capabilities for diverse AI model sources
- Implement parallel benchmarking for increased throughput