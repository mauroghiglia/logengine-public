#!/bin/bash

# Set executable permissions on install.sh if not already set
chmod +x "$0"

# Your installation commands here
echo "Running installation..."

# Install scripts to /usr/local/bin
sudo cp commands/logengine-start.sh /usr/local/bin/logengine-start
sudo cp commands/logengine-stop.sh /usr/local/bin/logengine-stop
sudo cp commands/logengine-status.sh /usr/local/bin/logengine-status

# Make them executable
sudo chmod +x /usr/local/bin/logengine-start
sudo chmod +x /usr/local/bin/logengine-stop
sudo chmod +x /usr/local/bin/logengine-status

# Make program files executable
sudo chmod +x program/logengine.py
sudo chmod +x program/logengine.config.yaml

# Create a directory for the logengine log files
sudo mkdir -p /var/log/logengine-public
sudo chmod +x /var/log/logengine-public
sudo chown $ubuntu:$ubuntu /var/log/logengine-public

sudo mkdir -p /var/log/logengine-public-logs
sudo chmod +x /var/log/logengine-public-logs
sudo chown $ubuntu:$ubuntu /var/log/logengine-public-logs

echo "lg-start, lg-stop, and og-status have been installed to /usr/local/bin."
echo "A folder named /var/log/logengine-public has been created for log files."
echo "You can view the logs in /var/log/logengine-public-logs."