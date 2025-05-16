#!/bin/bash
# Run script for ModelBenchmarking

set -e

# Function to display help
show_help() {
    echo "ModelBenchmarking Run Script"
    echo "----------------------------"
    echo "Usage: ./run.sh COMMAND [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  setup              Set up the database"
    echo "  example            Run the example benchmark"
    echo "  install            Install dependencies"
    echo "  tui                Run the terminal user interface"
    echo "  start-db           Start the ClickHouse database server"
    echo "  stop-db            Stop the ClickHouse database server"
    echo "  approve-clickhouse Prompt for macOS approval of ClickHouse binary"
    echo ""
    echo "Options:"
    echo "  --db-type     Database type: 'clickhouse' or 'timescaledb' (default is clickhouse)"
    echo "  --host        Database host (default is localhost)"
    echo "  --port        Database port (default depends on database type)"
    echo "  --user        Database username"
    echo "  --password    Database password"
    echo "  --database    Database name"
    echo ""
    echo "Examples:"
    echo "  ./run.sh install                      # Install all dependencies"
    echo "  ./run.sh setup --db-type clickhouse   # Set up ClickHouse database"
    echo "  ./run.sh setup --db-type timescaledb  # Set up TimescaleDB database"
    echo "  ./run.sh example                      # Run example benchmark with default settings"
    echo "  ./run.sh tui                          # Run the terminal user interface"
    echo "  ./run.sh start-db                     # Start the ClickHouse database server"
}

# Function to install dependencies
install_deps() {
    echo "Installing dependencies..."
    pip install -r requirements.txt
    echo "Done!"
}

# Parse command
if [ $# -lt 1 ]; then
    show_help
    exit 1
fi

COMMAND=$1
shift

# Process command
case "$COMMAND" in
    "setup")
        # Extract arguments for setup
        ARGS=""
        while [[ "$#" -gt 0 ]]; do
            case "$1" in
                --db-type|--host|--port|--user|--password|--database)
                    ARGS="$ARGS $1 $2"
                    shift 2
                    ;;
                *)
                    echo "Unknown option: $1"
                    show_help
                    exit 1
                    ;;
            esac
        done
        
        echo "Setting up database..."
        python scripts/setup_database.py $ARGS
        ;;

    "example")
        # Extract arguments for example
        ARGS=""
        while [[ "$#" -gt 0 ]]; do
            case "$1" in
                --db-type|--host|--port|--user|--password|--database)
                    ARGS="$ARGS $1 $2"
                    shift 2
                    ;;
                *)
                    echo "Unknown option: $1"
                    show_help
                    exit 1
                    ;;
            esac
        done
        
        echo "Running example benchmark..."
        python scripts/example_benchmark.py $ARGS
        ;;
        
    "tui")
        # Extract arguments for tui
        ARGS=""
        while [[ "$#" -gt 0 ]]; do
            case "$1" in
                --db-type|--host|--port|--user|--password|--database)
                    ARGS="$ARGS $1 $2"
                    shift 2
                    ;;
                *)
                    echo "Unknown option: $1"
                    show_help
                    exit 1
                    ;;
            esac
        done
        
        echo "Starting Terminal User Interface..."
        python scripts/tui.py $ARGS
        ;;
        
    "start-db")
        echo "Starting ClickHouse database server..."
        scripts/start_clickhouse.sh
        ;;
        
    "stop-db")
        echo "Stopping ClickHouse database server..."
        scripts/stop_clickhouse.sh
        ;;
        
    "approve-clickhouse")
        echo "Triggering macOS approval dialog for ClickHouse..."
        scripts/prompt_clickhouse_approval.sh
        ;;
        
    "install")
        install_deps
        ;;
        
    "help")
        show_help
        ;;
        
    *)
        echo "Unknown command: $COMMAND"
        show_help
        exit 1
        ;;
esac