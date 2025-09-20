#!/usr/bin/env python3
"""
Miscellaneous commands for the terminal interface
"""

import os
import sys
import importlib.util
from pathlib import Path

def exec_python_file(current_path, file_path):
    """Execute another Python file"""
    try:
        python_file = current_path / file_path
        
        if not python_file.exists():
            print(f"File not found: {file_path}")
            return False
            
        if not python_file.is_file():
            print(f"Not a file: {file_path}")
            return False
            
        if python_file.suffix != '.py':
            print(f"File must be a Python file (.py): {file_path}")
            return False
            
        # Load and execute the module
        spec = importlib.util.spec_from_file_location("exec_module", python_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        print(f"Executed Python file: {file_path}")
        return True
        
    except Exception as e:
        print(f"Error executing Python file '{file_path}': {e}")
        return False

def show_help():
    """Display available commands"""
    help_text = """
Available commands:
  help     - Show this help message
  ls       - List directory contents
  cd       - Change directory
  pwd      - Print working directory
  echo     - Display a line of text
  clear    - Clear the screen
  history  - Show command history
  mkdir    - Create directories
  rm       - Remove files and directories
  exec     - Execute Python files
  script   - Execute shell scripts
  exit     - Exit the terminal
  
    """
    print(help_text.strip())
