import argparse
import csv
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

import psutil


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "data" / "telemetry.csv"
PROCESS_NAMES = {"aow_exe.exe", "androidemulatoren.exe", "androidemulator.exe", "qmemulatorservice.exe"}


def gpu_sample():
    query = "utilization.gpu,temperature.gpu,memory.used,power.draw,clocks.gr"
    try:
        result = subprocess.run(
            ["nvidia-smi", f"--query-gpu={query}", "--format=csv,noheader,nounits"],
            capture_output=True,
            text=True,
            timeout=2,
            check=True,
        )
        values = [value.strip() for value in result.stdout.strip().split(",")]
        if len(values) != 5:
            return [None] * 5
        return [float(value) if value not in {"", "N/A"} else None for value in values]
    except (FileNotFoundError, OSError, subprocess.SubprocessError, ValueError):
        return [None] * 5


def process_sample():
    candidates = []
    for process in psutil.process_iter(["pid", "name", "ppid", "memory_info", "num_threads"]):
        try:
            name = (process.info["name"] or "").lower()
            if name not in PROCESS_NAMES:
                continue
            process.cpu_percent(None)
            candidates.append(process)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    time.sleep(0.15)
    active = []
    for process in candidates:
        try:
            active.append(
                {
                    "pid": process.pid,
                    "cpu": process.cpu_percent(None) / psutil.cpu_count(logical=True),
                    "ram_mb": process.memory_info().rss / (1024 * 1024),
                    "threads": process.num_threads(),
                }
            )
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    if not active:
        return {"pid": None, "cpu": 0.0, "ram_mb": 0.0, "threads": 0}
    return max(active, key=lambda item: (item["cpu"], item["ram_mb"]))


def collect_row():
    memory = psutil.virtual_memory()
    selected = process_sample()
    gpu = gpu_sample()
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "gameloop_pid": selected["pid"],
        "gameloop_cpu_pct": round(selected["cpu"], 2),
        "gameloop_ram_mb": round(selected["ram_mb"], 2),
        "gameloop_threads": selected["threads"],
        "system_cpu_pct": round(psutil.cpu_percent(interval=0.1), 2),
        "system_ram_pct": round(memory.percent, 2),
        "system_ram_used_mb": round(memory.used / (1024 * 1024), 2),
        "gpu_utilization_pct": gpu[0],
        "gpu_temperature_c": gpu[1],
        "gpu_vram_used_mb": gpu[2],
        "gpu_power_w": gpu[3],
        "gpu_clock_mhz": gpu[4],
    }


def main():
    parser = argparse.ArgumentParser(description="Collect read-only GameLoop performance telemetry.")
    parser.add_argument("--duration", type=float, default=60, help="Collection duration in seconds.")
    parser.add_argument("--interval", type=float, default=1, help="Seconds between samples.")
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fields = list(collect_row().keys())
    write_header = not args.output.exists() or args.output.stat().st_size == 0
    deadline = time.monotonic() + args.duration
    with args.output.open("a", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        if write_header:
            writer.writeheader()
        while time.monotonic() < deadline:
            writer.writerow(collect_row())
            stream.flush()
            time.sleep(max(0, args.interval))


if __name__ == "__main__":
    main()