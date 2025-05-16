#!/bin/bash

# Check if ClickHouse is already running
if pgrep -f "clickhouse-macos-aarch64 server" > /dev/null; then
    echo "ClickHouse server is already running"
    exit 0
fi

# Configure paths
CLICKHOUSE_BIN="/opt/homebrew/Caskroom/clickhouse/25.3.2.39-lts/clickhouse-macos-aarch64"
CONFIG_DIR="$HOME/clickhouse/config"
LOG_DIR="$HOME/clickhouse/logs"
DATA_DIR="$HOME/clickhouse/data"

# Create directories if they don't exist
mkdir -p "$LOG_DIR" "$DATA_DIR/tmp"

# Check if the binary exists
if [ ! -f "$CLICKHOUSE_BIN" ]; then
    echo "ERROR: ClickHouse binary not found at $CLICKHOUSE_BIN"
    echo "Please install ClickHouse using: brew install --cask clickhouse"
    exit 1
fi

# Display instructions for first-time launch
echo "====================== IMPORTANT ======================"
echo "If this is your first time running ClickHouse, macOS security"
echo "may prevent it from starting. If you encounter this issue:"
echo ""
echo "Please run the following command to approve ClickHouse:"
echo "  ./scripts/run.sh approve-clickhouse"
echo ""
echo "This will trigger the approval dialog directly."
echo "======================================================="
echo ""

# Start ClickHouse server in the background
echo "Starting ClickHouse server..."
nohup "$CLICKHOUSE_BIN" server --config-file="$CONFIG_DIR/config.xml" > "$LOG_DIR/clickhouse-start.log" 2>&1 &

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
    echo "Failed to start ClickHouse server. This might be due to macOS security."
    echo ""
    echo "Try the following:"
    echo "1. Run this command to check logs: cat $LOG_DIR/clickhouse-start.log"
    echo "2. Run: sudo xattr -d com.apple.quarantine $CLICKHOUSE_BIN"
    echo "3. Run this script again"
    
    # Check if Gatekeeper is blocking it
    if grep -q "Security" "$LOG_DIR/clickhouse-start.log" 2>/dev/null; then
        echo ""
        echo "Apple's security policy is blocking ClickHouse. Try running:"
        echo "sudo xattr -d com.apple.quarantine $CLICKHOUSE_BIN"
    fi
    
    exit 1
fi