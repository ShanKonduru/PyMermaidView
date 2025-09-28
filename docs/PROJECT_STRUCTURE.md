# 📁 **Project Structure Guide**

## 🏗️ **Organized Directory Structure**

PyMermaidView now has a clean, professional directory structure for better maintainability and navigation.

```
PyMermaidView/
├── 📁 src/                     # Core source code
│   ├── __init__.py
│   ├── mermaid_generator.py    # Main generation engine
│   ├── flowchart_builder.py    # OOP flowchart construction
│   ├── mermaid_utils.py        # Utilities and validation
│   ├── mermaid_cli.py          # Command-line interface
│   └── windows_utils.py        # Windows-specific utilities
│
├── 📁 tests/                   # Test suite
│   ├── __init__.py
│   ├── test_main.py           # Core functionality tests
│   ├── test_*_generation.py   # Generation tests
│   ├── test_*_validation.py   # Validation tests
│   └── pytest.ini            # Test configuration
│
├── 📁 scripts/                 # Automation scripts
│   ├── 000_init.bat           # Initialize git repository
│   ├── 001_env.bat            # Create virtual environment
│   ├── 002_activate.bat       # Activate virtual environment
│   ├── 003_setup.bat          # Install dependencies
│   ├── 004_run.bat            # Run main application
│   ├── 005_run_test.bat       # Execute tests
│   ├── 005_run_code_cov.bat   # Run tests with coverage
│   ├── 008_deactivate.bat     # Deactivate virtual environment
│   └── start_web_ui.bat       # Launch Streamlit interface
│
├── 📁 docs/                    # Documentation
│   ├── AI_ENHANCEMENT_GUIDE.md     # AI enhancement features
│   ├── WEB_INTERFACE_GUIDE.md      # Streamlit UI guide
│   ├── OOP_IMPLEMENTATION_SUMMARY.md # Architecture overview
│   ├── TEST_FIXES_SUMMARY.md       # Testing improvements
│   ├── ENHANCEMENT_SUMMARY.md      # Feature summary
│   └── *.md                        # Other documentation
│
├── 📁 examples/                # Example code and utilities
│   ├── examples_advanced_oop.py    # Advanced OOP examples
│   └── create_themed_versions.py   # Theme creation utility
│
├── 📁 tools/                   # Development and testing tools
│   ├── final_verification.py       # Complete system verification
│   ├── final_quadrant_test.py     # Quadrant chart testing
│   ├── generate_agentic_rag.py    # RAG system generation
│   └── view_agentic_rag.py        # RAG system viewer
│
├── 📁 templates/               # Mermaid templates
│   └── *.mmd                  # Pre-built diagram templates
│
├── 📁 output/                  # Generated files
│   └── *.png, *.svg, *.pdf    # Generated diagrams
│
├── 📁 temp/                    # Temporary files
│   └── *.mmd                  # Temporary diagram files
│
├── 📁 test_reports/           # Test results and coverage
│   └── *.html                 # Test reports
│
├── 📁 htmlcov/                # Coverage reports
│   └── *.html                 # HTML coverage reports
│
├── 📄 main.py                 # Main application entry point
├── 📄 streamlit_app.py        # Streamlit web interface
├── 📄 README.md               # Project documentation
├── 📄 requirements.txt        # Python dependencies
├── 📄 pytest.ini             # Test configuration
└── 📄 .gitignore              # Git ignore rules
```

## 🚀 **Quick Start Commands**

### **From Project Root:**
```bash
# Setup (run once)
scripts\000_init.bat          # Initialize git
scripts\001_env.bat           # Create virtual environment  
scripts\002_activate.bat      # Activate environment
scripts\003_setup.bat         # Install dependencies

# Development
scripts\004_run.bat           # Run CLI application
scripts\start_web_ui.bat      # Launch web interface
scripts\005_run_test.bat      # Run tests
scripts\005_run_code_cov.bat  # Run tests with coverage

# Cleanup
scripts\008_deactivate.bat    # Deactivate environment
```

### **From Scripts Directory:**
```bash
cd scripts
000_init.bat                  # All scripts work from their directory
001_env.bat                   # Paths automatically adjusted
# ... etc
```

## 📂 **Directory Purposes**

| Directory | Purpose | Contents |
|-----------|---------|----------|
| **`src/`** | Core application code | Main modules, generators, utilities |
| **`tests/`** | Test suite | Unit tests, integration tests, fixtures |
| **`scripts/`** | Automation | Batch files for setup and execution |
| **`docs/`** | Documentation | Guides, summaries, API documentation |
| **`examples/`** | Example code | Demonstrations, utilities, samples |
| **`tools/`** | Development tools | Testing utilities, verification scripts |
| **`templates/`** | Diagram templates | Pre-built Mermaid diagrams |
| **`output/`** | Generated content | Images, diagrams, exports |
| **`temp/`** | Temporary files | Working files, cache, temporary diagrams |

## 🔧 **Benefits of New Structure**

### **🎯 Improved Organization**
- **Logical Grouping**: Related files grouped by purpose
- **Easier Navigation**: Clear directory structure
- **Professional Layout**: Industry-standard organization
- **Reduced Clutter**: Clean root directory

### **🚀 Better Maintainability**  
- **Modular Structure**: Easy to find and modify components
- **Clear Separation**: Code, tests, docs, and tools separated
- **Scalable Design**: Easy to add new components
- **Version Control Friendly**: Better git organization

### **👥 Enhanced Collaboration**
- **Intuitive Layout**: New contributors can navigate easily
- **Clear Documentation**: Organized docs in dedicated folder  
- **Standardized Structure**: Follows Python project conventions
- **Tool Integration**: Better IDE and tool support

## 📋 **Migration Notes**

### **Updated Paths:**
- **Batch Scripts**: Now in `scripts/` with adjusted paths
- **Documentation**: Consolidated in `docs/` directory  
- **Examples**: Moved to `examples/` for clarity
- **Tools**: Development utilities in `tools/` folder

### **Backward Compatibility:**
- **All batch scripts updated** to work from new locations
- **Import paths unchanged** in Python modules
- **External references** automatically handled
- **Git history preserved** during reorganization

## 🎉 **Usage Examples**

### **Development Workflow:**
```bash
# 1. Setup (one-time)
scripts\003_setup.bat

# 2. Daily development
scripts\002_activate.bat      # Activate environment
scripts\004_run.bat           # Test CLI
scripts\start_web_ui.bat      # Launch web UI
scripts\005_run_test.bat      # Run tests

# 3. End of session  
scripts\008_deactivate.bat    # Deactivate environment
```

### **File Organization:**
```bash
# Add new features
src/new_feature.py            # Core functionality

# Add tests
tests/test_new_feature.py     # Test coverage

# Add documentation  
docs/NEW_FEATURE_GUIDE.md     # User documentation

# Add examples
examples/new_feature_demo.py  # Usage examples
```

This organized structure makes PyMermaidView more professional, maintainable, and easier to navigate! 🚀