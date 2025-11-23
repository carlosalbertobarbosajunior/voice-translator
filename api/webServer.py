"""
Web server for voice translator GUI.

This module provides a Flask web server with REST API endpoints
for voice recording, translation, and audio playback.
"""

from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import os
import tempfile
import numpy as np
import soundfile as sf
from typing import Optional, Tuple
from models.voiceTranslator import VoiceTranslator
from models.utils.languageConfig import LanguageConfig, LanguageCode
import threading
import uuid

app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

# Global translator instance
translator: Optional[VoiceTranslator] = None
translatorLock = threading.Lock()

# Temporary storage for audio files
audioStorage = {}


def getTranslator(sourceLanguage: str, targetLanguage: str) -> VoiceTranslator:
    """
    Get or create translator instance.
    
    Args:
        sourceLanguage: Source language code
        targetLanguage: Target language code
    
    Returns:
        VoiceTranslator instance
    """
    global translator
    
    with translatorLock:
        if translator is None or \
           translator.sourceLanguage != sourceLanguage or \
           translator.targetLanguage != targetLanguage:
            translator = VoiceTranslator(
                sourceLanguage=sourceLanguage,
                targetLanguage=targetLanguage
            )
        return translator


@app.route('/')
def index():
    """Serve main page."""
    return render_template('index.html')


@app.route('/api/languages', methods=['GET'])
def getLanguages():
    """Get list of supported languages."""
    languages = [
        {
            'code': LanguageCode.PORTUGUESE_BR,
            'name': LanguageConfig.getLanguageName(LanguageCode.PORTUGUESE_BR)
        },
        {
            'code': LanguageCode.ENGLISH,
            'name': LanguageConfig.getLanguageName(LanguageCode.ENGLISH)
        }
    ]
    return jsonify({'languages': languages})


@app.route('/api/translate', methods=['POST'])
def translate():
    """
    Translate audio from uploaded file or base64 audio data.
    
    Expected JSON:
    {
        "audioData": "base64 encoded audio data" (optional),
        "sourceLanguage": "pt-BR",
        "targetLanguage": "en"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        sourceLanguage = data.get('sourceLanguage', LanguageCode.PORTUGUESE_BR)
        targetLanguage = data.get('targetLanguage', LanguageCode.ENGLISH)
        
        # Validate languages
        if sourceLanguage == targetLanguage:
            return jsonify({'error': 'Source and target languages must be different'}), 400
        
        if not LanguageConfig.isSupported(sourceLanguage) or \
           not LanguageConfig.isSupported(targetLanguage):
            return jsonify({'error': 'Unsupported language'}), 400
        
        # Get translator
        translatorInstance = getTranslator(sourceLanguage, targetLanguage)
        
        # Handle audio data
        audioData = data.get('audioData')
        if not audioData:
            return jsonify({'error': 'No audio data provided'}), 400
        
        # Decode base64 audio data and convert to WAV
        import base64
        from pydub import AudioSegment
        import io
        
        try:
            # Remove data URL prefix if present
            audioDataClean = audioData.split(',')[1] if ',' in audioData else audioData
            audioBytes = base64.b64decode(audioDataClean)
            
            # Get audio format from request or default to webm
            audioFormat = data.get('audioFormat', 'webm')
            
            # Create AudioSegment from bytes
            audioSegment = AudioSegment.from_file(
                io.BytesIO(audioBytes),
                format=audioFormat
            )
            
            # Convert to mono and 16kHz
            audioSegment = audioSegment.set_channels(1)
            audioSegment = audioSegment.set_frame_rate(16000)
            
            # Export to WAV bytes
            wavBuffer = io.BytesIO()
            audioSegment.export(wavBuffer, format="wav")
            wavBytes = wavBuffer.getvalue()
            
            # Convert to numpy array (skip WAV header, start from byte 44)
            audioArray = np.frombuffer(wavBytes[44:], dtype=np.int16)
            audioArray = audioArray.astype(np.float32) / 32768.0
            
            sampleRate = 16000
            
        except Exception as e:
            return jsonify({'error': f'Failed to decode audio: {str(e)}'}), 400
        
        # Translate
        try:
            transcribedText, translatedText, translatedAudio = translatorInstance.translateAudioFromArray(
                audioArray=audioArray,
                sampleRate=sampleRate,
                outputAudioPath=None,
                returnText=True
            )
            
            # Save translated audio to temporary file
            audioId = str(uuid.uuid4())
            audioPath = os.path.join(tempfile.gettempdir(), f"translated_{audioId}.wav")
            sf.write(audioPath, translatedAudio, 16000)
            audioStorage[audioId] = audioPath
            
            return jsonify({
                'success': True,
                'originalText': transcribedText,
                'translatedText': translatedText,
                'audioId': audioId
            })
            
        except Exception as e:
            return jsonify({'error': f'Translation failed: {str(e)}'}), 500
    
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@app.route('/api/audio/<audioId>', methods=['GET'])
def getAudio(audioId: str):
    """
    Get translated audio file.
    
    Args:
        audioId: Audio file ID returned from translate endpoint
    """
    if audioId not in audioStorage:
        return jsonify({'error': 'Audio not found'}), 404
    
    audioPath = audioStorage[audioId]
    if not os.path.exists(audioPath):
        return jsonify({'error': 'Audio file not found'}), 404
    
    return send_file(
        audioPath,
        mimetype='audio/wav',
        as_attachment=False,
        download_name='translated.wav'
    )


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({'status': 'ok', 'service': 'voice-translator'})


if __name__ == '__main__':
    # Run development server
    app.run(host='0.0.0.0', port=5000, debug=True)

