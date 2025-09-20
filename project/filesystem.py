#!/usr/bin/env python3
"""
File system operations for the terminal interface
"""

import os
import shutil
from pathlib import Path

def list_directory(path, args):
    """List directory contents"""
    try:
        if args and args[0] == '-l':
            # Long format listing
            for item in sorted(path.iterdir()):
                if item.is_dir():
                    print(f"d {' ' * 8} {item.name}")
                else:
                    print(f"- {' ' * 8} {item.name}")
        else:
            # Simple listing
            items = [item.name for item in sorted(path.iterdir())]
            print(" ".join(items))
    except PermissionError:
        print("Permission denied")

def change_directory(current_path, args):
    """Change current directory"""
    if not args:
        print("cd: missing argument")
        return current_path
        
    target = args[0]
    
    try:
        if target == '..':
            # Go up one directory
            return current_path.parent
        elif target == '~':
            # Go to home directory
            return Path.home()
        else:
            # Go to specified directory
            new_path = current_path / target
            if new_path.exists() and new_path.is_dir():
                return new_path
            else:
                print(f"cd: {target}: No such directory")
                return current_path
    except Exception as e:
        print(f"cd: {e}")
        return current_path

def make_directory(current_path, args):
    """Create new directories"""
    if not args:
        print("mkdir: missing argument")
        return False
        
    try:
        for dir_name in args:
            new_path = current_path / dir_name
            new_path.mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        print(f"mkdir: {e}")
        return False

def remove_file(current_path, args):
    """Remove files and directories"""
    if not args:
        print("rm: missing argument")
        return False
        
    try:
        for item_name in args:
            item_path = current_path / item_name
            if item_path.exists():
                if item_path.is_dir():
                    # For directories, we need to be careful
                    if len(args) > 1:
                        # Multiple items, ask for confirmation
                        confirm = input(f"Remove directory '{item_name}'? (y/N): ")
                        if confirm.lower() != 'y':
                            continue
                    shutil.rmtree(item_path)
                else:
                    item_path.unlink()
            else:
                print(f"rm: {item_name}: No such file or directory")
        return True
    except Exception as e:
        print(f"rm: {e}")
        return False
