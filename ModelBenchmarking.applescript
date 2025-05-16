-- Model Benchmarking App Launcher
-- This script launches the Model Benchmarking TUI in a Terminal window

on run
    try
        tell application "Terminal"
            -- Get the absolute path to the script directory
            set projectPath to "/Users/joshkornreich/Documents/Code/ModelBenchmarking"
            
            -- Open a new terminal window and navigate to the project directory
            do script "cd \"" & projectPath & "\" && ./scripts/run.sh tui"
            
            -- Set the title of the terminal window
            set custom title of front window to "Model Benchmarking"
            
            -- Activate Terminal to bring it to the front
            activate
        end tell
    on error errMsg
        -- If there's a permissions error, open System Preferences
        display dialog "ModelBenchmarking needs permission to control Terminal. Click OK to open Security & Privacy settings." buttons {"OK"} default button "OK" with icon caution
        
        -- Display detailed instructions first
        display dialog "Please follow these steps:

1. In the Security & Privacy settings window that opens next
2. Click on 'Privacy & Security' in the sidebar
3. Scroll down and click on 'Automation'
4. Find 'ModelBenchmarking' in the list
5. Check the box next to 'Terminal'
6. Close System Settings and try running the app again" buttons {"Show Settings"} default button "Show Settings" with icon note giving up after 300
        
        -- Open security settings after user clicks button
        do shell script "open 'x-apple.systempreferences:com.apple.preference.security'"
    end try
end run