#!/usr/bin/env python3

import time
import random
import os
import signal
import sys

# === Configuration ===
log_dir = "/var/log/log-generator/ccp_logs"
logging_output_file = "/var/log/log-generator/logging_output.log"
log_control_file = "/var/log/log-generator/logging_active.flag"

# Ensure log directories exist
os.makedirs(log_dir, exist_ok=True)
os.makedirs(os.path.dirname(logging_output_file), exist_ok=True)

# Log levels and message pools
log_levels = ["INFO", "WARNING", "ERROR", "DEBUG"]
series_messages = [
    "End Process Message",
    "Processing series data batch",
    "Successfully processed message"
]
trades_messages = [
    "Start Process Message",
    "Unknown keyword $id - you should define your own Meta Schema."
]
prices_messages = [
    "Exchange[ExchangePattern: InOnly, BodyType: String, Body: {\"msg_code\":\"690\",\"msg_sequence\":1}"
]

stopped_by_signal = False

# === Signal Handler ===
def handle_exit(signum, frame):
    global stopped_by_signal
    stopped_by_signal = True
    log_to_file("Logging stopped manually (SIGTERM received).")
    print("🛑 Logging stopped manually (SIGTERM received).")
    sys.exit(0)

signal.signal(signal.SIGTERM, handle_exit)

# === Logging Functions ===
def log_to_file(message):
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    entry = f"{timestamp} - {message}"
    with open(logging_output_file, "a") as f:
        f.write(entry + "\n")

def log_message(log_file_name, category, context, messages):
    log_file_path = os.path.join(log_dir, log_file_name)
    thread_id = f"k{random.randint(100000, 999999)}"
    process_id = os.getpid()
    level = random.choice(log_levels)
    message = random.choice(messages)
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')

    entry = f"{timestamp},{random.randint(100,999)} {thread_id} <unknown>[{process_id}] {level:<5} [{category}] ({context}) {message}"

    with open(log_file_path, "a") as log_file:
        log_file.write(entry + "\n")
    
    log_to_file(entry)

# === Start Logging ===
def start_logging():
    try:
        pid = os.getpid()

        # Save PID in flag file
        with open(log_control_file, "w") as flag_file:
            flag_file.write(str(pid))

        # CLI output
        print(f"✅ Logging started with PID {pid}")
        print(f"📂 Generating logs in {log_dir}")

        # Log to file
        log_to_file(f"Logging started with PID {pid}.")

        while os.path.exists(log_control_file):
            log_message("series.log", "CTE.SER.CCP.TO.CCG.Q", "Camel (camel-1) thread #1", series_messages)
            log_message("trades.log", "CTE.TRA.CCP.TO.CCG.Q", "Camel (camel-1) thread #1", trades_messages)
            log_message("prices.log", "CTE.PRI.CCP.TO.CCG.Q", "Camel (camel-1) thread #1", prices_messages)
            time.sleep(random.randint(1, 3))

    except Exception as e:
        print(f"❌ Logging process stopped with ERROR: {e}")
        log_to_file(f"Logging process stopped with ERROR: {e}")
        sys.exit(1)

    if not stopped_by_signal:
        print("⏹️ Logging process stopped normally.")
        log_to_file("Logging process stopped normally.")

# === Stop Logging ===
def stop_logging():
    if os.path.exists(log_control_file):
        try:
            with open(log_control_file, "r") as flag_file:
                pid = flag_file.read().strip()
        except Exception:
            pid = "unknown"

        os.remove(log_control_file)
        print(f"🛑 Logger at PID {pid} has been stopped.")
        log_to_file(f"Logging stopped by user (PID {pid}).")
    else:
        print("⚠️ Logging is not currently running.")
        log_to_file("Logging stop requested, but no active flag file found.")

# === CLI Entry Point ===
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: logengine.py [start|stop]")
        sys.exit(1)

    command = sys.argv[1].lower()
    if command == "start":
        start_logging()
    elif command == "stop":
        stop_logging()
    else:
        print("Invalid command. Use 'start' or 'stop'.")
