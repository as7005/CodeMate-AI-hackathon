#!/usr/bin/env python3
"""
Miscellaneous commands for the terminal interface
"""

import os
import runpy
from pathlib import Path


def exec_python_file(current_path, file_path):
    """Execute a Python file safely in its own namespace"""
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

        runpy.run_path(str(python_file), run_name="__main__")
        print(f"Executed Python file: {file_path}")
        return True

    except Exception as e:
        print(f"Error executing Python file '{file_path}': {e}")
        return False


def exec_shell_file(terminal_instance, current_path, file_path):
    """Execute a shell script file line by line through the terminal's run_command"""
    try:
        script_file = current_path / file_path

        if not script_file.exists():
            print(f"Script not found: {file_path}")
            return False

        if not script_file.is_file():
            print(f"Not a file: {file_path}")
            return False

        if script_file.suffix != '.sh':
            print(f"File must be a shell script (.sh): {file_path}")
            return False

        with open(script_file, 'r') as f:
            lines = f.readlines()

        print(f"Executing script: {file_path}")
        print("-" * 70)

        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            parts = line.split()
            cmd = parts[0]
            args = parts[1:]

            terminal_instance.run_command(cmd, args)

        print("-" * 40)
        print("Script execution completed.")
        return True

    except Exception as e:
        print(f"Error executing script: {e}")
        return False


def exec_file(terminal_instance, current_path, file_path):
    """Dispatch to exec_python_file or exec_shell_file depending on suffix"""
    path = current_path / file_path
    if not path.exists():
        print(f"File not found: {file_path}")
        return False

    if path.suffix == ".py":
        return exec_python_file(current_path, file_path)
    elif path.suffix == ".sh":
        return exec_shell_file(terminal_instance, current_path, file_path)
    else:
        print(f"Unsupported file type: {file_path}")
        return False


def show_help():
    """Display available commands"""
    help_text = """
Available commands:
  help      - Show this help message
  ls        - List directory contents
  tree      - Show directory tree
  cd        - Change directory
  pwd       - Print working directory
  echo      - Display a line of text
  clear     - Clear the screen
  history   - Show command history
  mkdir     - Create directories
  rm        - Remove files and directories
  exec      - Execute Python (.py) and shell (.sh) files
  dashboard - Show system monitoring dashboard
  exit      - Exit the terminal
    """
    print(help_text.strip())
