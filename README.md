# PyMermaidView 🎨

A comprehensive Python application for generating Mermaid diagrams using Object-Oriented Programming principles. Create beautiful flowcharts, export them to various formats, and manage them through an intuitive API or CLI interface.

## ✨ Features

### 🌐 **Streamlit Web Interface (NEW!)**
- **9 Diagram Types**: Flowchart, Pie, Quadrant, Class, Sequence, Gantt, Git, User Journey, Mindmap
- **Clean UI Design**: Clutter-free interface with intuitive left-right layout
- **Real-time Validation**: Instant syntax checking with detailed error reporting
- **Template Gallery**: One-click loading of pre-built templates for all diagram types
- **Interactive Preview**: Live image preview with zoom in/out functionality
- **Drag & Drop Support**: Easy file upload and syntax import
- **High-Quality Export**: Generate PNG images with customizable resolution and scaling

### 🏗️ **Core Engine**
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

6.  **Launch Web Interface (Recommended):**
    Run `streamlit run streamlit_app.py --server.port 8507` and open <http://localhost:8507>

### Installation (macOS/Linux)

1.  Initialize git:
    Run `scripts/000_init.sh` (optional; respects GIT_USER_NAME and GIT_USER_EMAIL env vars).

2.  Create a virtual environment:
    Run `scripts/001_env.sh`.

3.  Activate the virtual environment:
    Run `source scripts/002_activate.sh` (or `source .venv/bin/activate`).

4.  Install dependencies and Playwright:
    Run `scripts/003_setup.sh`.

5.  Run demonstrations:
    Run `scripts/004_run.sh` or `python3 main.py`.

