from pathlib import Path
import json

class SeenDB:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if self.path.exists():
            try:
                self.data = set(json.loads(self.path.read_text()))
            except Exception:
                self.data = set()
        else:
            self.data = set()

    def has(self, key: str) -> bool:
        return key in self.data

    def add(self, key: str):
        self.data.add(key)

    def save(self):
        self.path.write_text(json.dumps(sorted(self.data), ensure_ascii=False, indent=2))
