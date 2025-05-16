#!/bin/bash
#
# This script helps users approve the ClickHouse binary through macOS security
# by opening the binary directly, which will trigger the security prompt.

CLICKHOUSE_BIN="/opt/homebrew/Caskroom/clickhouse/25.3.2.39-lts/clickhouse-macos-aarch64"

echo "==================================================="
echo "  ModelBenchmarking - ClickHouse Approval Helper"
echo "==================================================="
echo ""
echo "This script will help you approve the ClickHouse binary"
echo "through macOS security by triggering the approval dialog."
echo ""
echo "When prompted with:"
echo ""
echo "\"macOS cannot verify the developer of 'clickhouse-macos-aarch64'.\""
echo "or"
echo "\"Apple cannot check 'clickhouse-macos-aarch64' for malicious software.\""
echo ""
echo "Please click 'Open' or 'Open Anyway' to approve it."
echo ""
echo "Press ENTER to continue or CTRL+C to cancel..."
read

echo "Opening ClickHouse binary to trigger approval dialog..."
echo "(You'll see a security dialog pop up - please click 'Open')"
echo ""

# Try to run the binary with version command to trigger the dialog
"$CLICKHOUSE_BIN" version

echo ""
echo "If you approved the binary in the security dialog, ClickHouse should now be ready to use."
echo "You can now run: ./scripts/start_clickhouse.sh"
echo ""

# Check if the binary seems to be approved
if [ $? -eq 0 ]; then
    echo "SUCCESS! The ClickHouse binary appears to be approved."
    echo "You can now run: ./scripts/start_clickhouse.sh"
else
    echo "The binary might still be blocked."
    echo "Please check System Preferences > Security & Privacy > General"
    echo "and click 'Open Anyway' if there's a message about clickhouse-macos-aarch64."
fi