import time
import requests
from typing import Dict, List

BASE = "https://api.mercadolibre.com"

def _get(url: str, params: Dict=None, retries: int=3, timeout: int=15):
    for i in range(retries):
        r = requests.get(url, params=params, timeout=timeout)
        if r.status_code == 200:
            return r.json()
        time.sleep(1.5 * (i+1))
    r.raise_for_status()

def top_sellers_by_category(category_id: str, limit: int=5) -> List[Dict]:
    url = f"{BASE}/sites/MLB/search"
    params = {"category": category_id, "sort": "sold_quantity_desc", "limit": limit}
    data = _get(url, params=params)
    return data.get("results", [])

def get_item_details(item_id: str) -> Dict:
    url = f"{BASE}/items/{item_id}"
    return _get(url)
