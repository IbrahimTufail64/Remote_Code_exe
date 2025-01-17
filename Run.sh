#!/bin/bash

# Update package lists
echo "Updating package lists..."
sudo apt update

# Install Python3 and avrdude
echo "Installing Python3 and avrdude..."
sudo apt install -y python3 avrdude

# Install Python3 Flask and subprocess (subprocess is part of Python standard library)
echo "Installing Flask for Python3..."
sudo apt install -y python3-flask

# Confirm installations
echo "Installation completed."
echo "Installed packages:"
echo "- Python3"
echo "- avrdude"
echo "- Flask for Python3"
