import json
import re

from backend.bot.game_data import PRODUCT_NAMES
from backend.bot.helpers import farm_api_url


def owned_products(session, rid: str, server: str) -> dict[str, int]:
    payload = {"rid": rid, "mode": "getfarms", "farm": 1, "position": 0}
    response = session.post(farm_api_url(server), data=payload)
    response.raise_for_status()
    data = response.json()

    stock = data.get("updateblock", {}).get("stock", {}).get("stock", {})
    owned: dict[str, int] = {}

    def traverse(node):
        if not isinstance(node, dict):
            return

        if "amount" in node and "pid" in node:
            pid = str(node["pid"])
            try:
                amount = int(node.get("amount", 0))
            except (TypeError, ValueError):
                amount = 0
            if amount > 0:
                owned[pid] = amount
            return

        for value in node.values():
            traverse(value)

    traverse(stock)
    return owned


def get_main_page(session, server: str) -> str:
    url = f"https://s{server}.wolnifarmerzy.pl/main.php"
    response = session.get(url)
    response.raise_for_status()
    return response.text


def extract_produkty(html: str) -> dict[str, str]:
    pattern = r"var produkt_name\s*=\s*({.*?});"
    match = re.search(pattern, html, re.DOTALL)
    if not match:
        return {}

    js_object = re.sub(r",\s*}", "}", match.group(1))
    try:
        parsed = json.loads(js_object)
    except json.JSONDecodeError:
        return {}

    return {str(k): str(v) for k, v in parsed.items()}


def show_inventory(session, rid: str, server: str) -> dict[str, int]:
    html = get_main_page(session, server)
    product_names = extract_produkty(html)
    owned = owned_products(session, rid, server)

    print("\n--- EKWIPUNEK ---")
    if not owned:
        print("Brak produktow.")
        return owned

    for pid, amount in sorted(owned.items(), key=lambda item: int(item[0])):
        fallback_name = PRODUCT_NAMES.get(int(pid), f"Nieznany produkt ({pid})")
        name = product_names.get(pid, fallback_name)
        print(f"PID: {pid}, Nazwa: {name}, Ilosc: {amount}")

    return owned
