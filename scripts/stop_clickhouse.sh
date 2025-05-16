#!/bin/bash

# Configure paths
LOG_DIR="$HOME/clickhouse/logs"
PID_FILE="$LOG_DIR/clickhouse.pid"

# Check if PID file exists
if [ ! -f "$PID_FILE" ]; then
    echo "ClickHouse PID file not found. Server may not be running."
    exit 1
fi

# Get the PID from the file
PID=$(cat "$PID_FILE")

# Check if the process is running
if ! ps -p $PID > /dev/null; then
    echo "ClickHouse server (PID $PID) is not running."
    rm -f "$PID_FILE"
    exit 1
fi

# Stop the process
echo "Stopping ClickHouse server (PID $PID)..."
kill $PID

# Wait for the process to stop
for i in {1..10}; do
    if ! ps -p $PID > /dev/null; then
        echo "ClickHouse server stopped successfully."
        rm -f "$PID_FILE"
        exit 0
    fi
    sleep 1
done

# Force kill if it doesn't stop
echo "ClickHouse server did not stop gracefully. Forcing termination..."
kill -9 $PID
if ! ps -p $PID > /dev/null; then
    echo "ClickHouse server terminated."
    rm -f "$PID_FILE"
    exit 0
else
    echo "Failed to terminate ClickHouse server."
    exit 1
fi