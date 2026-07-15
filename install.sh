#!/bin/bash

# Force script to exit immediately if any single command fails
set -e

echo "Thanks for using the TRWNS One-Click Automated Installer (TM)!"

# 1. AUTOMATIC SYSTEM UPDATE & RADIO DRIVER INJECTION
echo "Updating system repositories and downloading drivers..."
# DEBIAN_FRONTEND=noninteractive skips all configuration menus
# -y forces a 'yes' response to every single driver installation prompt
sudo DEBIAN_FRONTEND=noninteractive apt-get update
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y python3 python3-pip rtl-sdr librtlsdr-dev

# 2. BLACKLIST CONFLICTING KERNEL DRIVERS NATIVELY
echo "Configuring Nooelec hardware rules and fixing Linux tuner issues..."
# Default Linux Mint treats SDRs as DVB-TV tuners. This forces it to act as an audio scanner.
sudo bash -c 'cat << EOF > /etc/modprobe.d/blacklist-rtl.conf
blacklist dvb_usb_rtl8xxu
blacklist rtl2832
blacklist rtl2830
EOF'

# Apply hardware access permissions so your normal user account can use the USB stick
sudo bash -c 'cat << EOF > /etc/udev/rules.d/20-rtlsdr.rules
SUBSYSTEM=="usb", ATTRS{idVendor}=="0bda", ATTRS{idProduct}=="2832", MODE="0666", GROUP="plugdev"
SUBSYSTEM=="usb", ATTRS{idVendor}=="0bda", ATTRS{idProduct}=="2838", MODE="0666", GROUP="plugdev"
EOF'

# Reload hardware rules instantly
sudo udevadm control --reload-rules
sudo udevadm trigger

# 3. FORCE PIP DEPENDENCY DEPLOYMENT
echo "Installing necessary Python packages..."
# --break-system-packages overrides the Linux Mint PEP 668 managed environment block
# --ignore-installed forces a complete fresh download of the stack
python3 -m pip install --break-system-packages --ignore-installed apprise numpy

echo "------------------------------------------------------------"
echo "✅ COMPLETED: TRWNS is fully installed on your machine!"
echo "Make sure your Discord Webhook is pasted in trwns.py"
echo "Simply type: python3 trwns.py"
echo "------------------------------------------------------------"
