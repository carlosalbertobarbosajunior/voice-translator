# Voice Translator

Voice translator using open source AI models from Hugging Face. Translate voice input between Portuguese (Brazil) and English using state-of-the-art ASR, translation, and TTS models.

## Features

- **Speech-to-Text (ASR)**: Uses OpenAI Whisper models for accurate transcription
- **Text Translation**: Uses MBART models for high-quality translation
- **Text-to-Speech (TTS)**: Generates natural-sounding speech in the target language
- **Multiple Input Methods**: Support for audio files and microphone input
- **Graphical User Interface**: Easy-to-use GUI with recording, translation, and playback
- **Extensible Architecture**: Designed to easily add new languages (including future Dovah support via web API)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd voice-translator
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Docker Installation

### Using Docker (CPU)

1. Build the Docker image:
```bash
docker build -t voice-translator .
```

2. Create input and output directories:
```bash
mkdir -p input output
```

3. Run the container:
```bash
# Translate an audio file
docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output voice-translator \
  python main.py --input /app/input/your_audio.wav --source pt-BR --target en --output /app/output/translated.wav
```

### Using Docker Compose

1. Create input and output directories:
```bash
mkdir -p input output cache
```

2. Edit `docker-compose.yml` to set your desired command, then run:
```bash
# Build and run
docker-compose build
docker-compose run --rm voice-translator python main.py --input /app/input/audio.wav --source pt-BR --target en --output /app/output/translated.wav
```

### Using Docker with GPU Support

**Important**: Before using GPU support, you need to install the NVIDIA Container Toolkit. See [DOCKER_GPU_SETUP.md](DOCKER_GPU_SETUP.md) for detailed installation instructions.

For GPU acceleration, use the GPU-enabled Dockerfile:

1. Build the GPU image:
```bash
docker build -f Dockerfile.gpu -t voice-translator:gpu .
```

2. Run with GPU support (requires NVIDIA Docker runtime):
```bash
docker run --rm --gpus all \
  -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output \
  voice-translator:gpu \
  python main.py --input /app/input/audio.wav --source pt-BR --target en --output /app/output/translated.wav --device cuda
```

**Note**: Microphone input is not available in Docker containers. Use audio files instead.

### Helper Scripts

For easier usage, helper scripts are provided:

**Linux/macOS:**
```bash
# Make scripts executable
chmod +x docker-run.sh docker-run-gpu.sh

# Run with CPU
./docker-run.sh audio.wav pt-BR en

# Run with GPU
./docker-run-gpu.sh audio.wav pt-BR en
```

**Windows (PowerShell):**
```powershell
# Run with CPU
docker run --rm -v ${PWD}/input:/app/input -v ${PWD}/output:/app/output voice-translator python main.py --input /app/input/audio.wav --source pt-BR --target en --output /app/output/translated.wav
```

## Usage

### Web Interface (Recommended for Docker)

**Start the web server:**

```bash
# Native
python runWeb.py

# Docker (much easier!)
docker run --rm -p 5000:5000 voice-translator:gpu python runWeb.py
```

Then open your browser and navigate to: **http://localhost:5000**

The web interface provides:
- **Language Selection**: Choose source and target languages
- **Recording**: Click "Start Recording" to begin, "Stop Recording" to finish
- **Translation**: Automatic transcription and translation after recording
- **Playback**: Listen to the translated audio directly in the browser

**Advantages of Web Interface:**
- ✅ No X11 configuration needed
- ✅ Works perfectly in Docker
- ✅ Accessible from any device on your network
- ✅ Modern, responsive design
- ✅ Works on Windows, Linux, macOS

### Desktop GUI (Alternative)

**Native (Recommended for best performance):**

Launch the desktop GUI application:

```bash
python runGui.py
```

**Docker:**

For running desktop GUI in Docker, see [DOCKER_GUI_SETUP.md](DOCKER_GUI_SETUP.md) for detailed instructions (requires X11 setup).

### Command Line Usage

Translate from an audio file:
```bash
python main.py --input path/to/audio.wav --source pt-BR --target en --output translated.wav
```

Record from microphone and translate:
```bash
python main.py --source pt-BR --target en --record-duration 5.0
```

Record until silence is detected:
```bash
python main.py --source en --target pt-BR --record-until-silence
```

### Command Line Arguments

- `--source`: Source language code (`pt-BR` or `en`)
- `--target`: Target language code (`pt-BR` or `en`)
- `--input`: Path to input audio file (optional, if not provided will use microphone)
- `--output`: Path to save translated audio file (default: `output_translated.wav`)
- `--device`: Device to run models on (`cuda` or `cpu`, default: auto-detect)
- `--record-duration`: Recording duration in seconds when using microphone (default: 5.0)
- `--record-until-silence`: Record from microphone until silence is detected

### Example

```bash
# Translate Portuguese audio file to English
python main.py --input my_audio.wav --source pt-BR --target en --output english_output.wav

# Record English speech and translate to Portuguese
python main.py --source en --target pt-BR --record-duration 10.0
```

## Project Structure

```
voice-translator/
├── models/              # AI models (ASR, Translation, TTS)
│   ├── asrModel.py      # Speech-to-Text model
│   ├── translationModel.py  # Text translation model
│   ├── ttsModel.py      # Text-to-Speech model
│   ├── voiceTranslator.py   # Main orchestrator
│   └── utils/
│       └── languageConfig.py  # Language configuration
├── interface/           # User interface modules
│   ├── audioInput.py    # Audio input handling
│   ├── audioRecorder.py # Audio recording for GUI
│   ├── audioPlayer.py   # Audio playback for GUI
│   ├── gui.py           # Graphical user interface
│   └── utils/
├── api/                 # Web API and server
│   ├── webServer.py     # Flask web server
│   ├── templates/       # HTML templates
│   │   └── index.html   # Web interface
│   └── utils/
├── prompts/             # Translation prompts
│   └── utils/
├── utils/               # General utilities
├── main.py              # Main entry point (CLI)
├── runWeb.py            # Web server entry point
├── runGui.py            # Desktop GUI application entry point
├── exampleUsage.py      # Example usage script
├── requirements.txt     # Python dependencies
├── Dockerfile           # Docker image for CPU
├── Dockerfile.gpu       # Docker image for GPU
├── docker-compose.yml   # Docker Compose configuration
├── DOCKER_GPU_SETUP.md  # NVIDIA Docker runtime setup guide
├── DOCKER_GUI_SETUP.md  # GUI setup guide for Docker
├── check-gpu-docker.sh  # Script to verify GPU Docker setup (Linux)
├── check-gpu-docker.ps1 # Script to verify GPU Docker setup (Windows/WSL2)
├── run-gui-docker.sh    # Script to run GUI in Docker (Linux/WSL2)
└── run-gui-docker.ps1   # Script to run GUI in Docker (PowerShell)
```

## Supported Languages

Currently supported:
- **Portuguese (Brazil)** (`pt-BR`)
- **English** (`en`)

Future support:
- **Dovah** (`dovah`) - Will use web API integration

## Requirements

- Python 3.8+
- PyTorch
- Transformers (Hugging Face)
- Audio processing libraries (librosa, soundfile, pyaudio)

## Notes

- First run will download models from Hugging Face (may take some time)
- GPU acceleration is recommended for faster processing
- Audio files should be in common formats (WAV, MP3, FLAC, etc.)

## License

See LICENSE file for details.
