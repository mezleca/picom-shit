#!/usr/bin/env python3

import subprocess
import time
import sys
import re

from typing import Tuple

# those windows will be ignored
exceptions = [
    'firefox',
    'chromium',
    'brave',
    'thunar',
    'pcmanfm',
    'nautilus',
    'dolphin',
    'nemo',
    'discord'
]

arguments = sys.argv

def check_arg(name: str) -> bool:
    for v in arguments:
        if v == name:
            return True
            
    return False

class PicomManager:
    def __init__(self):
        self.debug_mode = check_arg("--debug")
        
    def get_active_window_info(self) -> Tuple[str, bool]:
        try:
            xdotool = subprocess.run(
                ['xdotool', 'getactivewindow'],
                capture_output=True,
                text=True
            )
            
            if xdotool.returncode != 0:
                return "unknown", False
                
            window_id = xdotool.stdout.strip()
            xprop_class = subprocess.run(
                ['xprop', '-id', window_id, 'WM_CLASS'],
                capture_output=True,
                text=True
            )
            
            xprop_state = subprocess.run(
                ['xprop', '-id', window_id, '_NET_WM_STATE'],
                capture_output=True,
                text=True
            )
            
            window_class = "unknown"
            if xprop_class.returncode == 0:
                match = re.search(r'WM_CLASS\(STRING\) = "([^"]+)"', xprop_class.stdout)
                if match:
                    window_class = match.group(1)
            
            is_fullscreen = False
            if xprop_state.returncode == 0:
                is_fullscreen = '_NET_WM_STATE_FULLSCREEN' in xprop_state.stdout
            
            return window_class, is_fullscreen
            
        except Exception as e:
            self.log(f"failed to get window data: {e}")
            return "unknown", False
    
    def is_picom_running(self) -> bool:
        try:
            subprocess.run(['pgrep', 'picom'], capture_output=True, check=True)
            return True
        except subprocess.CalledProcessError:
            return False

    def log(self, info: str):
        if (not self.debug_mode or not info):
            return
        print(f"[{time.strftime('%H:%M:%S')}] {info}")
    
    def start_picom(self):
        if not self.is_picom_running():
            try:
                subprocess.run(['picom', '-b'], check=True)
                self.log("enabled picom")
            except subprocess.CalledProcessError as e:
                self.log(f"failed to run picom: {e}")
    
    def kill_picom(self):
        if self.is_picom_running():
            try:
                subprocess.run(['killall', 'picom'], check=True)
                self.log("killed picom")
            except subprocess.CalledProcessError as e:
                self.log(f"failed to kill picom {e}")
    
    def run(self):
        print(f"initialing...\ndebug mode: {self.debug_mode}") 
        previous_state = (None, None)  # (window_class, is_fullscreen)
        while True:
            try:
                window_class, is_fullscreen = self.get_active_window_info()
                current_state = (window_class, is_fullscreen)
                
                if current_state != previous_state:
                    self.log(f"window: {window_class}, fullscreen: {is_fullscreen}")      
                    if is_fullscreen and window_class not in exceptions:
                        self.kill_picom()
                    else:
                        self.start_picom()
                    
                    previous_state = current_state
            
            except Exception as e:
                self.log(f"fucking error: {e}")
            
            time.sleep(1)

if __name__ == "__main__":
    manager = PicomManager()
    manager.run()