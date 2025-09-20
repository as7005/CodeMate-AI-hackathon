#!/usr/bin/env python3
"""
Terminal Interface-like Project in Python
This simulates a basic terminal environment with common commands.
"""

import os
import sys
import subprocess
from pathlib import Path

# Import our new modules
from filesystem import list_directory, change_directory, make_directory, remove_file
from shell_scripts import execute_script
from misc import exec_python_file, show_help

class SimpleTerminal:
    def __init__(self):
        self.current_path = Path.cwd()
        self.history = []
        
    def run(self):
        """Main loop for the terminal interface"""
        print("Simple Terminal Interface")
        print("Type 'help' for available commands or 'exit' to quit")
        print(f"Current directory: {self.current_path}")
        print("-" * 70)
        
        while True:
            try:
                # Show prompt with current directory
                prompt = f"{self.current_path.name}$ "
                command = input(prompt).strip()
                
                if not command:
                    continue
                    
                # Add to history
                self.history.append(command)
                
                # Parse command and arguments
                parts = command.split()
                cmd = parts[0].lower()
                args = parts[1:]
                
                # Process commands
                if cmd == 'exit':
                    print("Goodbye!")
                    break
                elif cmd == 'help':
                    show_help()
                elif cmd == 'ls':
                    list_directory(self.current_path, args)
                elif cmd == 'cd':
                    self.current_path = change_directory(self.current_path, args)
                elif cmd == 'pwd':
                    print(self.current_path)
                elif cmd == 'echo':
                    print(" ".join(args))
                elif cmd == 'clear':
                    os.system('cls' if os.name == 'nt' else 'clear')
                elif cmd == 'history':
                    for i, cmd in enumerate(self.history, 1):
                        print(f"{i:3d}  {cmd}")
                elif cmd == 'mkdir':
                    make_directory(self.current_path, args)
                elif cmd == 'rm':
                    remove_file(self.current_path, args)
                elif cmd == 'exec':
                    if args:
                        exec_python_file(self.current_path, args[0])
                    else:
                        print("exec: missing argument")
                elif cmd == 'script':
                    if args:
                        execute_script(self.current_path, args[0])
                    else:
                        print("script: missing argument")
                else:
                    # Try to run as system command
                    self.run_system_command(command)
                    
            except KeyboardInterrupt:
                print("\nUse 'exit' to quit")
            except EOFError:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")
    
    def run_system_command(self, command):
        """Run a system command"""
        try:
            # Split command and arguments
            parts = command.split()
            cmd = parts[0]
            args = parts[1:]
            
            # Handle built-in commands that should not be passed to system
            if cmd in ['ls', 'cd', 'pwd', 'echo', 'clear', 'history', 'mkdir', 'rm', 'exec', 'script']:
                # These are handled internally, so we skip
                return
                
            # Run system command
            result = subprocess.run([cmd] + args, 
                                  capture_output=True, 
                                  text=True, 
                                  cwd=self.current_path)
            
            if result.stdout:
                print(result.stdout, end='')
            if result.stderr:
                print(result.stderr, end='')
                
        except FileNotFoundError:
            print(f"Command not found: {command.split()[0]}")
        except Exception as e:
            print(f"Error running command: {e}")

def main():
    """Main entry point"""
    terminal = SimpleTerminal()
    terminal.run()

if __name__ == "__main__":
    main()
