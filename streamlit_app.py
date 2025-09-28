#!/usr/bin/env python3
"""
PyMermaidView - Enhanced Streamlit Interface with AI Enhancement
"""
import streamlit as st
import asyncio
from pathlib import Path
from typing import Optional
import base64
import io
import requests
import json
from PIL import Image

# Import our core modules
from src.mermaid_generator import MermaidGenerator, MermaidConfig, OutputFormat, MermaidTheme
from src.mermaid_utils import FlowchartValidator

# Page configuration
st.set_page_config(
    page_title="PyMermaidView",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"  # Collapsible sidebar by default
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
if 'ai_enhancing' not in st.session_state:
    st.session_state.ai_enhancing = False
if 'enhancement_history' not in st.session_state:
    st.session_state.enhancement_history = []

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

def enhance_with_ai(mermaid_code: str, enhancement_type: str = "improve") -> Optional[str]:
    """Enhance Mermaid syntax using Ollama local LLM"""
    
    # Ollama API endpoint (default local installation)
    ollama_url = "http://localhost:11434/api/generate"
    
    # Define enhancement prompts
    prompts = {
        "improve": f"""You are a Mermaid diagram expert. Please improve and enhance the following Mermaid diagram syntax:

{mermaid_code}

Make the diagram more professional, add better styling, improve node names, add colors if appropriate, and ensure best practices. Return ONLY the enhanced Mermaid syntax without any explanations or markdown formatting.""",
        
        "add_styling": f"""You are a Mermaid diagram expert. Please add professional styling, colors, and visual enhancements to this Mermaid diagram:

{mermaid_code}

Add appropriate colors, styling, and visual improvements while keeping the same structure. Return ONLY the enhanced Mermaid syntax without explanations.""",
        
        "optimize": f"""You are a Mermaid diagram expert. Please optimize and restructure this Mermaid diagram for better clarity and readability:

{mermaid_code}

Improve the layout, node connections, and overall structure while maintaining the same meaning. Return ONLY the optimized Mermaid syntax without explanations."""
    }
    
    try:
        # Prepare the request
        payload = {
            "model": "llama3.2",  # You can change this to your preferred model
            "prompt": prompts.get(enhancement_type, prompts["improve"]),
            "stream": False,
            "options": {
                "temperature": 0.3,  # Lower temperature for more consistent results
                "num_predict": 1000  # Limit response length
            }
        }
        
        # Make request to Ollama with shorter timeout
        response = requests.post(ollama_url, json=payload, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            enhanced_code = result.get('response', '').strip()
            
            # Clean up the response (remove any markdown formatting)
            if enhanced_code.startswith('```'):
                lines = enhanced_code.split('\n')
                enhanced_code = '\n'.join(lines[1:])
            if enhanced_code.endswith('```'):
                lines = enhanced_code.split('\n')
                enhanced_code = '\n'.join(lines[:-1])
            
            # Additional cleanup - remove common AI response patterns
            enhanced_code = enhanced_code.replace('mermaid\n', '').strip()
            
            return enhanced_code if enhanced_code else None
        else:
            st.error(f"Ollama responded with status code: {response.status_code}")
            return None
            
    except Exception as e:
        st.error(f"AI Enhancement Error: {str(e)}")
        return None

def main():
    # Title
    st.markdown('<h1 class="main-title">PyMermaidView</h1>', unsafe_allow_html=True)
    
    # Sidebar - Collapsible configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Image Generation Settings
        with st.expander("🖼️ Image Generation", expanded=True):
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
        
        # AI Enhancement Setup
        with st.expander("🤖 AI Enhancement Setup", expanded=False):
            st.markdown("""
            **Ollama Local LLM Setup:**
            
            1. Install Ollama: `curl -fsSL https://ollama.ai/install.sh | sh`
            2. Start Ollama: `ollama serve`
            3. Pull model: `ollama pull llama3.2`
            4. Verify: `curl http://localhost:11434/api/tags`
            
            **Status Check:**
            """)
            
            # Check Ollama status
            try:
                response = requests.get("http://localhost:11434/api/tags", timeout=2)
                if response.status_code == 200:
                    st.success("✅ Ollama is running")
                    models = response.json().get('models', [])
                    if models:
                        st.info(f"📚 Available models: {len(models)}")
                    else:
                        st.warning("⚠️ No models found - run 'ollama pull llama3.2'")
                else:
                    st.error("❌ Ollama not responding")
            except:
                st.error("❌ Ollama not running - start with 'ollama serve'")
    
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
        
        # Action buttons - 3 columns now
        button_col1, button_col2, button_col3 = st.columns(3)
        
        with button_col1:
            if st.button("🔍 Validate Syntax", type="primary"):
                validate_syntax(mermaid_code)
        
        with button_col2:
            if st.button("🎨 Generate Image", type="primary"):
                generate_image(mermaid_code, theme, output_format, width, height, scale)
        
        with button_col3:
            # AI Enhancement button
            if st.button("🤖 Enhance with AI", type="secondary", help="Improve diagram using local Ollama LLM"):
                enhance_with_ollama(mermaid_code)
        
        # AI Enhancement options (collapsible)
        with st.expander("🎛️ AI Enhancement Options", expanded=False):
            enhancement_type = st.selectbox(
                "Enhancement Type",
                options=["improve", "add_styling", "optimize"],
                format_func=lambda x: {
                    "improve": "🔧 General Improvement",
                    "add_styling": "🎨 Add Visual Styling", 
                    "optimize": "⚡ Optimize Structure"
                }[x],
                help="Choose the type of AI enhancement to apply"
            )
            
            # Store enhancement type in session state
            st.session_state.enhancement_type = enhancement_type
            
            if st.session_state.enhancement_history:
                st.info(f"💡 {len(st.session_state.enhancement_history)} enhancement(s) applied in this session")
        
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
        # Header with zoom controls
        preview_col1, preview_col2, preview_col3, preview_col4 = st.columns([3, 1, 1, 1])
        
        with preview_col1:
            st.header("🖼️ Image Preview")
        
        # Zoom controls in the preview area
        if st.session_state.generated_image:
            with preview_col2:
                if st.button("🔍➕", help="Zoom In", key="zoom_in_preview"):
                    st.session_state.zoom_level = min(200, st.session_state.zoom_level + 25)
                    st.rerun()
            
            with preview_col3:
                if st.button("🔍➖", help="Zoom Out", key="zoom_out_preview"):
                    st.session_state.zoom_level = max(50, st.session_state.zoom_level - 25)
                    st.rerun()
            
            with preview_col4:
                if st.button("🔄", help="Reset Zoom", key="reset_zoom"):
                    st.session_state.zoom_level = 100
                    st.rerun()
        
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
                
                # Download and zoom info
                download_col1, download_col2 = st.columns([2, 1])
                
                with download_col1:
                    # Download button
                    with open(image_path, "rb") as file:
                        st.download_button(
                            label="💾 Download Image",
                            data=file.read(),
                            file_name=f"diagram.{output_format}",
                            mime=f"image/{output_format}"
                        )
                
                with download_col2:
                    st.info(f"🔍 Zoom: {st.session_state.zoom_level}%")
                
            except Exception as e:
                st.error(f"Error displaying image: {e}")
        else:
            st.info("👆 Generate an image to see the preview here")
            st.markdown("---")
            st.markdown("**🔍 Zoom Controls**")
            st.markdown("Zoom controls will appear here once an image is generated")

def enhance_with_ollama(mermaid_code: str):
    """Handle AI enhancement using Ollama"""
    
    if not mermaid_code.strip():
        st.error("Please enter Mermaid syntax first")
        return
    
    enhancement_type = st.session_state.get('enhancement_type', 'improve')
    
    # Show progress
    progress_placeholder = st.empty()
    progress_placeholder.info(f"🤖 Enhancing diagram with AI ({enhancement_type})...")
    
    try:
        # Call AI enhancement
        enhanced_code = enhance_with_ai(mermaid_code, enhancement_type)
        
        if enhanced_code and enhanced_code.strip() and enhanced_code != mermaid_code:
            # Store the enhancement
            st.session_state.enhancement_history.append({
                'original': mermaid_code,
                'enhanced': enhanced_code,
                'type': enhancement_type
            })
            
            # Update the mermaid code
            st.session_state.mermaid_code = enhanced_code
            
            # Clear progress and show success
            progress_placeholder.empty()
            st.success(f"✨ Diagram enhanced successfully using {enhancement_type}!")
            st.info("💡 The enhanced code has been loaded in the editor. Click refresh or generate to see changes.")
            
            # Auto-validate the enhanced code
            validate_syntax(enhanced_code)
            
        elif enhanced_code == mermaid_code:
            progress_placeholder.empty()
            st.warning("🤔 AI suggested no changes - your diagram is already well-optimized!")
        else:
            progress_placeholder.empty()
            st.error("❌ AI enhancement failed. Please check if Ollama is running on localhost:11434")
            
    except Exception as e:
        progress_placeholder.empty()
        st.error(f"❌ Enhancement failed: {str(e)}")
        st.info("💡 Make sure Ollama is running: `ollama serve`")

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