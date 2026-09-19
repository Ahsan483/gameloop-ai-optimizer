import psutil
import time
import csv
import os
import subprocess
from datetime import datetime

PID = 22772

DATA_DIR = "data"
CSV_FILE = os.path.join(DATA_DIR, "telemetry.csv")

os.makedirs(DATA_DIR, exist_ok=True)

try:
    process = psutil.Process(PID)
except psutil.NoSuchProcess:
    print(f"Process {PID} does not exist.")
    exit()


def get_gpu_stats():
    try:
        result = subprocess.check_output(
            [
                "nvidia-smi",
                "--query-gpu=temperature.gpu,utilization.gpu,"
                "memory.used,memory.total,power.draw",
                "--format=csv,noheader,nounits"
            ],
            text=True
        ).strip()

        temperature, gpu_util, memory_used, memory_total, power = (
            result.split(",")
        )

        return (
            float(temperature),
            float(gpu_util),
            float(memory_used),
            float(memory_total),
            float(power)
        )

    except Exception:
        return None, None, None, None, None


# Prime CPU measurements
process.cpu_percent(None)
psutil.cpu_percent(None)

file_exists = os.path.exists(CSV_FILE)

with open(CSV_FILE, "a", newline="") as file:

    writer = csv.writer(file)

    if not file_exists:
        writer.writerow([
            "timestamp",
            "process_cpu_percent",
            "process_ram_mb",
            "process_threads",
            "system_cpu_percent",
            "system_ram_percent",
            "system_ram_used_mb",
            "gpu_temperature_c",
            "gpu_util_percent",
            "gpu_memory_used_mb",
            "gpu_memory_total_mb",
            "gpu_power_w"
        ])

    print("=" * 110)
    print("GAMELOOP AI OPTIMIZER - GPU + CPU TELEMETRY")
    print("=" * 110)
    print(f"Monitoring PID: {PID}")
    print(f"Saving to: {CSV_FILE}")
    print("Press CTRL+C to stop.")
    print()

    time.sleep(1)

    while True:

        try:

            # GameLoop
            process_cpu = process.cpu_percent(None)

            memory = process.memory_info()
            process_ram = memory.rss / (1024 * 1024)

            threads = process.num_threads()

            # System
            system_cpu = psutil.cpu_percent(None)

            system_memory = psutil.virtual_memory()

            system_ram_percent = system_memory.percent
            system_ram_used = system_memory.used / (1024 * 1024)

            # GPU
            (
                gpu_temp,
                gpu_util,
                gpu_memory_used,
                gpu_memory_total,
                gpu_power
            ) = get_gpu_stats()

            timestamp = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            # Save
            writer.writerow([
                timestamp,
                round(process_cpu, 2),
                round(process_ram, 2),
                threads,
                round(system_cpu, 2),
                round(system_ram_percent, 2),
                round(system_ram_used, 2),
                gpu_temp,
                gpu_util,
                gpu_memory_used,
                gpu_memory_total,
                gpu_power
            ])

            file.flush()

            # Display
            print(
                f"{timestamp} | "
                f"GameLoop CPU: {process_cpu:6.1f}% | "
                f"RAM: {process_ram:7.1f} MB | "
                f"System RAM: {system_ram_percent:5.1f}% | "
                f"GPU: {gpu_util:3.0f}% | "
                f"VRAM: {gpu_memory_used:5.0f} MB | "
                f"Temp: {gpu_temp:4.0f}C | "
                f"Power: {gpu_power:5.1f}W"
            )

            time.sleep(1)

        except psutil.NoSuchProcess:
            print("GameLoop process ended.")
            break

        except psutil.AccessDenied:
            print("Access denied.")
            break

        except KeyboardInterrupt:
            print("\nTelemetry collection stopped.")
            break