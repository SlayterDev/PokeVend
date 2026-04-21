#!/bin/bash
set -e

echo "=== pokevend setup ==="

# Require Python 3.9+
python3 -c "import sys; assert sys.version_info >= (3, 9), 'Python 3.9+ required'" 2>/dev/null || {
    echo "ERROR: Python 3.9 or newer is required"
    exit 1
}

# Virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Installing dependencies..."
. venv/bin/activate
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet

# Ensure runtime directories exist
mkdir -p data assets/packs/cache assets/packs/local assets/ui assets/fonts

# Seed empty vend log
touch data/vend_log.jsonl

# Raspberry Pi specific guidance
if uname -m | grep -qE "aarch64|armv7l"; then
    echo ""
    echo "=== Raspberry Pi detected ==="
    echo "HyperPixel 4.0 i2c setup:"
    echo "  The HyperPixel blocks the standard i2c bus. Add to /boot/config.txt:"
    echo "    dtoverlay=i2c-gpio,bus=10,i2c_gpio_sda=<SDA_PIN>,i2c_gpio_scl=<SCL_PIN>"
    echo "  Reboot, then verify: i2cdetect -y 10"
    echo "  PCA9685 should appear at address 0x40"
    echo ""
fi

echo "Setup complete."
echo "Run:  ./run.sh --mock        (UI test without hardware)"
echo "Run:  ./run.sh               (production)"
