@echo off
echo ========================================
echo 🚀 Starting PyMermaidView Web Interface
echo ========================================
echo.
echo 📋 Features:
echo   • Interactive Mermaid editor
echo   • Real-time preview
echo   • Multiple theme generation
echo   • Template library
echo   • Syntax validation
echo.
echo 🌐 Opening web interface at: http://localhost:8501
echo 💡 Press Ctrl+C to stop the server
echo.
pause
echo Starting Streamlit server...

REM Detect if we're in project root or scripts directory
if exist "src\" (
	REM In project root
	python -m streamlit run streamlit_app.py
) else (
	REM Likely in scripts directory, go up to project root
	cd ..
	python -m streamlit run streamlit_app.py
)