"""
Audio player module for GUI interface.

This module handles audio playback functionality.
"""

import pygame
import threading
from typing import Optional, Callable
import os


class AudioPlayer:
    """Audio player for playing translated audio."""
    
    def __init__(self):
        """Initialize audio player."""
        pygame.mixer.init()
        self.isPlaying = False
        self.currentFile: Optional[str] = None
        self.playbackThread: Optional[threading.Thread] = None
        self.onPlaybackFinished: Optional[Callable[[], None]] = None
    
    def play(self, audioPath: str, onFinished: Optional[Callable[[], None]] = None) -> bool:
        """
        Play audio file.
        
        Args:
            audioPath: Path to audio file
            onFinished: Optional callback when playback finishes
        
        Returns:
            True if playback started successfully, False otherwise
        """
        if self.isPlaying:
            self.stop()
        
        if not os.path.exists(audioPath):
            print(f"Audio file not found: {audioPath}")
            return False
        
        try:
            self.currentFile = audioPath
            self.onPlaybackFinished = onFinished
            self.isPlaying = True
            
            # Start playback in separate thread
            self.playbackThread = threading.Thread(
                target=self._playbackLoop,
                daemon=True
            )
            self.playbackThread.start()
            
            return True
        except Exception as e:
            print(f"Error starting playback: {e}")
            self.isPlaying = False
            return False
    
    def _playbackLoop(self):
        """Internal playback loop running in separate thread."""
        try:
            pygame.mixer.music.load(self.currentFile)
            pygame.mixer.music.play()
            
            # Wait for playback to finish
            while pygame.mixer.music.get_busy():
                pygame.time.wait(100)
            
            # Playback finished
            if self.onPlaybackFinished:
                self.onPlaybackFinished()
        except Exception as e:
            print(f"Error in playback loop: {e}")
        finally:
            self.isPlaying = False
    
    def stop(self):
        """Stop audio playback."""
        if self.isPlaying:
            pygame.mixer.music.stop()
            self.isPlaying = False
    
    def isCurrentlyPlaying(self) -> bool:
        """Check if audio is currently playing."""
        return self.isPlaying
    
    def cleanup(self):
        """Clean up audio player resources."""
        self.stop()
        pygame.mixer.quit()

