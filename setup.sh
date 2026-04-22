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

# Seed data files if not present
touch data/vend_log.jsonl

if [ ! -f data/packs.json ]; then
    cp data/packs.json.example data/packs.json
fi

if [ ! -f data/inventory.json ]; then
    cp data/inventory.json.example data/inventory.json
fi

# Raspberry Pi specific setup
if uname -m | grep -qE "aarch64|armv7l"; then
    echo ""
    echo "=== Raspberry Pi detected ==="
    echo "HyperPixel 4.0 i2c setup:"
    echo "  The HyperPixel blocks the standard i2c bus. Add to /boot/config.txt:"
    echo "    dtoverlay=i2c-gpio,bus=10,i2c_gpio_sda=<SDA_PIN>,i2c_gpio_scl=<SCL_PIN>"
    echo "  Reboot, then verify: i2cdetect -y 10"
    echo "  PCA9685 should appear at address 0x40"
    echo ""

    # Install systemd user service
    echo "Installing systemd user service..."
    INSTALL_DIR="$(cd "$(dirname "$0")" && pwd)"
    SERVICE_DIR="${HOME}/.config/systemd/user"
    mkdir -p "${SERVICE_DIR}"
    sed \
        -e "s|__WORKING_DIR__|${INSTALL_DIR}|g" \
        "${INSTALL_DIR}/pokevend.service" \
        > "${SERVICE_DIR}/pokevend.service"
    systemctl --user daemon-reload
    systemctl --user enable pokevend.service
    # Allow the user service to start at boot without an interactive login
    loginctl enable-linger "$(whoami)"
    echo "Service enabled. It will start automatically when the desktop session starts."
    echo "Start now with: systemctl --user start pokevend"
    echo ""
fi

echo "Setup complete."
echo "Run:  ./run.sh --mock        (UI test without hardware)"
echo "Run:  ./run.sh               (production)"
