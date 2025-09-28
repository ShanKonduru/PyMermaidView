@echo off
REM Check if we're already in the project root or in scripts directory
if exist "src\" (
    REM We're in project root
    python main.py
) else (
    REM We're in scripts directory, go up one level
    cd ..
    python main.py
)
