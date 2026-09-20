import argparse
import csv
import json
import statistics
from pathlib import Path


def number(row, names):
    for name in names:
        for key, value in row.items():
            if key.lower() == name.lower() and value not in {None, "", "N/A"}:
                try:
                    return float(value)
                except ValueError:
                    pass
    return None


def analyze(path):
    frame_times = []
    with path.open(newline="", encoding="utf-8-sig") as stream:
        for row in csv.DictReader(stream):
            frame_time = number(row, ["MsBetweenPresents", "MsBetweenDisplayChange", "FrameTime", "FrameTimeMs"])
            if frame_time is not None and frame_time > 0:
                frame_times.append(frame_time)
    if not frame_times:
        raise ValueError("No usable frame-time column was found in the PresentMon CSV.")

    frame_times.sort()
    worst_count = max(1, len(frame_times) // 100)
    one_percent_low = 1000 / statistics.mean(frame_times[-worst_count:])
    average_fps = 1000 / statistics.mean(frame_times)
    median = statistics.median(frame_times)
    stutter_threshold = max(25.0, median * 1.5)
    stutters = sum(frame_time > stutter_threshold for frame_time in frame_times)
    return {
        "frames": len(frame_times),
        "average_fps": round(average_fps, 3),
        "one_percent_low": round(one_percent_low, 3),
        "frame_time_ms": round(statistics.mean(frame_times), 3),
        "frame_time_p95_ms": round(frame_times[int(len(frame_times) * 0.95)], 3),
        "stutter_events": stutters,
        "stutter_score": round(stutters / len(frame_times) * 100, 3),
    }


def main():
    parser = argparse.ArgumentParser(description="Analyze frame-time CSV output from PresentMon.")
    parser.add_argument("csv_file", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = analyze(args.csv_file)
    payload = json.dumps(result, indent=2)
    if args.output:
        args.output.write_text(payload + "\n", encoding="utf-8")
    else:
        print(payload)


if __name__ == "__main__":
    main()