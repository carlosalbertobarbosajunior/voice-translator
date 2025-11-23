"""
Main entry point for web server.

Run this script to start the voice translator web interface.
"""

# Load environment variables from .env file before importing anything else
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✓ Loaded .env file")
except ImportError:
    print("⚠ python-dotenv not installed, .env file will not be loaded")
except Exception as e:
    print(f"⚠ Error loading .env file: {e}")

from api.webServer import app

if __name__ == '__main__':
    print("=" * 50)
    print("Voice Translator Web Server")
    print("=" * 50)
    
    # Check if HF token is available
    from models.utils.hfAuth import getHfToken
    token = getHfToken()
    if token:
        print(f"✓ Hugging Face token found: {token[:10]}...")
    else:
        print("⚠ No Hugging Face token found (may be required for some models)")
        print("  Create a .env file with HF_TOKEN=your_token")
    
    print("Starting server on http://0.0.0.0:5000")
    print("Open your browser and navigate to: http://localhost:5000")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=False)

