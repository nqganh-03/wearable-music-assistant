#!/usr/bin/env python3
"""
Music Controller
Controls MPD playback based on activity state
"""

import subprocess
import time
from threading import Thread

class MusicController:
    """
    Controls music playback using MPD
    """
    
    # Activity to folder mapping
    ACTIVITY_PLAYLISTS = {
        0: "lowactivity",   # STATE_LOWACTIVITY
        1: "walking",       # STATE_WALKING
        2: "fastwalk",      # STATE_FASTWALK
        3: "running"        # STATE_RUNNING
    }
    
    def __init__(self, display_manager=None):
        self.current_activity = None
        self.is_playing = False
        self.user_paused = False  # Track manual pause by user
        self.display = display_manager
        self.current_song = ""
        
        # Start song monitor thread
        self.monitoring = True
        self.monitor_thread = Thread(target=self._monitor_song_changes, daemon=True)
        self.monitor_thread.start()
        
    def _run_mpc(self, command):
        """Execute MPC command"""
        try:
            result = subprocess.run(
                ['mpc'] + command.split(),
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception as e:
            print(f"MPC error: {e}")
            return False
    
    def _get_current_song(self):
        """Get currently playing song name from MPD"""
        try:
            result = subprocess.run(
                ['mpc', 'current'],
                capture_output=True,
                text=True,
                timeout=2
            )
            song_name = result.stdout.strip()
            return song_name if song_name else "Unknown"
        except:
            return "Unknown"
    
    def _monitor_song_changes(self):
        """Background thread to monitor song changes and update display"""
        while self.monitoring:
            if self.is_playing and self.display:
                current = self._get_current_song()
                if current != self.current_song and current != "Unknown":
                    self.current_song = current
                    self.display.update_song(current)
            time.sleep(1)  # Check every second
    
    def switch_playlist(self, activity_state):
        """
        Switch playlist based on activity state
        
        Args:
            activity_state: Integer state (0-3)
        """
        if activity_state == self.current_activity:
            return  # Already playing this playlist
        
        playlist_name = self.ACTIVITY_PLAYLISTS.get(activity_state, "lowactivity")
        
        print(f"\n[Music] Switching to: {playlist_name.upper()}")
        
        # Clear current playlist
        self._run_mpc('clear')
        
        # Add all songs from activity folder
        self._run_mpc(f'add {playlist_name}')
        
        # Start playing
        self._run_mpc('play')
        
        self.current_activity = activity_state
        self.is_playing = True
        
        # Update display with song name
        if self.display:
            time.sleep(0.1)  # Give MPD time to start
            song_name = self._get_current_song()
            self.display.update_song(song_name)
    
    def play(self):
        """Resume playback"""
        self._run_mpc('play')
        self.is_playing = True
        self.user_paused = False  # Clear manual pause flag
        print("[Music] Playing")
    
    def pause(self):
        """Pause playback"""
        self._run_mpc('pause')
        self.is_playing = False
        self.user_paused = True  # Set manual pause flag
        print("[Music] Paused by user")
    
    def stop(self):
        """Stop playback"""
        self._run_mpc('stop')
        self.is_playing = False
        print("[Music] Stopped")
    
    def cleanup(self):
        """Stop monitoring thread"""
        self.monitoring = False
        if self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=1)
    
    def volume_up(self):
        """Increase volume by 10%"""
        self._run_mpc('volume +10')
        print("[Music] Volume up")
    
    def volume_down(self):
        """Decrease volume by 10%"""
        self._run_mpc('volume -10')
        print("[Music] Volume down")
    
    def get_status(self):
        """Get current playback status"""
        try:
            result = subprocess.run(
                ['mpc', 'status'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.stdout
        except:
            return "Status unavailable"


if __name__ == "__main__":
    # Test music controller
    music = MusicController()
    
    print("Testing music controller...\n")
    
    # Test each activity
    for activity in range(4):
        music.switch_playlist(activity)
        time.sleep(2)
    
    print("\n✓ Music controller test complete!")
    music.stop()
