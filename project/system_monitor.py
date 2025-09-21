import os
import sys
import subprocess
import time
import threading
import psutil
from datetime import datetime, timedelta
from pathlib import Path
import curses

class SystemMonitor:
    def __init__(self, update_interval=1):
        """Initializes the SystemMonitor state."""
        self.running = False
        self.update_interval = update_interval
        self.sort_key = 'cpu_percent'  # Default sort key for processes

        # For calculating I/O rates
        self.last_time = time.time()
        self.last_net_io = psutil.net_io_counters()
        self.last_disk_io = psutil.disk_io_counters()

    def _init_colors(self):
        """Initializes color pairs for the curses interface."""
        curses.start_color()
        curses.use_default_colors()
        # Pair 1: Header/Title (White on Blue)
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)
        # Pair 2: Normal Text (Default)
        curses.init_pair(2, -1, -1)
        # Pair 3: Highlight/High Usage (Yellow on Default)
        curses.init_pair(3, curses.COLOR_YELLOW, -1)
        # Pair 4: Critical/Very High Usage (Red on Default)
        curses.init_pair(4, curses.COLOR_RED, -1)
        # Pair 5: Progress Bar Fill (Green on Default)
        curses.init_pair(5, curses.COLOR_GREEN, -1)

    def format_bytes(self, b):
        """Converts bytes to a human-readable format (KB, MB, GB, etc.)."""
        if b is None: return "N/A"
        power = 1024
        n = 0
        power_labels = {0: '', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
        while b >= power and n < len(power_labels):
            b /= power
            n += 1
        return f"{b:.1f} {power_labels[n]}B"

    def get_system_info(self):
        """Gathers general system information like uptime."""
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time
        return {
            'uptime': str(uptime).split('.')[0],
        }

    def get_io_rates(self):
        """Calculates current network and disk I/O rates."""
        current_time = time.time()
        time_delta = current_time - self.last_time
        if time_delta == 0:
            return {'dl_rate': 0, 'ul_rate': 0, 'read_rate': 0, 'write_rate': 0}

        # Network
        current_net_io = psutil.net_io_counters()
        dl_rate = (current_net_io.bytes_recv - self.last_net_io.bytes_recv) / time_delta
        ul_rate = (current_net_io.bytes_sent - self.last_net_io.bytes_sent) / time_delta
        self.last_net_io = current_net_io

        # Disk
        current_disk_io = psutil.disk_io_counters()
        read_rate = (current_disk_io.read_bytes - self.last_disk_io.read_bytes) / time_delta
        write_rate = (current_disk_io.write_bytes - self.last_disk_io.write_bytes) / time_delta
        self.last_disk_io = current_disk_io

        self.last_time = current_time
        return {
            'dl_rate': self.format_bytes(dl_rate) + '/s',
            'ul_rate': self.format_bytes(ul_rate) + '/s',
            'read_rate': self.format_bytes(read_rate) + '/s',
            'write_rate': self.format_bytes(write_rate) + '/s',
        }

    def get_process_info(self, limit=10):
        """Gathers information about top processes, sorted by a key."""
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'username']):
            try:
                # cpu_percent can be None on the first call
                if proc.info['cpu_percent'] is not None:
                    processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        processes.sort(key=lambda x: x.get(self.sort_key, 0), reverse=True)
        return processes[:limit]

    def draw_progress_bar(self, stdscr, y, x, width, percent):
        """Draws a text-based progress bar."""
        filled_width = int(percent / 100 * width)
        
        color = curses.color_pair(5) # Green
        if percent > 75:
            color = curses.color_pair(3) # Yellow
        if percent > 90:
            color = curses.color_pair(4) # Red
            
        bar = '█' * filled_width + '─' * (width - filled_width)
        try:
            stdscr.addstr(y, x, f"[{bar}] {percent:.1f}%", color)
        except curses.error:
            pass # Avoid crashing if it tries to draw off-screen

    def draw_dashboard(self, stdscr):
        """The main drawing function for the entire dashboard."""
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        current_y = 0

        # --- Header ---
        header_text = "SYSTEM MONITOR  |  Press 'c' to sort by CPU, 'm' by Mem  |  Press Ctrl+X to Exit"
        try:
            stdscr.addstr(current_y, 0, header_text.ljust(w), curses.color_pair(1))
            current_y += 2
        except curses.error:
            return # Screen too small to draw anything

        # --- System & I/O Info ---
        sys_info = self.get_system_info()
        io_rates = self.get_io_rates()
        info_line1 = f"Uptime: {sys_info['uptime']} | Network D/L: {io_rates['dl_rate']:>10} | Disk Read: {io_rates['read_rate']:>10}"
        info_line2 = f"Time: {datetime.now().strftime('%H:%M:%S')}   | Network U/L: {io_rates['ul_rate']:>10} | Disk Write: {io_rates['write_rate']:>10}"
        if w > len(info_line1): stdscr.addstr(current_y, 2, info_line1); current_y += 1
        if w > len(info_line2): stdscr.addstr(current_y, 2, info_line2); current_y += 2

        # --- CPU Info ---
        cpu_percent = psutil.cpu_percent(interval=None)
        cpu_freq = psutil.cpu_freq()
        if w > 10: stdscr.addstr(current_y, 2, f"CPU Usage ({psutil.cpu_count()} Cores, {cpu_freq.current:.0f} MHz):")
        if w > 40: self.draw_progress_bar(stdscr, current_y + 1, 2, w - 20, cpu_percent)
        current_y += 3

        # --- Memory Info ---
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        if w > 10: stdscr.addstr(current_y, 2, "Memory Usage:")
        if w > 40: self.draw_progress_bar(stdscr, current_y + 1, 2, w - 20, mem.percent)
        if w > 40: stdscr.addstr(current_y + 1, w - 16, f"{self.format_bytes(mem.used)}/{self.format_bytes(mem.total)}")
        if w > 10: stdscr.addstr(current_y + 2, 2, "Swap Usage:")
        if w > 40: self.draw_progress_bar(stdscr, current_y + 3, 2, w - 20, swap.percent)
        if w > 40: stdscr.addstr(current_y + 3, w - 16, f"{self.format_bytes(swap.used)}/{self.format_bytes(swap.total)}")
        current_y += 5

        # --- Disk Partitions ---
        if w > 10: stdscr.addstr(current_y, 2, "Disk Partitions:")
        current_y += 1
        partitions = psutil.disk_partitions()
        for p in partitions:
            if current_y >= h - 4: break # Stop if no more space
            try:
                usage = psutil.disk_usage(p.mountpoint)
                if w > 10: stdscr.addstr(current_y, 2, f"{p.device[:15]:<15} {p.mountpoint[:w-60]:<20}")
                if w > 60: self.draw_progress_bar(stdscr, current_y, 40, w - 60, usage.percent)
                current_y += 1
            except FileNotFoundError:
                continue # Skip removable media that isn't present
        current_y += 1

        # --- Process List ---
        num_procs_to_show = h - current_y - 2
        if num_procs_to_show > 1:
            procs = self.get_process_info(limit=num_procs_to_show)
            sort_indicator_cpu = '▼' if self.sort_key == 'cpu_percent' else ''
            sort_indicator_mem = '▼' if self.sort_key == 'memory_percent' else ''
            
            p_header = f"{'PID':<8} {'USER':<12} {'CPU%'+sort_indicator_cpu:<8} {'MEM%'+sort_indicator_mem:<8} {'NAME'}"
            if w > 10: stdscr.addstr(current_y, 0, p_header.ljust(w), curses.color_pair(1))
            current_y += 1
            for p in procs:
                p_line = (f"{p['pid']:<8} "
                          f"{str(p.get('username', 'N/A'))[:12]:<12} "
                          f"{p.get('cpu_percent', 0):<8.1f} "
                          f"{p.get('memory_percent', 0):<8.1f} "
                          f"{p.get('name', 'N/A')}")
                if w > len(p_line):
                    stdscr.addstr(current_y, 1, p_line[:w-2])
                    current_y += 1
                if current_y >= h -1: break

        stdscr.refresh()

    def start_dashboard(self):
        """Entry point to start the curses dashboard loop."""
        self.running = True
        # Wrapper handles terminal setup and restoration
        curses.wrapper(self._dashboard_loop)

    def _dashboard_loop(self, stdscr):
        """The main loop that handles drawing, timing, and input."""
        curses.curs_set(0) # Hide the cursor
        stdscr.nodelay(True) # Non-blocking input
        self._init_colors()

        # Call once before the loop to initialize psutil's cpu_percent
        psutil.cpu_percent(interval=None)

        while self.running:
            # Handle user input
            try:
                key = stdscr.getch()
                if key == 24: # Ctrl+X
                    self.running = False
                elif key == ord('c'):
                    self.sort_key = 'cpu_percent'
                elif key == ord('m'):
                    self.sort_key = 'memory_percent'
                elif key == curses.KEY_RESIZE:
                    # Let the loop handle the redraw on resize
                    pass
            except curses.error:
                # No input
                pass

            # Draw the screen
            self.draw_dashboard(stdscr)
            
            # Wait for the next update
            time.sleep(self.update_interval)

    def stop_dashboard(self):
        self.running = False


if __name__ == "__main__":
    monitor = SystemMonitor(update_interval=1) # Refresh every 1 second
    try:
        monitor.start_dashboard()
    except KeyboardInterrupt:
        print("System monitor stopped.")
    finally:
        print("Exiting.")