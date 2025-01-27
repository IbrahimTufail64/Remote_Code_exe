#!/bin/bash

# Update package lists
./Scripts/activate
python app.py

# Confirm installations
echo "Installation completed."
echo "Installed packages:"
echo "- Python3"
echo "- avrdude"
echo "- Flask for Python3"
