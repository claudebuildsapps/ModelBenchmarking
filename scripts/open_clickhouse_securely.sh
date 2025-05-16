#!/bin/bash

# This script uses AppleScript to open the ClickHouse binary in a way
# that triggers the security dialog with an "Open" button option

CLICKHOUSE_BIN="/opt/homebrew/Caskroom/clickhouse/25.3.2.39-lts/clickhouse-macos-aarch64"

echo "==================================================="
echo "  ClickHouse Security Approval Helper"
echo "==================================================="
echo ""
echo "This script will open a Finder window with the ClickHouse binary."
echo ""
echo "INSTRUCTIONS:"
echo "1. When Finder opens, RIGHT-CLICK on the clickhouse-macos-aarch64 file"
echo "2. Select 'Open' from the context menu"
echo "3. When the security dialog appears, click 'Open'"
echo ""
echo "Press ENTER to continue or CTRL+C to cancel..."
read

# Use AppleScript to open the containing folder and select the binary
osascript <<EOF
tell application "Finder"
  activate
  reveal POSIX file "$CLICKHOUSE_BIN"
end tell
EOF

echo ""
echo "Finder should now be open showing the ClickHouse binary."
echo "Please RIGHT-CLICK on the binary and select 'Open'."
echo ""
echo "After approving ClickHouse in the security dialog, you can run:"
echo "./scripts/start_clickhouse.sh"