#!/usr/bin/env python3
"""
Test quadrant chart validation
"""
from src.mermaid_utils import FlowchartValidator

def test_quadrant_validation():
    validator = FlowchartValidator()
    
    # Your quadrant chart syntax
    quadrant_syntax = """quadrantChart
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
    
    print("Testing quadrant chart validation...")
    print(f"Syntax:\n{quadrant_syntax}")
    print("\nValidation result:")
    
    is_valid = validator.validate_mermaid_syntax(quadrant_syntax)
    print(f"Valid: {is_valid}")
    
    if validator.errors:
        print("Errors:")
        for error in validator.errors:
            print(f"  - {error}")
    
    if validator.warnings:
        print("Warnings:")
        for warning in validator.warnings:
            print(f"  - {warning}")
    
    print(f"\nValidation report:\n{validator.get_validation_report()}")

if __name__ == "__main__":
    test_quadrant_validation()