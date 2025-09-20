#!/usr/bin/env python3
"""
Shell script execution for the terminal interface
"""

import os
import subprocess
from pathlib import Path

def execute_script(current_path, script_path):
    """Execute a shell script line by line"""
    try:
        script_file = current_path / script_path
        
        if not script_file.exists():
            print(f"Script not found: {script_path}")
            return False
            
        if not script_file.is_file():
            print(f"Not a file: {script_path}")
            return False
            
        with open(script_file, 'r') as f:
            lines = f.readlines()
            
        print(f"Executing script: {script_path}")
        print("-" * 40)
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
                
            print(f"[{i}] {line}")
            
            # Split command and arguments
            parts = line.split()
            if not parts:
                continue
                
            cmd = parts[0]
            args = parts[1:]
            
            # Handle built-in commands that should not be passed to system
            if cmd in ['ls', 'cd', 'pwd', 'echo', 'clear', 'history', 'mkdir', 'rm']:
                print(f"Skipping built-in command: {cmd}")
                continue
                
            # Run system command
            try:
                result = subprocess.run([cmd] + args, 
                                      capture_output=True, 
                                      text=True, 
                                      cwd=current_path)
                
                if result.stdout:
                    print(result.stdout, end='')
                if result.stderr:
                    print(result.stderr, end='')
                    
            except FileNotFoundError:
                print(f"Command not found: {cmd}")
            except Exception as e:
                print(f"Error running command '{line}': {e}")
                
        print("-" * 40)
        print("Script execution completed.")
        return True
        
    except Exception as e:
        print(f"Error executing script: {e}")
        return False
