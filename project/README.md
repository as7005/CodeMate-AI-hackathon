# Simple Terminal Interface in Python

A terminal-like interface implemented in Python that provides a command-line environment with common commands.

## Features

- Basic terminal commands: `ls`, `cd`, `pwd`, `echo`, `clear`, `history`, `help`
- File system commands: `mkdir`, `rm`
- Support for system commands (e.g., `python`, `git`, etc.)
- Shell script execution
- Python file execution with `exec` command
- Command history tracking
- Cross-platform compatibility (Windows, macOS, Linux)
- Clean and intuitive interface

## Getting Started

### Prerequisites

- Python 3.x installed on your system

### Running the Terminal

```bash
py project/main.py
```

Or alternatively:

```bash
python project/main.py
```

## Available Commands

| Command | Description |
|---------|-------------|
| `help` | Show available commands |
| `ls` | List directory contents |
| `cd <directory>` | Change directory |
| `pwd` | Print working directory |
| `echo <text>` | Display text |
| `clear` | Clear the screen |
| `history` | Show command history |
| `mkdir <directory>` | Create directories |
| `rm <file/directory>` | Remove files and directories |
| `exec <file.py>` | Execute Python files |
| `script <script.sh>` | Execute shell scripts |
| `exit` | Exit the terminal |

## Usage Examples

```bash
# List files in current directory
ls

# Change to a subdirectory
cd project

# Go back to parent directory
cd ..

# Print current directory
pwd

# Display text
echo Hello, World!

# Create a new directory
mkdir new_folder

# Remove a file
rm old_file.txt

# Clear the screen
clear

# Show command history
history

# Execute a Python file
exec test_exec.py

# Execute a shell script
script sample_script.sh

# Get help
help
```

## How It Works

This terminal interface:
1. Displays a prompt showing the current directory
2. Accepts user input and parses commands
3. Handles built-in commands internally
4. Delegates system commands to the underlying OS
5. Maintains a history of entered commands
6. Provides error handling for invalid commands or paths

## Customization

You can extend the terminal by adding new commands to the respective modules:
- File system operations: `filesystem.py`
- Shell script execution: `shell_scripts.py`
- Miscellaneous commands: `misc.py`

## License

This project is open source and available under the MIT License.
