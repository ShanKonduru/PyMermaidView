# PyMermaidView 🎨

A comprehensive Python application for generating Mermaid diagrams using Object-Oriented Programming principles. Create beautiful flowcharts, export them to various formats, and manage them through an intuitive API or CLI interface.

## ✨ Features

- **Object-Oriented Design**: Clean, extensible architecture with proper OOP principles
- **Multiple Renderers**: Browser-based (Playwright) and online API renderers
- **Fluent Interface**: Intuitive builder pattern for creating flowcharts
- **Template System**: Pre-built templates and custom template creation
- **Format Support**: PNG, SVG, PDF, JPEG output formats
- **Theme Support**: Multiple Mermaid themes (default, dark, forest, etc.)
- **Validation**: Comprehensive syntax and structure validation
- **CLI Interface**: Powerful command-line tools for all operations
- **Import/Export**: JSON, YAML, CSV import/export capabilities
- **Error Handling**: Robust error handling with custom exceptions

## 🚀 Quick Start

### Installation (Windows)

1.  **Initialize git:**
    Run the `000_init.bat` file.

2.  **Create a virtual environment:**
    Run the `001_env.bat` file.

3.  **Activate the virtual environment:**
    Run the `002_activate.bat` file.

4.  **Install dependencies:**
    Run the `003_setup.bat` file. This will install all packages and set up Playwright.

5.  **Run demonstrations:**
    Run the `004_run.bat` file or `python main.py`.

## 🌐 Web Interface (NEW!)

PyMermaidView now includes a powerful **Streamlit-based web interface** for interactive diagram creation!

### 🚀 Launch Web Interface

**Method 1: One-Click Launch**
```bash
# Double-click or run:
start_web_ui.bat
```

**Method 2: Command Line**
```bash
streamlit run streamlit_app.py
# Opens at: http://localhost:8501
```

### ✨ Web Interface Features

- **📝 Interactive Editor**: Real-time Mermaid code editing with syntax highlighting
- **🔍 Live Validation**: Instant syntax checking and error feedback
- **🗂️ Template Gallery**: Built-in templates with one-click loading
- **⚡ Quick Builder**: Generate flowcharts from simple step descriptions
- **🎨 Multi-Theme Generation**: Create all 4 themes with one button
- **👁️ Live Preview**: See your diagrams as you create them
- **⬇️ Easy Downloads**: Direct download of high-resolution images
- **📱 Responsive Design**: Works on desktop and tablets

### 🎯 Perfect for:
- **Rapid Prototyping**: Quick flowchart creation and iteration
- **Team Collaboration**: Share the web interface for team diagram creation
- **Learning**: Interactive environment for learning Mermaid syntax
- **Presentations**: Generate multiple themed versions for different contexts

📖 **[Complete Web Interface Guide](WEB_UI_GUIDE.md)**

### Basic Programmatic Usage

```python
from src.mermaid_generator import MermaidGenerator, OutputFormat, MermaidTheme
from src.flowchart_builder import FlowchartBuilder, NodeShape, Direction

# Create a flowchart using the builder pattern
builder = (FlowchartBuilder("User Registration Process")
          .set_direction(Direction.TOP_BOTTOM)
          .add_start_end_node("start", "Start")
          .add_process_node("input", "User Input")
          .add_decision_node("validate", "Valid Data?")
          .add_process_node("save", "Save User")
          .add_process_node("error", "Show Error")
          .add_start_end_node("end", "End")
          .connect("start", "input")
          .connect("input", "validate")
          .connect_with_label("validate", "save", "Yes")
          .connect_with_label("validate", "error", "No")
          .connect("save", "end")
          .connect("error", "input"))

# Save to file
mermaid_file = builder.save_to_file("user_registration.mmd")

# Generate image
generator = MermaidGenerator()
generator.set_theme(MermaidTheme.FOREST).set_output_format(OutputFormat.PNG)
image_file = await generator.generate_from_file(mermaid_file)
```

### CLI Usage

```bash
# Create a quick flowchart
python -m src.mermaid_cli quick -t "Development Process" -s "Plan" -s "Code" -s "Test" -s "Deploy"

# Generate image from Mermaid file
python -m src.mermaid_cli generate flowchart.mmd -f svg -t dark

# Validate syntax
python -m src.mermaid_cli validate flowchart.mmd

# List available templates
python -m src.mermaid_cli template list
```

## 🏗️ Architecture Overview

### Core OOP Classes

- **`MermaidGenerator`**: Main orchestrator for diagram generation
- **`FlowchartBuilder`**: Fluent interface for building flowcharts  
- **`FlowchartNode`**: Represents individual nodes with styling
- **`FlowchartConnection`**: Represents connections between nodes
- **`TemplateManager`**: Template creation and management
- **`FlowchartValidator`**: Syntax and structure validation

### Design Patterns Implemented

1. **Builder Pattern**: Fluent flowchart construction
2. **Strategy Pattern**: Multiple renderer implementations  
3. **Template Method**: Customizable base behaviors
4. **Factory Pattern**: Node and connection creation
5. **Command Pattern**: CLI command structure

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage (use batch file)
005_run_code_cov.bat

# Run specific test types
python -m pytest tests/ -m "positive"
```

## 📖 Key CLI Commands

```bash
# Generate: Create images from Mermaid files
python -m src.mermaid_cli generate INPUT_FILE [OPTIONS]

# Create: Interactive flowchart creation
python -m src.mermaid_cli create --interactive

# Quick: Fast flowchart from steps  
python -m src.mermaid_cli quick -s "Step 1" -s "Step 2" -d

# Template: Work with templates
python -m src.mermaid_cli template list
python -m src.mermaid_cli template create TEMPLATE_NAME

# Validate: Check syntax
python -m src.mermaid_cli validate INPUT_FILE

# Info: Get file information
python -m src.mermaid_cli info INPUT_FILE
```

## 📁 Project Structure

- `src/`: Core application modules
  - `mermaid_generator.py`: Main generation engine
  - `flowchart_builder.py`: OOP flowchart construction
  - `mermaid_utils.py`: Utilities and templates
  - `mermaid_cli.py`: Command-line interface
- `tests/`: Comprehensive test suite
- `output/`: Generated files directory
- `templates/`: Custom template storage

## 🎯 Example Use Cases

1. **Software Development Workflows**
2. **Business Process Documentation**  
3. **System Architecture Diagrams**
4. **Decision Tree Visualization**
5. **API Flow Documentation**

## Batch Files (Windows)

* `000_init.bat`: Initialize git repository
* `001_env.bat`: Create virtual environment
* `002_activate.bat`: Activate virtual environment
* `003_setup.bat`: Install dependencies and setup Playwright
* `004_run.bat`: Run main demonstrations
* `005_run_test.bat`: Execute tests
* `005_run_code_cov.bat`: Run tests with coverage
* `008_deactivate.bat`: Deactivate virtual environment

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Implement changes with proper OOP principles
4. Add comprehensive tests
5. Submit a pull request

## License

[Specify the project license, if any.]
