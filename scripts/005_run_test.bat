@echo off
REM Check if we're already in the project root or in scripts directory
if exist "src\" (
    REM We're in project root
    pytest --html=test_reports\report.html --self-contained-html tests\
) else (
    REM We're in scripts directory, go up one level
    cd ..
    pytest --html=test_reports\report.html --self-contained-html tests\
)
