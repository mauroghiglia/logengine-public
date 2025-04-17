#!/bin/bash

# Install scripts to /usr/local/bin
sudo cp commands/logengine-start.sh /usr/local/bin/logengine-start
sudo cp commands/logengine-stop.sh /usr/local/bin/logengine-stop
sudo cp commands/logengine-status.sh /usr/local/bin/logengine-status

# Make them executable
# sudo chmod +x /usr/local/bin/logengine-start
# sudo chmod +x /usr/local/bin/logengine-stop
# sudo chmod +x /usr/local/bin/logengine-status

# Make program files executable
# sudo chmod +x program/logengine.py
# sudo chmod +x program/logengine.config.yaml

# echo "lg-start, lg-stop, and og-status have been installed to /usr/local/bin."
# echo "You can now use them from anywhere in the terminal."