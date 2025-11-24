import csv
from pathlib import Path
from typing import List, Dict

def export_to_csv(rows: List[Dict], outpath: Path):
    outpath.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    keys = sorted({k for r in rows for k in r.keys()})
    with outpath.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)
