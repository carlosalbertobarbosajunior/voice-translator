"""
Example usage of the voice translator as a Python module.

This script demonstrates how to use the VoiceTranslator class
programmatically in your own code.
"""

from models.voiceTranslator import VoiceTranslator
from models.utils.languageConfig import LanguageCode
from interface.audioInput import AudioInput


def exampleTranslateFromFile():
    """Example: Translate from an audio file."""
    print("=" * 50)
    print("Example 1: Translate from audio file")
    print("=" * 50)
    
    # Initialize translator
    translator = VoiceTranslator(
        sourceLanguage=LanguageCode.PORTUGUESE_BR,
        targetLanguage=LanguageCode.ENGLISH
    )
    
    # Translate audio file
    transcribedText, translatedText, audioData = translator.translateAudio(
        audioPath="inputAudio.wav",  # Replace with your audio file path
        outputAudioPath="outputTranslated.wav",
        returnText=True
    )
    
    print(f"Transcribed: {transcribedText}")
    print(f"Translated: {translatedText}")
    print("Audio saved to outputTranslated.wav")


def exampleTranslateFromMicrophone():
    """Example: Record from microphone and translate."""
    print("\n" + "=" * 50)
    print("Example 2: Record from microphone and translate")
    print("=" * 50)
    
    # Initialize audio input
    audioInput = AudioInput(sampleRate=16000)
    
    try:
        # Record audio
        print("Recording 5 seconds of audio...")
        audioData, sampleRate = audioInput.recordFromMicrophone(duration=5.0)
        
        # Initialize translator
        translator = VoiceTranslator(
            sourceLanguage=LanguageCode.ENGLISH,
            targetLanguage=LanguageCode.PORTUGUESE_BR
        )
        
        # Translate
        transcribedText, translatedText, outputAudio = translator.translateAudioFromArray(
            audioArray=audioData,
            sampleRate=sampleRate,
            outputAudioPath="translatedOutput.wav",
            returnText=True
        )
        
        print(f"Transcribed: {transcribedText}")
        print(f"Translated: {translatedText}")
        print("Audio saved to translatedOutput.wav")
    
    finally:
        audioInput.cleanup()


def exampleChangeLanguages():
    """Example: Change languages dynamically."""
    print("\n" + "=" * 50)
    print("Example 3: Change languages dynamically")
    print("=" * 50)
    
    # Initialize translator
    translator = VoiceTranslator(
        sourceLanguage=LanguageCode.PORTUGUESE_BR,
        targetLanguage=LanguageCode.ENGLISH
    )
    
    # Translate in one direction
    print("Translating Portuguese -> English")
    # ... use translator ...
    
    # Change languages
    translator.setLanguages(
        sourceLanguage=LanguageCode.ENGLISH,
        targetLanguage=LanguageCode.PORTUGUESE_BR
    )
    
    print("Now translating English -> Portuguese")
    # ... use translator ...


if __name__ == "__main__":
    print("Voice Translator - Example Usage")
    print("\nNote: These examples require audio files or microphone access.")
    print("Uncomment the example you want to run.\n")
    
    # Uncomment the example you want to run:
    # exampleTranslateFromFile()
    # exampleTranslateFromMicrophone()
    # exampleChangeLanguages()
    
    print("\nFor command-line usage, run: python main.py --help")

