"""
Graphical user interface for voice translator.

This module provides a GUI for recording, translating, and playing back voice.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import os
import tempfile
from typing import Optional
from models.voiceTranslator import VoiceTranslator
from models.utils.languageConfig import LanguageConfig, LanguageCode
from interface.audioRecorder import AudioRecorder
from interface.audioPlayer import AudioPlayer


class VoiceTranslatorGUI:
    """Main GUI application for voice translator."""
    
    def __init__(self, root: tk.Tk):
        """
        Initialize GUI application.
        
        Args:
            root: Tkinter root window
        """
        self.root = root
        self.root.title("Voice Translator")
        self.root.geometry("800x700")
        self.root.resizable(True, True)
        
        # Initialize components
        self.audioRecorder = AudioRecorder()
        self.audioRecorder.onRecordingUpdate = self.updateRecordingDuration
        self.audioPlayer = AudioPlayer()
        self.voiceTranslator: Optional[VoiceTranslator] = None
        
        # State variables
        self.isRecording = False
        self.recordedAudioPath: Optional[str] = None
        self.translatedAudioPath: Optional[str] = None
        self.currentSourceLanguage = LanguageCode.PORTUGUESE_BR
        self.currentTargetLanguage = LanguageCode.ENGLISH
        
        # Create UI
        self.createWidgets()
        
        # Cleanup on close
        self.root.protocol("WM_DELETE_WINDOW", self.onClose)
    
    def createWidgets(self):
        """Create and arrange GUI widgets."""
        # Main container
        mainFrame = ttk.Frame(self.root, padding="10")
        mainFrame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        mainFrame.columnconfigure(1, weight=1)
        
        # Title
        titleLabel = ttk.Label(
            mainFrame,
            text="Voice Translator",
            font=("Arial", 18, "bold")
        )
        titleLabel.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Language selection frame
        langFrame = ttk.LabelFrame(mainFrame, text="Language Selection", padding="10")
        langFrame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        langFrame.columnconfigure(1, weight=1)
        langFrame.columnconfigure(3, weight=1)
        
        # Source language
        ttk.Label(langFrame, text="From:").grid(row=0, column=0, padx=(0, 5))
        self.sourceLangVar = tk.StringVar(value=LanguageCode.PORTUGUESE_BR)
        sourceLangCombo = ttk.Combobox(
            langFrame,
            textvariable=self.sourceLangVar,
            values=[LanguageCode.PORTUGUESE_BR, LanguageCode.ENGLISH],
            state="readonly",
            width=20
        )
        sourceLangCombo.grid(row=0, column=1, padx=(0, 20))
        sourceLangCombo.bind("<<ComboboxSelected>>", self.onLanguageChanged)
        
        # Target language
        ttk.Label(langFrame, text="To:").grid(row=0, column=2, padx=(0, 5))
        self.targetLangVar = tk.StringVar(value=LanguageCode.ENGLISH)
        targetLangCombo = ttk.Combobox(
            langFrame,
            textvariable=self.targetLangVar,
            values=[LanguageCode.PORTUGUESE_BR, LanguageCode.ENGLISH],
            state="readonly",
            width=20
        )
        targetLangCombo.grid(row=0, column=3)
        targetLangCombo.bind("<<ComboboxSelected>>", self.onLanguageChanged)
        
        # Recording frame
        recordFrame = ttk.LabelFrame(mainFrame, text="Recording", padding="10")
        recordFrame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Record button
        self.recordButton = ttk.Button(
            recordFrame,
            text="🎤 Start Recording",
            command=self.toggleRecording,
            width=20
        )
        self.recordButton.grid(row=0, column=0, padx=5)
        
        # Recording duration label
        self.durationLabel = ttk.Label(recordFrame, text="Duration: 0.0s")
        self.durationLabel.grid(row=0, column=1, padx=10)
        
        # Status label
        self.statusLabel = ttk.Label(recordFrame, text="Ready", foreground="green")
        self.statusLabel.grid(row=0, column=2, padx=10)
        
        # Original text frame
        originalFrame = ttk.LabelFrame(mainFrame, text="Original Text", padding="10")
        originalFrame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        originalFrame.columnconfigure(0, weight=1)
        originalFrame.rowconfigure(0, weight=1)
        mainFrame.rowconfigure(3, weight=1)
        
        self.originalText = scrolledtext.ScrolledText(
            originalFrame,
            height=5,
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.originalText.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Translated text frame
        translatedFrame = ttk.LabelFrame(mainFrame, text="Translated Text", padding="10")
        translatedFrame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        translatedFrame.columnconfigure(0, weight=1)
        translatedFrame.rowconfigure(0, weight=1)
        mainFrame.rowconfigure(4, weight=1)
        
        self.translatedText = scrolledtext.ScrolledText(
            translatedFrame,
            height=5,
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.translatedText.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Playback frame
        playbackFrame = ttk.Frame(mainFrame, padding="10")
        playbackFrame.grid(row=5, column=0, columnspan=3, pady=(0, 10))
        
        self.playButton = ttk.Button(
            playbackFrame,
            text="▶ Play Translated Audio",
            command=self.playTranslatedAudio,
            state=tk.DISABLED
        )
        self.playButton.grid(row=0, column=0, padx=5)
        
        self.stopButton = ttk.Button(
            playbackFrame,
            text="⏹ Stop",
            command=self.stopPlayback,
            state=tk.DISABLED
        )
        self.stopButton.grid(row=0, column=1, padx=5)
        
        # Progress bar
        self.progressBar = ttk.Progressbar(
            mainFrame,
            mode='indeterminate',
            length=400
        )
        self.progressBar.grid(row=6, column=0, columnspan=3, pady=(0, 10), sticky=(tk.W, tk.E))
        
        # Initialize translator
        self.initializeTranslator()
    
    def onLanguageChanged(self, event=None):
        """Handle language selection change."""
        sourceLang = self.sourceLangVar.get()
        targetLang = self.targetLangVar.get()
        
        if sourceLang == targetLang:
            messagebox.showwarning(
                "Invalid Selection",
                "Source and target languages must be different!"
            )
            # Revert to previous selection
            self.sourceLangVar.set(self.currentSourceLanguage)
            self.targetLangVar.set(self.currentTargetLanguage)
            return
        
        self.currentSourceLanguage = sourceLang
        self.currentTargetLanguage = targetLang
        
        # Reinitialize translator with new languages
        self.initializeTranslator()
    
    def initializeTranslator(self):
        """Initialize voice translator with current language settings."""
        try:
            self.statusLabel.config(text="Initializing translator...", foreground="blue")
            self.root.update()
            
            self.voiceTranslator = VoiceTranslator(
                sourceLanguage=self.currentSourceLanguage,
                targetLanguage=self.currentTargetLanguage
            )
            
            self.statusLabel.config(text="Ready", foreground="green")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to initialize translator: {e}")
            self.statusLabel.config(text="Error", foreground="red")
    
    def toggleRecording(self):
        """Toggle recording state."""
        if not self.isRecording:
            self.startRecording()
        else:
            self.stopRecording()
    
    def startRecording(self):
        """Start audio recording."""
        if self.isRecording:
            return
        
        # Create temporary file for recording
        self.recordedAudioPath = os.path.join(tempfile.gettempdir(), "voice_translator_recording.wav")
        
        if self.audioRecorder.startRecording():
            self.isRecording = True
            self.recordButton.config(text="⏹ Stop Recording", state=tk.NORMAL)
            self.statusLabel.config(text="Recording...", foreground="red")
            self.clearTexts()
        else:
            messagebox.showerror("Error", "Failed to start recording. Check microphone permissions.")
    
    def stopRecording(self):
        """Stop audio recording and process translation."""
        if not self.isRecording:
            return
        
        self.isRecording = False
        self.recordButton.config(text="🎤 Start Recording", state=tk.NORMAL)
        self.statusLabel.config(text="Processing...", foreground="blue")
        self.progressBar.start()
        
        # Stop recording in separate thread to avoid blocking
        threading.Thread(target=self.processRecording, daemon=True).start()
    
    def processRecording(self):
        """Process recorded audio and translate."""
        try:
            # Stop recording and get audio data
            audioData = self.audioRecorder.stopRecording()
            
            if audioData is None:
                self.root.after(0, lambda: self.statusLabel.config(text="Recording failed", foreground="red"))
                self.root.after(0, self.progressBar.stop)
                return
            
            audioArray, sampleRate = audioData
            
            # Save recording to file
            if not self.audioRecorder.saveRecording(audioArray, sampleRate, self.recordedAudioPath):
                self.root.after(0, lambda: self.statusLabel.config(text="Failed to save recording", foreground="red"))
                self.root.after(0, self.progressBar.stop)
                return
            
            # Translate audio
            if self.voiceTranslator is None:
                self.initializeTranslator()
            
            self.root.after(0, lambda: self.statusLabel.config(text="Transcribing...", foreground="blue"))
            
            transcribedText, translatedText, translatedAudio = self.voiceTranslator.translateAudioFromArray(
                audioArray=audioArray,
                sampleRate=sampleRate,
                outputAudioPath=None,  # We'll save it ourselves
                returnText=True
            )
            
            # Save translated audio
            self.translatedAudioPath = os.path.join(tempfile.gettempdir(), "voice_translator_translated.wav")
            import soundfile as sf
            if translatedAudio is not None:
                sf.write(self.translatedAudioPath, translatedAudio, 16000)
            
            # Update UI in main thread
            self.root.after(0, lambda: self.updateResults(transcribedText, translatedText))
            
        except Exception as e:
            errorMsg = f"Translation error: {e}"
            print(errorMsg)
            self.root.after(0, lambda: messagebox.showerror("Error", errorMsg))
            self.root.after(0, lambda: self.statusLabel.config(text="Error", foreground="red"))
            self.root.after(0, self.progressBar.stop)
    
    def updateResults(self, originalText: str, translatedText: str):
        """Update UI with translation results."""
        # Update original text
        self.originalText.config(state=tk.NORMAL)
        self.originalText.delete(1.0, tk.END)
        self.originalText.insert(1.0, originalText)
        self.originalText.config(state=tk.DISABLED)
        
        # Update translated text
        self.translatedText.config(state=tk.NORMAL)
        self.translatedText.delete(1.0, tk.END)
        self.translatedText.insert(1.0, translatedText)
        self.translatedText.config(state=tk.DISABLED)
        
        # Enable play button
        self.playButton.config(state=tk.NORMAL)
        
        # Update status
        self.statusLabel.config(text="Translation complete!", foreground="green")
        self.progressBar.stop()
    
    def clearTexts(self):
        """Clear text areas."""
        self.originalText.config(state=tk.NORMAL)
        self.originalText.delete(1.0, tk.END)
        self.originalText.config(state=tk.DISABLED)
        
        self.translatedText.config(state=tk.NORMAL)
        self.translatedText.delete(1.0, tk.END)
        self.translatedText.config(state=tk.DISABLED)
        
        self.playButton.config(state=tk.DISABLED)
    
    def updateRecordingDuration(self, duration: float):
        """Update recording duration display."""
        if self.isRecording:
            self.root.after(0, lambda: self.durationLabel.config(text=f"Duration: {duration:.1f}s"))
    
    def playTranslatedAudio(self):
        """Play translated audio."""
        if self.translatedAudioPath and os.path.exists(self.translatedAudioPath):
            if self.audioPlayer.play(self.translatedAudioPath, self.onPlaybackFinished):
                self.playButton.config(state=tk.DISABLED)
                self.stopButton.config(state=tk.NORMAL)
            else:
                messagebox.showerror("Error", "Failed to play audio")
        else:
            messagebox.showwarning("Warning", "No translated audio available")
    
    def stopPlayback(self):
        """Stop audio playback."""
        self.audioPlayer.stop()
        self.onPlaybackFinished()
    
    def onPlaybackFinished(self):
        """Handle playback finished event."""
        self.playButton.config(state=tk.NORMAL)
        self.stopButton.config(state=tk.DISABLED)
    
    def onClose(self):
        """Handle window close event."""
        self.audioRecorder.cleanup()
        self.audioPlayer.cleanup()
        self.root.destroy()


def main():
    """Main function to run GUI application."""
    root = tk.Tk()
    app = VoiceTranslatorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

