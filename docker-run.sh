#!/bin/bash
# Helper script to run voice translator in Docker

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Voice Translator - Docker Helper${NC}"
echo ""

# Check if input file is provided
if [ -z "$1" ]; then
    echo "Usage: ./docker-run.sh <input_audio_file> [source_lang] [target_lang] [output_file]"
    echo ""
    echo "Examples:"
    echo "  ./docker-run.sh audio.wav pt-BR en"
    echo "  ./docker-run.sh audio.wav pt-BR en translated.wav"
    exit 1
fi

INPUT_FILE="$1"
SOURCE_LANG="${2:-pt-BR}"
TARGET_LANG="${3:-en}"
OUTPUT_FILE="${4:-translated.wav}"

# Check if input file exists
if [ ! -f "input/$INPUT_FILE" ]; then
    echo "Error: Input file 'input/$INPUT_FILE' not found"
    echo "Please place your audio file in the 'input' directory"
    exit 1
fi

echo -e "${GREEN}Translating: $INPUT_FILE${NC}"
echo "Source: $SOURCE_LANG -> Target: $TARGET_LANG"
echo ""

# Run Docker container
docker run --rm \
    -v "$(pwd)/input:/app/input" \
    -v "$(pwd)/output:/app/output" \
    -v "$(pwd)/cache:/root/.cache" \
    voice-translator \
    python main.py \
        --input "/app/input/$INPUT_FILE" \
        --source "$SOURCE_LANG" \
        --target "$TARGET_LANG" \
        --output "/app/output/$OUTPUT_FILE"

echo ""
echo -e "${GREEN}Translation complete!${NC}"
echo "Output saved to: output/$OUTPUT_FILE"

