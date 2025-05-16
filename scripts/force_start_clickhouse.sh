#!/bin/bash

# This script attempts to start ClickHouse even if quarantine is present,
# by directly executing the binary with explicit server parameters

# Configure paths
CLICKHOUSE_BIN="/opt/homebrew/Caskroom/clickhouse/25.3.2.39-lts/clickhouse-macos-aarch64"
CONFIG_DIR="$HOME/clickhouse/config"
LOG_DIR="$HOME/clickhouse/logs"
DATA_DIR="$HOME/clickhouse/data"

# Create directories if they don't exist
mkdir -p "$LOG_DIR" "$DATA_DIR/tmp"

# Check if ClickHouse is already running
if pgrep -f "clickhouse-macos-aarch64 server" > /dev/null; then
    echo "ClickHouse server is already running"
    exit 0
fi

# Check if the binary exists
if [ ! -f "$CLICKHOUSE_BIN" ]; then
    echo "ERROR: ClickHouse binary not found at $CLICKHOUSE_BIN"
    echo "Please install ClickHouse using: brew install --cask clickhouse"
    exit 1
fi

echo "Starting ClickHouse server directly with explicit parameters..."
echo "This bypasses some of the normal startup procedures"

# Start ClickHouse server with explicit parameters
# This may sometimes work even when quarantine is active
nohup "$CLICKHOUSE_BIN" server \
  --config-file="$CONFIG_DIR/config.xml" \
  --pid-file="$LOG_DIR/clickhouse.pid" \
  --http_port=8123 \
  --tcp_port=9000 \
  --log-file="$LOG_DIR/clickhouse-server.log" \
  > "$LOG_DIR/clickhouse-start.log" 2>&1 &

# Store the process ID for later use
echo $! > "$LOG_DIR/clickhouse.pid"

# Wait a moment for the server to start
sleep 5

# Check if the server is running
if pgrep -f "clickhouse-macos-aarch64 server" > /dev/null; then
    echo "ClickHouse server started successfully!"
    echo "PID: $(cat $LOG_DIR/clickhouse.pid)"
    echo "HTTP Interface: http://localhost:8123"
    echo "Native Interface: localhost:9000"
    echo ""
    echo "To stop the server, run: ./scripts/stop_clickhouse.sh"
else
    echo "Failed to start ClickHouse server."
    echo ""
    echo "Please run this command in your terminal to remove the quarantine:"
    echo "sudo xattr -d com.apple.quarantine $CLICKHOUSE_BIN"
    
    # Show the startup log
    echo ""
    echo "=== Startup log ==="
    cat "$LOG_DIR/clickhouse-start.log"
    
    exit 1
fi