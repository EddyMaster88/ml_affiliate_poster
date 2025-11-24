from pathlib import Path
import requests, hashlib

def download_image(url: str, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    name = hashlib.sha1(url.encode("utf-8")).hexdigest() + ".jpg"
    path = out_dir / name
    if path.exists():
        return path
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    path.write_bytes(r.content)
    return path
