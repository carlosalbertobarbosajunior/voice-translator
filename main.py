"""
Main entry point for voice translator application.

This script provides a command-line interface for voice translation
between Portuguese (Brazil) and English.
"""

import argparse
import os
import sys
from models.voiceTranslator import VoiceTranslator
from models.utils.languageConfig import LanguageConfig, LanguageCode
from interface.audioInput import AudioInput


def main():
    """Main function to run voice translator."""
    parser = argparse.ArgumentParser(
        description="Voice Translator - Translate voice between languages using AI models"
    )
    parser.add_argument(
        "--source",
        type=str,
        default=LanguageCode.PORTUGUESE_BR,
        choices=[LanguageCode.PORTUGUESE_BR, LanguageCode.ENGLISH],
        help="Source language code"
    )
    parser.add_argument(
        "--target",
        type=str,
        default=LanguageCode.ENGLISH,
        choices=[LanguageCode.PORTUGUESE_BR, LanguageCode.ENGLISH],
        help="Target language code"
    )
    parser.add_argument(
        "--input",
        type=str,
        help="Path to input audio file (if not provided, will record from microphone)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="output_translated.wav",
        help="Path to save translated audio file"
    )
    parser.add_argument(
        "--device",
        type=str,
        choices=["cuda", "cpu"],
        help="Device to run models on (default: auto-detect)"
    )
    parser.add_argument(
        "--record-duration",
        type=float,
        default=5.0,
        help="Recording duration in seconds (when using microphone input)"
    )
    parser.add_argument(
        "--record-until-silence",
        action="store_true",
        help="Record from microphone until silence is detected"
    )
    
    args = parser.parse_args()
    
    # Validate language pair
    if args.source == args.target:
        print("Error: Source and target languages must be different")
        sys.exit(1)
    
    try:
        # Initialize voice translator
        print(f"Initializing voice translator: {LanguageConfig.getLanguageName(args.source)} -> {LanguageConfig.getLanguageName(args.target)}")
        translator = VoiceTranslator(
            sourceLanguage=args.source,
            targetLanguage=args.target,
            device=args.device
        )
        
        # Get audio input
        if args.input:
            # Load from file
            if not os.path.exists(args.input):
                print(f"Error: Input file not found: {args.input}")
                sys.exit(1)
            
            print(f"Processing audio file: {args.input}")
            transcribedText, translatedText, audioData = translator.translateAudio(
                audioPath=args.input,
                outputAudioPath=args.output,
                returnText=True
            )
        else:
            # Record from microphone
            audioInput = AudioInput()
            
            try:
                if args.record_until_silence:
                    print("Recording from microphone (until silence)...")
                    audioData, sampleRate = audioInput.recordUntilSilence()
                else:
                    print(f"Recording from microphone for {args.record_duration} seconds...")
                    audioData, sampleRate = audioInput.recordFromMicrophone(
                        duration=args.record_duration
                    )
                
                # Save temporary recording
                tempInputPath = "temp_input.wav"
                import soundfile as sf
                sf.write(tempInputPath, audioData, sampleRate)
                
                print("Processing recorded audio...")
                transcribedText, translatedText, audioData = translator.translateAudio(
                    audioPath=tempInputPath,
                    outputAudioPath=args.output,
                    returnText=True
                )
                
                # Clean up temporary file
                if os.path.exists(tempInputPath):
                    os.remove(tempInputPath)
            
            finally:
                audioInput.cleanup()
        
        # Display results
        print("\n" + "="*50)
        print("TRANSLATION RESULTS")
        print("="*50)
        print(f"Source Language: {LanguageConfig.getLanguageName(args.source)}")
        print(f"Target Language: {LanguageConfig.getLanguageName(args.target)}")
        print(f"\nOriginal Text ({args.source}):")
        print(f"  {transcribedText}")
        print(f"\nTranslated Text ({args.target}):")
        print(f"  {translatedText}")
        print(f"\nTranslated audio saved to: {args.output}")
        print("="*50)
        
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

