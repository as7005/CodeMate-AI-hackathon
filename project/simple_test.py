#!/usr/bin/env python3
"""
Simple test to validate our fixes
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Test importing the modules
try:
    from filesystem import list_directory, change_directory
    from misc import show_help
    print("✓ All modules imported successfully")
    
    # Test help function
    print("\n--- Testing help function ---")
    show_help()
    
    print("\n--- Testing list_directory function ---")
    from pathlib import Path
    current_path = Path('.')
    print(f"Current path: {current_path}")
    
    # Test simple listing
    print("Simple listing:")
    list_directory(current_path, [])
    
    # Test long listing
    print("\nLong listing:")
    list_directory(current_path, ['-l'])
    
except Exception as e:
    print(f"Error during testing: {e}")
    import traceback
    traceback.print_exc()
