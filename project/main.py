#!/usr/bin/env python3
"""
Terminal Interface-like Project in Python
This simulates a basic terminal environment with common commands.
"""

import os
import sys
import subprocess
import time
from pathlib import Path
import threading

# Import our new modules
from filesystem import list_directory, change_directory, make_directory, remove_file, tree_directory
from system_monitor import SystemMonitor
from shell_scripts import execute_script
from misc import exec_file, show_help


class SimpleTerminal:
    def __init__(self):
        self.current_path = Path.cwd()
        self.history = []
        self.system_monitor = SystemMonitor()

    def run_command(self, command, args):
        try:
            match command:
                case 'ls': list_directory(self.current_path, args)
                case 'tree': tree_directory(self.current_path, args)
                case 'cd': self.current_path = change_directory(self.current_path, args)
                case 'pwd': print(self.current_path)
                case 'echo': print(" ".join(args))
                case 'clear': os.system('cls' if os.name == 'nt' else 'clear')
                case 'history':
                    for i, cmd in enumerate(self.history, 1):
                        print(f"{i:3d}  {cmd}")
                case 'mkdir': make_directory(self.current_path, args)
                case 'rm': remove_file(self.current_path, args)
                case 'exec':
                    if not args:
                        print("exec: missing argument")
                    else:
                        exec_file(self, self.current_path, args[0])
                case 'help': show_help()
                case 'dashboard':
                    self.system_monitor.start_dashboard()
                case 'exit':
                    print("Goodbye!")
                    return False
            return True
        except Exception as e:
            print(f"Error: {e}")
            return True

    def run(self):
        print("Simple Terminal Interface")
        print("Type 'help' for available commands or 'exit' to quit.")
        print("-" * 70)

        while True:
            try:
                if self.system_monitor.dashboard_active:
                    time.sleep(1)
                    continue

                prompt = f"{self.current_path.name}$ "
                command_line = input(prompt).strip()

                if not command_line: continue

                self.history.append(command_line)
                parts = command_line.split()
                cmd, args = parts[0].lower(), parts[1:]

                if not self.run_command(cmd, args): break

            except KeyboardInterrupt:
                if self.system_monitor.dashboard_active:
                    self.system_monitor.stop_dashboard()
                    time.sleep(0.1)
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print("\nDashboard stopped.")
                else:
                    print("\nUse 'exit' to quit.")
            except EOFError:
                print("\nGoodbye!")
                break

def main():
    terminal = SimpleTerminal()
    terminal.run()

if __name__ == "__main__":
    main()