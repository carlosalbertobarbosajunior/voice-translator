"""
Audio input interface module.

This module handles audio input from various sources:
- Audio files
- Microphone input
- Real-time audio streaming
"""

import numpy as np
import soundfile as sf
import pyaudio
from typing import Optional, Tuple
import wave
import tempfile
import os


class AudioInput:
    """Interface for audio input from files or microphone."""
    
    def __init__(self, sampleRate: int = 16000, chunkSize: int = 1024):
        """
        Initialize audio input interface.
        
        Args:
            sampleRate: Sample rate for audio recording
            chunkSize: Chunk size for audio buffer
        """
        self.sampleRate = sampleRate
        self.chunkSize = chunkSize
        self.audio = None
        self.stream = None
    
    def loadFromFile(self, filePath: str) -> Tuple[np.ndarray, int]:
        """
        Load audio from file.
        
        Args:
            filePath: Path to audio file
        
        Returns:
            Tuple of (audioData, sampleRate)
        """
        audioData, sampleRate = sf.read(filePath)
        
        # Convert to mono if stereo
        if len(audioData.shape) > 1:
            audioData = np.mean(audioData, axis=1)
        
        return audioData, sampleRate
    
    def recordFromMicrophone(
        self,
        duration: float = 5.0,
        outputPath: Optional[str] = None
    ) -> Tuple[np.ndarray, int]:
        """
        Record audio from microphone.
        
        Args:
            duration: Recording duration in seconds
            outputPath: Optional path to save recorded audio
        
        Returns:
            Tuple of (audioData, sampleRate)
        """
        self.audio = pyaudio.PyAudio()
        
        # Open audio stream
        self.stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.sampleRate,
            input=True,
            frames_per_buffer=self.chunkSize
        )
        
        print(f"Recording for {duration} seconds...")
        frames = []
        
        for _ in range(0, int(self.sampleRate / self.chunkSize * duration)):
            data = self.stream.read(self.chunkSize)
            frames.append(data)
        
        print("Recording finished!")
        
        # Stop and close stream
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()
        
        # Convert to numpy array
        audioData = np.frombuffer(b''.join(frames), dtype=np.int16)
        audioData = audioData.astype(np.float32) / 32768.0  # Normalize to [-1, 1]
        
        # Save to file if path provided
        if outputPath:
            sf.write(outputPath, audioData, self.sampleRate)
        
        return audioData, self.sampleRate
    
    def recordUntilSilence(
        self,
        silenceThreshold: float = 0.01,
        maxDuration: float = 30.0,
        outputPath: Optional[str] = None
    ) -> Tuple[np.ndarray, int]:
        """
        Record audio from microphone until silence is detected.
        
        Args:
            silenceThreshold: Threshold for silence detection
            maxDuration: Maximum recording duration in seconds
            outputPath: Optional path to save recorded audio
        
        Returns:
            Tuple of (audioData, sampleRate)
        """
        self.audio = pyaudio.PyAudio()
        
        # Open audio stream
        self.stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.sampleRate,
            input=True,
            frames_per_buffer=self.chunkSize
        )
        
        print("Recording... (speak now, silence will stop recording)")
        frames = []
        silenceCount = 0
        maxFrames = int(self.sampleRate / self.chunkSize * maxDuration)
        
        for i in range(maxFrames):
            data = self.stream.read(self.chunkSize)
            frames.append(data)
            
            # Check for silence
            audioChunk = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
            if np.abs(audioChunk).mean() < silenceThreshold:
                silenceCount += 1
                if silenceCount > 10:  # 10 consecutive silent chunks
                    print("Silence detected, stopping recording...")
                    break
            else:
                silenceCount = 0
        
        print("Recording finished!")
        
        # Stop and close stream
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()
        
        # Convert to numpy array
        audioData = np.frombuffer(b''.join(frames), dtype=np.int16)
        audioData = audioData.astype(np.float32) / 32768.0  # Normalize to [-1, 1]
        
        # Save to file if path provided
        if outputPath:
            sf.write(outputPath, audioData, self.sampleRate)
        
        return audioData, self.sampleRate
    
    def cleanup(self):
        """Clean up audio resources."""
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        if self.audio:
            self.audio.terminate()

