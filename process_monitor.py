import psutil
import time
import os

GAMELOOP_PATH = r"C:\Program Files\TxGameAssistant"

KEYWORDS = [
    "androidemulator",
    "aow",
    "qmemulator",
    "androidrenderer",
    "gameloop",
]

def is_gameloop_process(proc):
    try:
        name = proc.info["name"] or ""
        exe = proc.info["exe"] or ""

        name_lower = name.lower()
        exe_lower = exe.lower()

        if any(k in name_lower for k in KEYWORDS):
            return True

        if exe_lower.startswith(GAMELOOP_PATH.lower()):
            return True

    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass

    return False


def get_processes():
    processes = []

    for proc in psutil.process_iter(
        ["pid", "name", "exe", "memory_info", "cpu_percent"]
    ):
        try:
            if is_gameloop_process(proc):
                processes.append(proc)

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return processes


print("=" * 100)
print("GAMELOOP AI OPTIMIZER - PROCESS MONITOR")
print("=" * 100)
print("Start PUBG Mobile and leave it running.")
print("Press CTRL+C to stop.")
print()

# Prime CPU measurements
for proc in get_processes():
    try:
        proc.cpu_percent(None)
    except:
        pass

time.sleep(1)

while True:

    os.system("cls")

    print("=" * 100)
    print("GAMELOOP AI OPTIMIZER - PROCESS MONITOR")
    print("=" * 100)
    print()

    processes = get_processes()

    if not processes:
        print("No GameLoop processes detected.")
    else:

        print(
            f"{'PID':<8}"
            f"{'CPU %':<10}"
            f"{'RAM MB':<12}"
            f"{'NAME':<30}"
        )

        print("-" * 100)

        total_cpu = 0
        total_ram = 0

        for proc in processes:

            try:
                pid = proc.info["pid"]
                name = proc.info["name"] or "Unknown"

                cpu = proc.cpu_percent(None)

                memory = proc.info["memory_info"]
                ram_mb = memory.rss / (1024 * 1024)

                total_cpu += cpu
                total_ram += ram_mb

                print(
                    f"{pid:<8}"
                    f"{cpu:<10.1f}"
                    f"{ram_mb:<12.1f}"
                    f"{name:<30}"
                )

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        print("-" * 100)
        print(f"GameLoop CPU total: {total_cpu:.1f}%")
        print(f"GameLoop RAM total: {total_ram:.1f} MB")

    print()
    print("Refreshing every 2 seconds...")

    time.sleep(2)