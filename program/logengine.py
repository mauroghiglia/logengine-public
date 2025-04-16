#!/usr/bin/env python3

import time
import random
import os
import signal
import sys
import yaml
import json
import threading

# === Version ===
__version__ = "2.0.1"
__author__ = "Mauro Ghiglia"

# === Load configuration from YAML ===
with open("/usr/local/bin/logengine.config.yaml", "r") as f:
    config = yaml.safe_load(f)

# === New Configuration Parameters ===
stop_day_of_week = config.get("stop_day_of_week", 5)  # 5 is Saturday (0 is Sunday)
stop_hour = config.get("stop_hour", 0)  # 0 is midnight (12 AM)

log_dir = config["log_dir"]
logging_output_file = config["logging_output_file"]
log_control_file = config["log_control_file"]

log_types = config.get("log_types", {"prices": True, "trades": True, "series": True})
interval_range = config.get("interval_range", [1, 3])
raw_levels = config.get("log_levels", {"INFO": 50, "WARNING": 20, "ERROR": 10, "DEBUG": 20})
categories = config.get("categories", {})
message_sets = config.get("messages", {})

# Handle both old and new formats for log_levels
if isinstance(raw_levels, dict):
    log_levels = list(raw_levels.keys())
    level_weights = list(raw_levels.values())
else:
    log_levels = raw_levels
    level_weights = [1] * len(log_levels)

# Ensure log directories exist
os.makedirs(log_dir, exist_ok=True)
os.makedirs(os.path.dirname(logging_output_file), exist_ok=True)

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

def generate_message(template):
    if "*" not in template:
        return template
    parts = template.split("*")
    rand_id = f"ID{random.randint(1000,9999)}"
    rand_value = round(random.uniform(10.0, 100.0), 2)
    return "".join(
        parts[i] + (rand_id if i % 2 == 0 else str(rand_value))
        for i in range(len(parts))
    )

def log_message(log_file_name, category, context, messages):
    log_file_path = os.path.join(log_dir, log_file_name)
    thread_id = f"k{random.randint(100000, 999999)}"
    process_id = os.getpid()
    level = random.choices(log_levels, weights=level_weights, k=1)[0]
    message_template = random.choice(messages)
    message = generate_message(message_template)
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')

    log_entry = {
        "timestamp": timestamp,
        "thread": thread_id,
        "pid": process_id,
        "level": level,
        "category": category,
        "context": context,
        "message": message
    }

    with open(log_file_path, "a") as log_file:
        log_file.write(json.dumps(log_entry) + "\n")

    log_to_file(f"[{level}] {category} {message}")

# === Schedule Log Cleanup ===
def schedule_log_cleanup():
    while True:
        current_time = time.localtime()
        if current_time.tm_wday == stop_day_of_week and current_time.tm_hour == stop_hour and current_time.tm_min == 0:
            for log_type in ["series", "trades", "prices"]:
                log_file_path = os.path.join(log_dir, f"{log_type}.log")
                open(log_file_path, "w").close()
                log_to_file(f"Log file {log_file_path} cleared.")
            time.sleep(60)
        time.sleep(30)

cleanup_thread = threading.Thread(target=schedule_log_cleanup, daemon=True)
cleanup_thread.start()

# === Start Logging ===
def start_logging():
    try:
        pid = os.getpid()
        with open(log_control_file, "w") as flag_file:
            flag_file.write(str(pid))

        print(f"logengine v{__version__} by {__author__}")
        print(f"✅ Logging started with PID {pid}")
        print(f"📂 Generating logs in {log_dir}")
        log_to_file(f"logengine v{__version__} by {__author__}")
        log_to_file(f"Logging started with PID {pid}.")

        for log_type in log_types:
            if log_types[log_type]:
                open(os.path.join(log_dir, f"{log_type}.log"), "w").close()

        start_time = time.time()

        while os.path.exists(log_control_file):
            for log_type in ["series", "trades", "prices"]:
                if log_types.get(log_type):
                    log_message(
                        f"{log_type}.log",
                        categories.get(log_type, f"CTE.{log_type.upper()}.CCP.TO.CCG.Q"),
                        "Camel (camel-1) thread #1",
                        message_sets.get(log_type, ["No message defined"])
                    )
            time.sleep(random.randint(*interval_range))

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

def get_status():
    if os.path.exists(log_control_file):
        try:
            with open(log_control_file, "r") as flag_file:
                pid = flag_file.read().strip()
            status = f"✅ Logger is running with PID {pid}."
        except Exception:
            status = "⚠️ Logger is running, but PID could not be determined."
    else:
        status = "🛑 Logger is not running."

    log_sizes = []
    for log_type in ["series", "trades", "prices"]:
        log_file_path = os.path.join(log_dir, f"{log_type}.log")
        if os.path.exists(log_file_path):
            size = os.path.getsize(log_file_path)
            log_sizes.append(f"{log_type}.log: {size} bytes")
        else:
            log_sizes.append(f"{log_type}.log: File not found")

    return status + "\n" + "\n".join(log_sizes)

# === CLI Entry Point ===
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: logengine.py [start|stop|status]")
        sys.exit(1)

    command = sys.argv[1].lower()
    if command == "start":
        start_logging()
    elif command == "stop":
        stop_logging()
    elif command == "status":
        print(get_status())
    else:
        print("Invalid command. Use 'start', 'stop', or 'status'.")
        sys.exit(1)