#!/bin/bash

# Sexy Audio Streamer - Cross-platform launcher for Linux/macOS

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo ""
echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}   Sexy Audio Streamer - Setup${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

# Detect OS
OS="unknown"
case "$(uname -s)" in
    Linux*)     OS="Linux";;
    Darwin*)    OS="macOS";;
    CYGWIN*)    OS="Cygwin";;
    MINGW*)     OS="MinGW";;
    MSYS*)      OS="MSYS";;
    *)          OS="unknown";;
esac

echo -e "${GREEN}[OK]${NC} Detected OS: $OS"

# Check if Windows-based (should use .bat instead)
if [[ "$OS" == "Cygwin" || "$OS" == "MinGW" || "$OS" == "MSYS" ]]; then
    echo -e "${YELLOW}[WARN]${NC} Windows detected. Consider using 'sexy audio.bat' instead."
    echo -e "${YELLOW}[INFO]${NC} Continuing with shell script..."
fi

# macOS specific warning about audio capture
if [[ "$OS" == "macOS" ]]; then
    echo -e "${YELLOW}[WARN]${NC} macOS has limited system audio capture support."
    echo -e "${YELLOW}[INFO]${NC} You may need to install BlackHole or Soundflower for audio loopback."
fi

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
echo -e "${GREEN}[OK]${NC} Working directory: $SCRIPT_DIR"

# Check for Python 3
PYTHON_CMD=""
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    # Check if python is Python 3
    if python --version 2>&1 | grep -q "Python 3"; then
        PYTHON_CMD="python"
    fi
fi

if [[ -z "$PYTHON_CMD" ]]; then
    echo -e "${RED}[ERROR]${NC} Python 3 not found."
    echo "Please install Python 3.8+ from https://python.org"
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2)
echo -e "${GREEN}[OK]${NC} Python $PYTHON_VERSION found ($PYTHON_CMD)"

# Check/Create virtual environment
VENV_DIR="$SCRIPT_DIR/sound"
if [[ ! -f "$VENV_DIR/bin/activate" ]]; then
    echo -e "${YELLOW}[INFO]${NC} Creating virtual environment..."
    $PYTHON_CMD -m venv sound
    if [[ $? -ne 0 ]]; then
        echo -e "${RED}[ERROR]${NC} Failed to create virtual environment."
        exit 1
    fi
    echo -e "${GREEN}[OK]${NC} Virtual environment created"
fi

# Activate virtual environment
echo -e "${YELLOW}[INFO]${NC} Activating virtual environment..."
source "$VENV_DIR/bin/activate"
if [[ $? -ne 0 ]]; then
    echo -e "${RED}[ERROR]${NC} Failed to activate virtual environment."
    exit 1
fi
echo -e "${GREEN}[OK]${NC} Virtual environment activated"

# Check/Install dependencies
echo -e "${YELLOW}[INFO]${NC} Checking dependencies..."
if ! pip show sounddevice &> /dev/null; then
    echo -e "${YELLOW}[INFO]${NC} Installing Python dependencies..."
    pip install -r requirements.txt
    if [[ $? -ne 0 ]]; then
        echo -e "${RED}[ERROR]${NC} Failed to install dependencies."
        exit 1
    fi
fi
echo -e "${GREEN}[OK]${NC} Dependencies installed"

# Check for required files
if [[ ! -f "$SCRIPT_DIR/server.py" ]]; then
    echo -e "${RED}[ERROR]${NC} server.py not found."
    exit 1
fi
if [[ ! -f "$SCRIPT_DIR/client.html" ]]; then
    echo -e "${RED}[ERROR]${NC} client.html not found."
    exit 1
fi
if [[ ! -f "$SCRIPT_DIR/src/config.py" ]]; then
    echo -e "${RED}[ERROR]${NC} src/config.py not found. Project structure incomplete."
    exit 1
fi
echo -e "${GREEN}[OK]${NC} Required files present"

# Display network info
echo ""
echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}   Network Information${NC}"
echo -e "${CYAN}========================================${NC}"

if [[ "$OS" == "macOS" ]]; then
    # macOS
    IP_ADDRS=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}')
elif [[ "$OS" == "Linux" ]]; then
    # Linux
    IP_ADDRS=$(hostname -I 2>/dev/null || ip addr show | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | cut -d'/' -f1)
else
    IP_ADDRS="Unable to detect"
fi

for ip in $IP_ADDRS; do
    echo -e "${GREEN}[IP]${NC} $ip"
done

echo ""
echo -e "${YELLOW}Clients can connect at: http://YOUR_IP:5000${NC}"
echo ""

# Trap Ctrl+C for graceful shutdown
trap 'echo -e "\n${GREEN}[INFO]${NC} Shutting down..."; exit 0' INT TERM

# Start server loop
while true; do
    echo ""
    echo -e "${CYAN}========================================${NC}"
    echo -e "${CYAN}   Starting Audio Server...${NC}"
    echo -e "${CYAN}========================================${NC}"
    echo ""

    python server.py
    EXIT_CODE=$?

    echo ""
    if [[ $EXIT_CODE -eq 0 ]]; then
        echo -e "${GREEN}[INFO]${NC} Server stopped gracefully."
        break
    else
        echo -e "${YELLOW}[WARN]${NC} Server exited with code $EXIT_CODE"
        echo "Restarting in 3 seconds... (Press Ctrl+C to exit)"
        sleep 3
    fi
done

echo ""
echo -e "${GREEN}Goodbye!${NC}"
