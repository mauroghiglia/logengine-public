#!/usr/bin/env python3
import os
import signal
import sys
import subprocess

log_dir = os.path.expanduser("~/logs")
os.makedirs(log_dir, exist_ok=True)  # Ensure log directory exists
log_control_file = os.path.join(log_dir, "logging_active.flag")
log_script = "/usr/local/bin/log-generator.py"
pid_file = os.path.join(log_dir, "logging_process.pid")

def start_logging():
    if os.path.exists(pid_file):
        print("Logging process is already running.")
        return

    # Create the control file to allow logging
    open(log_control_file, "w").close()

    # Start the logging process in the background
    process = subprocess.Popen(["nohup", "python3", log_script, "&"],
                               stdout=open(os.path.join(log_dir, "logging_output.log"), "a"),
                               stderr=subprocess.STDOUT,
                               preexec_fn=os.setpgrp)

    # Save the process ID
    with open(pid_file, "w") as f:
        f.write(str(process.pid))

    print(f"Logging started with PID {process.pid}")

def stop_logging():
    if not os.path.exists(pid_file):
        print("No logging process found.")
        return

    # Read the process ID
    with open(pid_file, "r") as f:
        pid = int(f.read().strip())

    # Send SIGTERM to stop the process
    try:
        os.kill(pid, signal.SIGTERM)
        print(f"Logging process {pid} stopped.")
    except ProcessLookupError:
        print("Process not found, cleaning up.")

    # Remove control file and PID file
    os.remove(log_control_file)
    os.remove(pid_file)

def status_logging():
    if os.path.exists(pid_file):
        with open(pid_file, "r") as f:
            pid = f.read().strip()
        print(f"Logging is **running** with PID {pid}.")
    else:
        print("Logging is **stopped**.")

if len(sys.argv) != 2 or sys.argv[1] not in ["start", "stop", "status"]:
    print("Usage: logging_manager.py [start|stop|status]")
    sys.exit(1)

if sys.argv[1] == "start":
    start_logging()
elif sys.argv[1] == "stop":
    stop_logging()
elif sys.argv[1] == "status":
    status_logging()
