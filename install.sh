#!/bin/bash

# Install scripts to /usr/local/bin
sudo cp commands/lg-start /usr/local/bin/lg-start
sudo cp commands/lg-stop /usr/local/bin/lg-stop
sudo cp commands/lg-status /usr/local/bin/lg-status

# Make them executable
sudo chmod +x /usr/local/bin/lg-start
sudo chmod +x /usr/local/bin/lg-stop
sudo chmod +x /usr/local/bin/lg-status

# Make program files executable
sudo chmod +x program/logengine.py
sudo chmod +x program/logengine.config.yaml

echo "lg-start, lg-stop, and og-status have been installed to /usr/local/bin."
echo "You can now use them from anywhere in the terminal."