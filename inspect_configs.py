from pathlib import Path


BASE = Path(r"C:\Program Files\TxGameAssistant")


TARGET_FILES = [
    "AowConfig.ini",
    "Config.ini",
    "ConfigPath.xml",
    "HardwareDetect.xml",
    "opengl.conf",
    "AowGame.xml",
    "AndroidEmulator.xml",
]


def find_file(filename):

    matches = []

    for path in BASE.rglob(filename):
        matches.append(path)

    return matches


for filename in TARGET_FILES:

    print("\n")
    print("=" * 100)
    print(f"SEARCHING: {filename}")
    print("=" * 100)

    matches = find_file(filename)

    if not matches:

        print("Not found.")
        continue

    for path in matches:

        print(f"\nFILE: {path}")
        print("-" * 100)

        try:

            with open(
                path,
                "r",
                encoding="utf-8",
                errors="replace"
            ) as file:

                content = file.read()

            print(content[:15000])

        except PermissionError:

            print("Permission denied.")

        except Exception as e:

            print(f"Error: {e}")