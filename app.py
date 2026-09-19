import psutil
import time
from datetime import datetime

try:
    import GPUtil
except ImportError:
    GPUtil = None


def get_gpu_info():
    if GPUtil is None:
        return None

    gpus = GPUtil.getGPUs()

    if not gpus:
        return None

    gpu = gpus[0]

    return {
        "gpu_name": gpu.name,
        "gpu_usage": gpu.load * 100,
        "gpu_memory_used": gpu.memoryUsed,
        "gpu_memory_total": gpu.memoryTotal,
        "gpu_temperature": gpu.temperature,
    }


def get_system_info():
    memory = psutil.virtual_memory()

    cpu_usage = psutil.cpu_percent(interval=1)

    gpu = get_gpu_info()

    return {
        "timestamp": datetime.now().isoformat(),

        "cpu_usage": cpu_usage,
        "cpu_cores": psutil.cpu_count(logical=False),
        "cpu_threads": psutil.cpu_count(logical=True),

        "ram_used": memory.used / (1024 ** 3),
        "ram_total": memory.total / (1024 ** 3),
        "ram_usage": memory.percent,

        "gpu": gpu,
    }


while True:

    info = get_system_info()

    print("\n-----------------------------")
    print("GameLoop AI Optimizer")
    print("-----------------------------")

    print(f"CPU Usage: {info['cpu_usage']:.1f}%")
    print(f"CPU Cores: {info['cpu_cores']}")
    print(f"CPU Threads: {info['cpu_threads']}")

    print(f"RAM Usage: {info['ram_usage']:.1f}%")
    print(f"RAM Used: {info['ram_used']:.2f} GB")
    print(f"RAM Total: {info['ram_total']:.2f} GB")

    if info["gpu"]:
        gpu = info["gpu"]

        print(f"GPU: {gpu['gpu_name']}")
        print(f"GPU Usage: {gpu['gpu_usage']:.1f}%")
        print(f"GPU Temperature: {gpu['gpu_temperature']}°C")
        print(
            f"GPU Memory: "
            f"{gpu['gpu_memory_used']:.0f}/"
            f"{gpu['gpu_memory_total']:.0f} MB"
        )

    time.sleep(2)