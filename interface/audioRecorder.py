"""
Audio recorder module for GUI interface.

This module handles audio recording with start/stop functionality,
designed to work in both native and Docker environments.
"""

import numpy as np
import soundfile as sf
import pyaudio
from typing import Optional, Tuple, Callable
import threading
import time
import tempfile
import os


class AudioRecorder:
    """Audio recorder with start/stop functionality for GUI."""
    
    def __init__(
        self,
        sampleRate: int = 16000,
        chunkSize: int = 1024,
        channels: int = 1,
        format: int = pyaudio.paInt16
    ):
        """
        Initialize audio recorder.
        
        Args:
            sampleRate: Sample rate for recording
            chunkSize: Chunk size for audio buffer
            channels: Number of audio channels (1 = mono, 2 = stereo)
            format: Audio format (paInt16, paFloat32, etc.)
        """
        self.sampleRate = sampleRate
        self.chunkSize = chunkSize
        self.channels = channels
        self.format = format
        self.audio = None
        self.stream = None
        self.isRecording = False
        self.recordedFrames = []
        self.recordingThread = None
        self.onRecordingUpdate: Optional[Callable[[float], None]] = None  # Callback for recording duration
    
    def startRecording(self, outputPath: Optional[str] = None) -> bool:
        """
        Start recording audio.
        
        Args:
            outputPath: Optional path to save recorded audio immediately
        
        Returns:
            True if recording started successfully, False otherwise
        """
        if self.isRecording:
            return False
        
        try:
            self.audio = pyaudio.PyAudio()
            self.stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.sampleRate,
                input=True,
                frames_per_buffer=self.chunkSize
            )
            
            self.isRecording = True
            self.recordedFrames = []
            self.startTime = time.time()
            
            # Start recording thread
            self.recordingThread = threading.Thread(
                target=self._recordingLoop,
                args=(outputPath,),
                daemon=True
            )
            self.recordingThread.start()
            
            return True
        except Exception as e:
            print(f"Error starting recording: {e}")
            self.stopRecording()
            return False
    
    def _recordingLoop(self, outputPath: Optional[str] = None):
        """Internal recording loop running in separate thread."""
        try:
            while self.isRecording:
                data = self.stream.read(self.chunkSize, exception_on_overflow=False)
                self.recordedFrames.append(data)
                
                # Call update callback if provided
                if self.onRecordingUpdate:
                    duration = time.time() - self.startTime
                    self.onRecordingUpdate(duration)
                
                # Small sleep to prevent CPU spinning
                time.sleep(0.01)
        except Exception as e:
            print(f"Error in recording loop: {e}")
        finally:
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
            if self.audio:
                self.audio.terminate()
    
    def stopRecording(self) -> Optional[Tuple[np.ndarray, int]]:
        """
        Stop recording and return audio data.
        
        Returns:
            Tuple of (audioData, sampleRate) or None if recording failed
        """
        if not self.isRecording:
            return None
        
        self.isRecording = False
        
        # Wait for recording thread to finish
        if self.recordingThread:
            self.recordingThread.join(timeout=2.0)
        
        # Convert frames to numpy array
        if not self.recordedFrames:
            return None
        
        try:
            # Convert to numpy array
            audioData = np.frombuffer(b''.join(self.recordedFrames), dtype=np.int16)
            audioData = audioData.astype(np.float32) / 32768.0  # Normalize to [-1, 1]
            
            # Convert to mono if stereo
            if self.channels > 1 and len(audioData.shape) > 1:
                audioData = np.mean(audioData, axis=1)
            
            return audioData, self.sampleRate
        except Exception as e:
            print(f"Error processing recorded audio: {e}")
            return None
    
    def saveRecording(self, audioData: np.ndarray, sampleRate: int, outputPath: str) -> bool:
        """
        Save recorded audio to file.
        
        Args:
            audioData: Audio data as numpy array
            sampleRate: Sample rate of the audio
            outputPath: Path to save audio file
        
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            sf.write(outputPath, audioData, sampleRate)
            return True
        except Exception as e:
            print(f"Error saving audio: {e}")
            return False
    
    def getRecordingDuration(self) -> float:
        """
        Get current recording duration in seconds.
        
        Returns:
            Recording duration in seconds, or 0 if not recording
        """
        if not self.isRecording:
            return 0.0
        return time.time() - self.startTime
    
    def cleanup(self):
        """Clean up audio resources."""
        self.stopRecording()
        if self.stream:
            try:
                self.stream.stop_stream()
                self.stream.close()
            except:
                pass
        if self.audio:
            try:
                self.audio.terminate()
            except:
                pass

