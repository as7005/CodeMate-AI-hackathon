import os
import sys
import subprocess
import time
import threading
import psutil
from datetime import datetime
from pathlib import Path

import psutil
import time
import curses
from datetime import datetime

class SystemMonitor:
    def __init__(self):
        self.running = False
        self.dashboard_active = False
        self.update_interval = 0.25  # 250 ms refresh

    def get_cpu_info(self):
        cpu_freq = psutil.cpu_freq()
        return {
            'percent': psutil.cpu_percent(interval=None),
            'count': psutil.cpu_count(),
            'frequency': cpu_freq.current if cpu_freq else None,
            'per_core': psutil.cpu_percent(interval=None, percpu=True)
        }

    def get_memory_info(self):
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        return {
            'total': memory.total, 'available': memory.available,
            'used': memory.used, 'percent': memory.percent,
            'swap_total': swap.total, 'swap_used': swap.used,
            'swap_percent': swap.percent
        }

    def get_process_info(self, limit=10):
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'username']):
            try:
                if proc.info['cpu_percent'] is not None:
                    processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        processes.sort(key=lambda x: x.get('cpu_percent', 0), reverse=True)
        return processes[:limit]

    def get_system_info(self):
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time
        return {
            'boot_time': boot_time.strftime('%Y-%m-%d %H:%M:%S'),
            'uptime': str(uptime).split('.')[0],
        }

    def format_bytes(self, bytes_value):
        if bytes_value is None: return "N/A"
        power = 1024
        n = 0
        power_labels = {0: '', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
        while bytes_value >= power and n < len(power_labels) - 1:
            bytes_value /= power
            n += 1
        return f"{bytes_value:.1f} {power_labels[n]}B"

    def start_dashboard(self):
        self.running = True
        self.dashboard_active = True

        def dashboard_loop(stdscr):
            curses.curs_set(0)  # hide cursor
            stdscr.nodelay(True)  # non-blocking input

            while self.running:
                stdscr.clear()

                # collect info
                cpu_info = self.get_cpu_info()
                mem_info = self.get_memory_info()
                proc_info = self.get_process_info()
                sys_info = self.get_system_info()

                # header
                stdscr.addstr(0, 0, "SYSTEM MONITOR DASHBOARD (Press 'q' to exit)")
                stdscr.addstr(1, 0, "=" * 70)
                stdscr.addstr(2, 0, f"Uptime: {sys_info['uptime']} | Boot: {sys_info['boot_time']}")

                # CPU
                stdscr.addstr(4, 0, f"CPU Usage: {cpu_info['percent']:.1f}% | Cores: {cpu_info['count']}")
                if cpu_info['frequency']:
                    stdscr.addstr(5, 0, f"Frequency: {cpu_info['frequency']:.1f} MHz")

                # Memory
                stdscr.addstr(7, 0, f"RAM:  {self.format_bytes(mem_info['used'])} / "
                                     f"{self.format_bytes(mem_info['total'])} ({mem_info['percent']:.1f}%)")
                stdscr.addstr(8, 0, f"Swap: {self.format_bytes(mem_info['swap_used'])} / "
                                     f"{self.format_bytes(mem_info['swap_total'])} ({mem_info['swap_percent']:.1f}%)")

                # Processes
                stdscr.addstr(10, 0, "TOP PROCESSES BY CPU:")
                stdscr.addstr(11, 0, f"{'PID':<8} {'NAME':<20} {'CPU%':<6} {'MEM%':<6} USER")
                y = 12
                for p in proc_info:
                    stdscr.addstr(y, 0, f"{p['pid']:<8} {p['name'][:20]:<20} "
                                         f"{p['cpu_percent']:<6.1f} {p['memory_percent']:<6.1f} {p['username']}")
                    y += 1

                stdscr.refresh()
                time.sleep(self.update_interval)

                # keypress check
                try:
                    key = stdscr.getch()
                    if key == ord('q'):  # quit on 'q'
                        self.stop_dashboard()
                        break
                except:
                    pass

        curses.wrapper(dashboard_loop)

    def stop_dashboard(self):
        self.running = False
        self.dashboard_active = False
