#!/usr/bin/env python3
"""
Test all diagram templates from Streamlit app
"""
from src.mermaid_utils import FlowchartValidator

# Same templates as in streamlit_app.py
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

def test_all_templates():
    """Test validation of all diagram templates"""
    print("🧪 Testing All Diagram Templates Validation")
    print("=" * 60)
    
    validator = FlowchartValidator()
    results = {}
    
    for template_name, template_code in DIAGRAM_TEMPLATES.items():
        print(f"\n📊 Testing: {template_name}")
        print("-" * 40)
        
        # Reset validator
        validator.errors.clear()
        validator.warnings.clear()
        
        is_valid = validator.validate_mermaid_syntax(template_code)
        results[template_name] = {
            'valid': is_valid,
            'errors': validator.errors.copy(),
            'warnings': validator.warnings.copy()
        }
        
        if is_valid:
            print(f"✅ {template_name}: VALID")
        else:
            print(f"❌ {template_name}: INVALID")
            for error in validator.errors:
                print(f"   Error: {error}")
        
        if validator.warnings:
            print("⚠️  Warnings:")
            for warning in validator.warnings:
                print(f"   {warning}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 VALIDATION SUMMARY")
    print("=" * 60)
    
    valid_count = sum(1 for r in results.values() if r['valid'])
    total_count = len(results)
    
    for template_name, result in results.items():
        status = "✅ PASS" if result['valid'] else "❌ FAIL"
        print(f"{template_name:<30} {status}")
    
    print(f"\n📊 Overall: {valid_count}/{total_count} templates valid")
    
    if valid_count == total_count:
        print("🎉 All templates are valid!")
        return True
    else:
        print("❌ Some templates need fixing!")
        return False

if __name__ == "__main__":
    success = test_all_templates()
    
    if success:
        print("\n✅ All Streamlit diagram templates are validated and ready!")
    else:
        print("\n❌ Some templates need validation fixes!")