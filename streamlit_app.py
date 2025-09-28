#!/usr/bin/env python3
"""
PyMermaidView - Clean Streamlit Interface
"""
import streamlit as st
import asyncio
from pathlib import Path
from typing import Optional
import base64
import io
from PIL import Image

# Import our core modules
from src.mermaid_generator import MermaidGenerator, MermaidConfig, OutputFormat, MermaidTheme
from src.mermaid_utils import FlowchartValidator

# Page configuration
st.set_page_config(
    page_title="PyMermaidView",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for clean interface
st.markdown("""
<style>
    .main-title {
        text-align: center;
        color: #2E86C1;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 2rem;
    }
    .stButton > button {
        width: 100%;
        margin: 0.5rem 0;
    }
    .success-msg {
        color: #28a745;
        font-weight: bold;
    }
    .error-msg {
        color: #dc3545;
        font-weight: bold;
    }
</style>""", unsafe_allow_html=True)

# Initialize session state
if 'validation_result' not in st.session_state:
    st.session_state.validation_result = None
if 'generated_image' not in st.session_state:
    st.session_state.generated_image = None
if 'zoom_level' not in st.session_state:
    st.session_state.zoom_level = 100

# Diagram templates
DIAGRAM_TEMPLATES = {
    "Flowchart": """flowchart TD
    A[Start] --> B{Decision}
    B -->|Yes| C[Process]
    B -->|No| D[Alternative]
    C --> E[End]
    D --> E""",
    
    "Sequence Diagram": """sequenceDiagram
    participant A as Alice
    participant B as Bob
    A->>B: Hello Bob, how are you?
    B-->>A: Great thanks!
    A-)B: See you later!""",
    
    "Class Diagram": """classDiagram
    class Animal {
        +String name
        +int age
        +makeSound()
    }
    class Dog {
        +String breed
        +bark()
    }
    Animal <|-- Dog""",
    
    "State Diagram": """stateDiagram-v2
    [*] --> Still
    Still --> [*]
    Still --> Moving
    Moving --> Still
    Moving --> Crash
    Crash --> [*]""",
    
    "Entity Relationship Diagram": """erDiagram
    CUSTOMER ||--o{ ORDER : places
    ORDER ||--|{ LINE-ITEM : contains
    CUSTOMER }|..|{ DELIVERY-ADDRESS : uses""",
    
    "User Journey": """journey
    title My working day
    section Go to work
      Make tea: 5: Me
      Go upstairs: 3: Me
      Do work: 1: Me, Cat
    section Go home
      Go downstairs: 5: Me
      Sit down: 5: Me""",
    
    "Gantt": """gantt
    title A Gantt Diagram
    dateFormat  YYYY-MM-DD
    section Section
    A task           :a1, 2014-01-01, 30d
    Another task     :after a1, 20d""",
    
    "Pie Chart": """pie title Pets adopted by volunteers
    "Dogs" : 386
    "Cats" : 85
    "Rats" : 15""",
    
    "Quadrant Chart": """quadrantChart
    title Reach and influence
    x-axis Low Reach --> High Reach
    y-axis Low Influence --> High Influence
    quadrant-1 We should expand
    quadrant-2 Need to promote
    quadrant-3 Re-evaluate
    quadrant-4 May be improved
    Campaign A: [0.3, 0.6]
    Campaign B: [0.45, 0.23]
    Campaign C: [0.57, 0.69]"""
}

def main():
    # Title
    st.markdown('<h1 class="main-title">PyMermaidView</h1>', unsafe_allow_html=True)
    
    # Sidebar - Image Generation Config
    with st.sidebar:
        st.header("⚙️ Image Config")
        
        theme = st.selectbox(
            "Theme",
            options=["default", "dark", "forest", "neutral"],
            index=0
        )
        
        output_format = st.selectbox(
            "Format",
            options=["png", "svg", "pdf"],
            index=0
        )
        
        width = st.number_input("Width", min_value=400, max_value=2400, value=800, step=100)
        height = st.number_input("Height", min_value=300, max_value=1800, value=600, step=100)
        scale = st.slider("Scale", min_value=1.0, max_value=3.0, value=2.0, step=0.5)
        
        st.divider()
        
        # Zoom controls for preview
        st.header("🔍 Preview Zoom")
        zoom_col1, zoom_col2 = st.columns(2)
        with zoom_col1:
            if st.button("🔍 Zoom In"):
                st.session_state.zoom_level = min(200, st.session_state.zoom_level + 25)
                st.rerun()
        with zoom_col2:
            if st.button("🔍 Zoom Out"):
                st.session_state.zoom_level = max(50, st.session_state.zoom_level - 25)
                st.rerun()
        
        st.text(f"Zoom: {st.session_state.zoom_level}%")
    
    # Main layout - two columns
    col1, col2 = st.columns([1, 1])
    
    # Left pane - Editor
    with col1:
        st.header("📝 Mermaid Syntax Editor")
        
        # Diagram type selector
        selected_type = st.selectbox(
            "Select Diagram Type",
            options=list(DIAGRAM_TEMPLATES.keys()),
            index=0
        )
        
        # Load template button
        if st.button("📋 Load Template"):
            st.session_state.mermaid_code = DIAGRAM_TEMPLATES[selected_type]
            st.rerun()
        
        # Text editor
        mermaid_code = st.text_area(
            "Enter Mermaid Syntax",
            value=st.session_state.get('mermaid_code', DIAGRAM_TEMPLATES[selected_type]),
            height=400,
            key="mermaid_input"
        )
        
        # Store in session state
        st.session_state.mermaid_code = mermaid_code
        
        # Action buttons
        button_col1, button_col2 = st.columns(2)
        
        with button_col1:
            if st.button("🔍 Validate Syntax", type="primary"):
                validate_syntax(mermaid_code)
        
        with button_col2:
            if st.button("🎨 Generate Image", type="primary"):
                generate_image(mermaid_code, theme, output_format, width, height, scale)
        
        # Show validation results
        if st.session_state.validation_result:
            result = st.session_state.validation_result
            if result['is_valid']:
                st.success("✅ Syntax is valid!")
            else:
                st.error("❌ Syntax has errors:")
                for error in result['errors']:
                    st.error(f"• {error}")
                if result['warnings']:
                    st.warning("⚠️ Warnings:")
                    for warning in result['warnings']:
                        st.warning(f"• {warning}")
    
    # Right pane - Preview
    with col2:
        st.header("🖼️ Image Preview")
        
        if st.session_state.generated_image:
            image_path = st.session_state.generated_image
            
            try:
                # Load and display image
                image = Image.open(image_path)
                
                # Apply zoom
                zoom_factor = st.session_state.zoom_level / 100
                new_width = int(image.width * zoom_factor)
                new_height = int(image.height * zoom_factor)
                
                if zoom_factor != 1.0:
                    image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                st.image(image, caption=f"Generated Diagram (Zoom: {st.session_state.zoom_level}%)")
                
                # Download button
                with open(image_path, "rb") as file:
                    st.download_button(
                        label="💾 Download Image",
                        data=file.read(),
                        file_name=f"diagram.{output_format}",
                        mime=f"image/{output_format}"
                    )
                
            except Exception as e:
                st.error(f"Error displaying image: {e}")
        else:
            st.info("👆 Generate an image to see the preview here")

def validate_syntax(mermaid_code: str):
    """Validate Mermaid syntax"""
    try:
        validator = FlowchartValidator()
        is_valid = validator.validate_mermaid_syntax(mermaid_code)
        
        st.session_state.validation_result = {
            'is_valid': is_valid,
            'errors': validator.errors.copy(),
            'warnings': validator.warnings.copy()
        }
        
    except Exception as e:
        st.session_state.validation_result = {
            'is_valid': False,
            'errors': [f"Validation error: {str(e)}"],
            'warnings': []
        }

def generate_image(mermaid_code: str, theme: str, output_format: str, width: int, height: int, scale: float):
    """Generate image from Mermaid code"""
    
    if not mermaid_code.strip():
        st.error("Please enter Mermaid syntax first")
        return
    
    try:
        with st.spinner("Generating image..."):
            # Create config
            config = MermaidConfig()
            config.theme = MermaidTheme(theme)
            config.output_format = OutputFormat(output_format.lower())
            config.width = width
            config.height = height
            config.scale = scale
            config.background_color = "white" if theme != "dark" else "#1e1e1e"
            
            # Generate image
            generator = MermaidGenerator()
            generator.config = config
            
            # Run async generation
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            output_file = Path(f"output/streamlit_diagram.{output_format}")
            result = loop.run_until_complete(generator.generate(mermaid_code, output_file))
            
            if result and result.exists():
                st.session_state.generated_image = result
                st.success(f"✅ Image generated successfully! ({result.stat().st_size / 1024:.1f} KB)")
            else:
                st.error("❌ Failed to generate image")
                
    except Exception as e:
        st.error(f"❌ Generation failed: {str(e)}")

if __name__ == "__main__":
    main()