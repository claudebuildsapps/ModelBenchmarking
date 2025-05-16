#!/bin/bash

# This script removes the quarantine attribute from the ClickHouse binary
# This is a developer-friendly approach to bypass Gatekeeper for trusted applications

CLICKHOUSE_BIN="/opt/homebrew/Caskroom/clickhouse/25.3.2.39-lts/clickhouse-macos-aarch64"

echo "==================================================="
echo "  ClickHouse Quarantine Removal"
echo "==================================================="
echo ""
echo "This script will remove the quarantine attribute from ClickHouse"
echo "allowing it to run without security prompts."
echo ""
echo "You will be prompted for your password to run the sudo command."
echo ""
echo "Press ENTER to continue or CTRL+C to cancel..."
read

# Remove the quarantine attribute
echo "Removing quarantine attribute from $CLICKHOUSE_BIN..."
sudo xattr -d com.apple.quarantine "$CLICKHOUSE_BIN"

if [ $? -eq 0 ]; then
    echo ""
    echo "SUCCESS! Quarantine attribute removed."
    echo "You can now run: ./scripts/start_clickhouse.sh"
else
    echo ""
    echo "Failed to remove quarantine attribute."
    echo "Please make sure you entered the correct password."
fi