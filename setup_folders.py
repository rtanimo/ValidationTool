from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

folders = ["incoming", "output", "known", "logs"]

for folder in folders:
    (BASE_DIR / folder).mkdir(exist_ok=True)

print("Folders created.")
