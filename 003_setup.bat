@echo off
echo "Setting up PyMermaidView project..."

echo "Upgrading pip..."
python -m pip install --upgrade pip

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Installing Playwright browsers for image generation..."
playwright install chromium

echo "Creating output directory..."
if not exist "output" mkdir output

echo "Creating templates directory..."
if not exist "templates" mkdir templates

echo "Setup complete! You can now run:"
echo "  python main.py                    - Run demonstrations"
echo "  python -m src.mermaid_cli --help  - See CLI options"
echo "  python -m pytest tests/           - Run tests"
