# PokéVend

[![BuyMeACoffee](https://raw.githubusercontent.com/pachadotdev/buymeacoffee-badges/main/bmc-donate-yellow.svg)](https://buymeacoffee.com/slayterdev)

This is the repo for the controller code for the 3D Printed [PokéVend](https://www.printables.com/model/1699016-pokevend-pokemon-booster-pack-vending-machine) Vending Machine. 3D printed parts can be found on [Printables](https://www.printables.com/model/1699016-pokevend-pokemon-booster-pack-vending-machine). Follow the instructions below to setup the controller code on a Raspberry Pi.

### Bill of Materials

- Raspberry Pi 4 Model B
- Hyperpixel 4.0
- PCA9685 Servo Driver
- MG90S Servo Motor x4
- QW/ST to female header breakout ([example](https://www.amazon.com/dp/B08HQ1VSVL?ref=ppx_yo2ov_dt_b_fed_asin_title))
- 5V 3A power supply ([example](https://www.amazon.com/dp/B078RXZM4C?ref=ppx_yo2ov_dt_b_fed_asin_title))
    - *Note:* You can probably get away with splicing the red/black wires from an old USB cable into the PCA9685's power terminals and then powering it off the Pi's USB. But this is likely not reccomended.
- Right angle USB-C connector ([example](https://www.amazon.com/dp/B0CNGFZ1JD?ref=ppx_yo2ov_dt_b_fed_asin_title))
- Some wire (to connect psu screw terminal to PCA9685)
- 6mmx2mm magnets x14
- M3x10 screws x6
- M3 nuts x6

### Raspberry Pi Setup

#### 1. **Install Raspbian OS**:

Use Raspberry Pi Imager or similar to install the latest Raspbian OS with desktop environment on your SD card. Be sure to configure SSH and WiFi before booting.

#### 2. **Configure Raspberry Pi**:

- Enable the Hyperpixel display by adding this line to the bottom of `/boot/firmware/config.txt`:
```bash
dtoverlay=vc4-kms-dpi-hyperpixel4
```
- You will need to rotate the display 180º. I had issues doing this via the config file and was able to do it on the desktop Click `Raspberry Pi Icon > Preferences > Screens`. Click DPI-1 and set its orrientation to inverted. Its a bit difficult on the hyperpixel screen but doable.

#### 3. **I2C Passthrough**

Follow the instructions [here](https://learn.pimoroni.com/article/getting-started-with-hyperpixel-4#using-the-alternate-i2c-interface-for-advanced-users) to find the I2C bus number your device is using. Ignore the `sudo ln ...` command and instead note this number.

#### 4. **Software Setup**

**NOTE: It is recommended to run the software before attaching the paddles to the servos. This way your servos will be set to the neutral angle before mounting them.**

- Clone this repositiory
```bash
git clone https://github.com/SlayterDev/PokeVend.git
cd PokeVend
```

- Edit the config file to match the I2C bus number you noted above
```toml
[i2c]
# HyperPixel 4.0 blocks the standard i2c bus (1).
# Connect PCA9685 to the HyperPixel breakout i2c header
# `ls /dev/i2c*` to view available buses. Then `i2cdetect -y XX` to find the address of your PCA9685.
# You should see `40` in one of the entries of the output. This indicates the correct i2c bus number.
bus = 22 # <- Replace with the number from your device
```

- Run the setup script. This will setup a virtual environment, install dependencies, and setup the app to run at boot.
```bash
./setup.sh
```

- To start the app immediately run:
```bash
systemctl --user start pokevend
```

### Servo Tweaking

If you find your servos aren't at the correct angle once mounted, or they aren't vending properly, you can tweak the config file to fine tune the servo angles.

```toml
[servo.lane_0] # <- Lanes are numbers 0-3 from left to right
channel = 0
neutral_angle = 130.0 # <- This is the resting angle. Adjust this if the paddle is too far forward or back at rest.
vend_angle = 32.0 # <- This is the angle at which the paddle should be pushed to vend. Adjust this if the paddle goes too far or not far enough.
sweep_ms = 0
vend_hold_ms = 750
return_ms = 300
```

### Inventory Management

There is an included `stock.py` script that can be used to manage the inventory of your PokéVend. You can run it with the following command:
```bash
./stock.py
```

The script will show a menu with the current loaded stock and options to add inventory or manage available packs. When exiting the script it will give you
an option to restart the PokeVend service to apply changes.

### Support

If you run into issues feel free to open an issue here or comment on Printables and I will do my best to help you!


