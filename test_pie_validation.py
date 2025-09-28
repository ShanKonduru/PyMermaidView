#!/usr/bin/env python3
"""
Test the pie chart validation
"""
from src.mermaid_utils import FlowchartValidator

def test_pie_validation():
    validator = FlowchartValidator()
    
    # Your pie chart syntax
    pie_syntax = '''pie title NETFLIX
         "Time spent looking for movie" : 90
         "Time spent watching it" : 10'''
    
    print("Testing pie chart validation...")
    print(f"Syntax:\n{pie_syntax}")
    print("\nValidation result:")
    
    is_valid = validator.validate_mermaid_syntax(pie_syntax)
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
    test_pie_validation()