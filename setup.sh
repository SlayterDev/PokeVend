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
    echo "  See https://learn.pimoroni.com/article/getting-started-with-hyperpixel-4#using-the-alternate-i2c-interface-for-advanced-users"
    echo "  When you run i2cdetect, you should see the PCA9685 at address 0x40. If not, check your connections and ensure the HyperPixel is configured to use the alternate i2c interface."
    echo "  Enter the number of the i2c bus that shows the PCA9685 (e.g. 10) in config/config.toml → [i2c] bus = XX"
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
    # Allow the user's systemd instance to persist at boot (needed for Restart=on-failure)
    loginctl enable-linger "$(whoami)"

    # XDG autostart triggers the service when the desktop session loads.
    # This is more reliable than graphical-session.target on Raspberry Pi OS.
    AUTOSTART_DIR="${HOME}/.config/autostart"
    mkdir -p "${AUTOSTART_DIR}"
    cp "${INSTALL_DIR}/pokevend.desktop" "${AUTOSTART_DIR}/pokevend.desktop"

    echo "Service installed. It will start automatically when the desktop session loads."
    echo "Start now with: systemctl --user start pokevend"
    echo ""
fi

echo "Setup complete."
echo "Run:  ./run.sh --mock        (UI test without hardware)"
echo "Run:  ./run.sh               (production)"