6.  Launch Web Interface (Recommended):
    Run `scripts/start_web_ui.sh` (defaults to http://localhost:8501), or `streamlit run streamlit_app.py --server.port 8507`.

### 📦 **Dependencies**

**Core Requirements:**
- Python 3.8+
- Playwright (for browser-based rendering)  
- Pillow (image processing)
- Pydantic (data validation)

**Web Interface:**
- Streamlit 1.28+ (web framework)
- streamlit-ace (code editor component)

**Development:**
- pytest (testing framework)
- pytest-cov (coverage reporting)

## 🌐 **Streamlit Web Interface** 

PyMermaidView features a **comprehensive web-based interface** for interactive Mermaid diagram creation and visualization!

### 🚀 **Quick Launch**

```bash
# Start the web interface
streamlit run streamlit_app.py --server.port 8507

# Opens at: http://localhost:8507
```

### 🎨 **Interface Layout**

**Clean, Professional Design:**
- **Left Pane**: Mermaid syntax editor with template support
- **Right Pane**: Live image preview with zoom controls
- **Top Controls**: Diagram type selector, validation, and generation buttons

### 🔧 **Complete Feature Set**

#### **📋 Diagram Types (9 Supported)**
- **Flowchart**: Process flows and decision trees
- **Pie Chart**: Data visualization with percentages
- **Quadrant Chart**: Strategic analysis and positioning
- **Class Diagram**: Object-oriented system design
- **Sequence Diagram**: Interaction flows over time
- **Gantt Chart**: Project timelines and scheduling
- **Git Graph**: Version control branching visualization
- **User Journey**: User experience mapping
- **Mindmap**: Hierarchical information organization

#### **🎯 Core Functionality**
- **📋 Template Loading**: One-click access to pre-built templates for all diagram types
- **🔍 Real-time Validation**: Instant syntax checking with detailed error reporting
- **🎨 Image Generation**: High-quality PNG output with customizable settings
- **� Interactive Preview**: Zoom in/out functionality for detailed viewing
- **📱 Responsive Design**: Clean, clutter-free interface optimized for productivity

#### **⚡ User Experience**
- **Instant Feedback**: Real-time validation as you type
- **Template Gallery**: Professional templates for rapid prototyping  
- **Error Handling**: Clear, actionable error messages
- **Session Persistence**: Maintains your work across browser sessions

### 🎯 **Perfect For**
- **Business Process Mapping**: Document workflows and procedures
- **Software Architecture**: Design system components and interactions  
- **Project Planning**: Create Gantt charts and timeline visualization
- **Data Presentation**: Build compelling pie charts and quadrant analysis
- **Team Collaboration**: Share interactive diagram creation environment
- **Learning & Training**: Educational environment for Mermaid syntax mastery

## 🔍 **Enhanced Multi-Diagram Validation**

The validation system now supports **9 different Mermaid diagram types** with specific syntax rules:

```python
from src.mermaid_utils import FlowchartValidator

# Validate any supported diagram type
validator = FlowchartValidator()

# Examples of supported diagrams
pie_chart = "pie title Pets: 'Dogs' : 386, 'Cats' : 85"
quadrant_chart = "quadrantChart\n    title Market Analysis\n    x-axis Low --> High"
class_diagram = "classDiagram\n    class Animal {\n        +name: string\n    }"

# Validate with detailed feedback
if validator.validate_mermaid_syntax(pie_chart):
    print("✅ Valid syntax!")
else:
    print("❌ Validation errors:", validator.errors)
```

## 💻 **Programmatic Usage**

### Basic Diagram Generation

```python
from src.mermaid_generator import MermaidGenerator, OutputFormat, MermaidTheme
from src.flowchart_builder import FlowchartBuilder, NodeShape, Direction
import asyncio

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

# Save to file and generate image
async def create_diagram():
    mermaid_file = builder.save_to_file("user_registration.mmd")
    
    generator = MermaidGenerator()
    generator.set_theme(MermaidTheme.FOREST).set_output_format(OutputFormat.PNG)
    image_file = await generator.generate_from_file(mermaid_file)
    return image_file

# Run async function
image_path = asyncio.run(create_diagram())
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

- **`MermaidGenerator`**: Main orchestrator for diagram generation with async support
- **`FlowchartBuilder`**: Fluent interface for building flowcharts  
- **`FlowchartNode`**: Represents individual nodes with styling
- **`FlowchartConnection`**: Represents connections between nodes
- **`TemplateManager`**: Template creation and management
- **`FlowchartValidator`**: Enhanced multi-diagram syntax validation (9 diagram types)
- **`StreamlitApp`**: Web interface controller with session management

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

- `streamlit_app.py`: **Web interface** - Complete Streamlit application
- `src/`: Core application modules
  - `mermaid_generator.py`: Main generation engine with async support
  - `flowchart_builder.py`: OOP flowchart construction
  - `mermaid_utils.py`: Enhanced utilities, validation, and templates
  - `mermaid_cli.py`: Command-line interface
- `tests/`: Comprehensive test suite with web interface tests
- `output/`: Generated files directory
- `templates/`: Custom template storage
- Batch files for Windows automation (000_*.bat to 008_*.bat)

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

## 📈 **Recent Updates & Changelog**

### **Version 2.0 - Streamlit Web Interface** *(Latest)*

🎉 **Major Release: Complete Web Interface**

**🌟 New Features:**
- **Streamlit Web Application**: Full-featured web interface for diagram creation
- **9 Diagram Type Support**: Comprehensive support for all major Mermaid diagram types
- **Enhanced Validation System**: Real-time syntax validation with detailed error reporting  
- **Interactive Preview**: Live image preview with zoom functionality
- **Template Gallery**: One-click loading of professional templates
- **Clean UI Design**: Clutter-free, professional interface optimized for productivity

**🔧 Technical Improvements:**
- **Async Support**: Full asynchronous image generation capabilities
- **Multi-Diagram Validation**: Enhanced `FlowchartValidator` supporting 9 diagram types
- **Session Management**: Streamlit session state for persistent user experience
- **Error Handling**: Comprehensive error reporting and user feedback
- **Code Quality**: 100% test coverage for new web interface components

**🚀 Quick Access:**
```bash
# Launch the new web interface
streamlit run streamlit_app.py --server.port 8507
# Visit: http://localhost:8507
```

### **Previous Versions**
- **Version 1.x**: Core CLI functionality, OOP architecture, basic diagram generation
- **Version 0.x**: Initial implementation with basic flowchart support

## 🤝 **Contributing**

We welcome contributions! Here's how to get started:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/your-feature-name`
3. **Implement changes** with proper OOP principles and comprehensive tests
4. **Add/update tests** ensuring coverage for new functionality
5. **Update documentation** including README and inline comments
6. **Submit a pull request** with detailed description of changes

### **Development Guidelines**
- Follow existing code style and OOP patterns
- Add comprehensive tests for all new features  
- Update documentation for user-facing changes
- Test both CLI and web interface functionality

## 📄 **License**

[Specify the project license, if any.]
