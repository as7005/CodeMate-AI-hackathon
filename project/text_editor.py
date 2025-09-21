import curses
from pathlib import Path
import sys

class NanoEditor:
    """
    A simple, Nano-like text editor implemented using Python's curses library.
    """
    def __init__(self, file_path):
        """Initializes the editor with the target file path."""
        self.file_path = Path(file_path)
        self.content = [""]
        self.cursor_y = 0
        self.cursor_x = 0
        self.scroll = 0
        self.modified = False

    def load_file(self):
        """Loads the file content into the editor buffer. If the file doesn't exist, starts with an empty buffer."""
        if self.file_path.exists() and self.file_path.is_file():
            with open(self.file_path, 'r') as f:
                lines = f.readlines()
            # Use rstrip to remove any newline characters, or initialize with one empty line
            self.content = [line.rstrip('\n\r') for line in lines] or [""]
        else:
            self.content = [""]

    def save_file(self):
        """Saves the current buffer content to the file."""
        try:
            with open(self.file_path, 'w') as f:
                f.write("\n".join(self.content))
            self.modified = False
        except IOError as e:
            # In a real app, you'd show this error on the status bar
            # For this example, we'll just handle it silently.
            pass


    def run(self):
        """Starts the editor and wraps the main loop in curses."""
        curses.wrapper(self.main_loop)

    def main_loop(self, stdscr):
        """
        The main event loop for the editor, handling rendering, key presses, and UI.
        """
        curses.curs_set(1)
        stdscr.keypad(True)

        # --- EDIT: Prompt to create the file if it does not exist ---
        if not self.file_path.exists():
            # Explicitly reset state to ensure no data carries over
            self.content = [""]
            self.cursor_y = 0
            self.cursor_x = 0
            self.scroll = 0
            self.modified = False

            stdscr.clear()
            h, w = stdscr.getmaxyx()
            prompt = f"File '{self.file_path.name}' does not exist. Create? (y/n)"
            start_x = max(0, (w - len(prompt)) // 2)
            start_y = h // 2
            stdscr.addstr(start_y, start_x, prompt)
            stdscr.refresh()
            key = stdscr.getch()
            if key not in (ord('y'), ord('Y')):
                return # Exit the application
            # If creating a new file, we skip loading and start fresh.
        else:
            self.load_file()

        while True:
            stdscr.clear()
            h, w = stdscr.getmaxyx()
            # Reserve one line for the status bar
            max_visible_lines = h - 1

            # Adjust vertical scroll based on cursor position
            if self.cursor_y < self.scroll:
                self.scroll = self.cursor_y
            elif self.cursor_y >= self.scroll + max_visible_lines:
                self.scroll = self.cursor_y - max_visible_lines + 1

            # Display the content window
            for i, line in enumerate(self.content[self.scroll:self.scroll + max_visible_lines]):
                # Avoid writing past the screen width, which causes an error
                if len(line) > 0:
                    stdscr.addstr(i, 0, line[:w-1])


            # Draw the status bar
            status_text = f"File: {self.file_path.name}{' (modified)' if self.modified else ''} | Ctrl+S: Save | Ctrl+X: Exit"
            stdscr.addstr(h-1, 0, status_text.ljust(w-1), curses.A_REVERSE)

            # Move cursor to its current position, ensuring it's within screen bounds
            cy = self.cursor_y - self.scroll
            cx = min(self.cursor_x, w - 1)
            stdscr.move(cy, cx)
            stdscr.refresh()

            # Handle user input
            key = stdscr.getch()
            # If handle_key returns True, it's a signal to exit.
            if self.handle_key(key, stdscr):
                break


    def handle_key(self, key, stdscr):
        """Processes a single key press. Returns True to signal exit, otherwise False."""
        current_line = self.content[self.cursor_y]

        if key == curses.KEY_UP:
            if self.cursor_y > 0:
                self.cursor_y -= 1
                self.cursor_x = min(self.cursor_x, len(self.content[self.cursor_y]))
        elif key == curses.KEY_DOWN:
            if self.cursor_y < len(self.content) - 1:
                self.cursor_y += 1
                self.cursor_x = min(self.cursor_x, len(self.content[self.cursor_y]))
        elif key == curses.KEY_LEFT:
            if self.cursor_x > 0:
                self.cursor_x -= 1
            elif self.cursor_y > 0: # Move to the end of the previous line
                self.cursor_y -= 1
                self.cursor_x = len(self.content[self.cursor_y])
        elif key == curses.KEY_RIGHT:
            if self.cursor_x < len(current_line):
                self.cursor_x += 1
            elif self.cursor_y < len(self.content) - 1: # Move to the start of the next line
                self.cursor_y += 1
                self.cursor_x = 0
        elif key in (curses.KEY_BACKSPACE, 127, 8): # Recognize multiple backspace codes
            if self.cursor_x > 0:
                self.content[self.cursor_y] = current_line[:self.cursor_x - 1] + current_line[self.cursor_x:]
                self.cursor_x -= 1
                self.modified = True
            elif self.cursor_y > 0: # Join with the previous line
                prev_line_len = len(self.content[self.cursor_y - 1])
                self.content[self.cursor_y - 1] += self.content.pop(self.cursor_y)
                self.cursor_y -= 1
                self.cursor_x = prev_line_len
                self.modified = True
        elif key == 10:  # Enter key
            self.content[self.cursor_y] = current_line[:self.cursor_x]
            self.content.insert(self.cursor_y + 1, current_line[self.cursor_x:])
            self.cursor_y += 1
            self.cursor_x = 0
            self.modified = True
        elif key == 24:  # Ctrl+X
            if self.modified:
                h, w = stdscr.getmaxyx()
                prompt = "Save modified buffer? (Y/N/C for Cancel)"
                # Keep prompting until a valid key is pressed
                while True:
                    stdscr.addstr(h - 1, 0, prompt.ljust(w - 1), curses.A_REVERSE)
                    stdscr.move(self.cursor_y - self.scroll, self.cursor_x) # Keep cursor visible
                    stdscr.refresh()
                    choice = stdscr.getch()
                    if choice in (ord('y'), ord('Y')):
                        self.save_file()
                        return True # Signal main_loop to exit
                    elif choice in (ord('n'), ord('N')):
                        return True # Signal main_loop to exit
                    elif choice in (ord('c'), ord('C'), 27): # 27 is Escape key
                        # Cancel exit, so break inner loop and continue editing
                        return False
            else:
                 return True # Not modified, signal main_loop to exit
        elif key == 19:  # Ctrl+S
            self.save_file()
        # Check for printable characters
        elif key >= 32 and key <= 126:
            char = chr(key)
            self.content[self.cursor_y] = current_line[:self.cursor_x] + char + current_line[self.cursor_x:]
            self.cursor_x += 1
            self.modified = True
        
        return False # Do not exit

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python nano_editor.py <filename>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    editor = NanoEditor(file_path)
    editor.run()