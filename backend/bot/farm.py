import random
import time

from backend.bot.helpers import farm_api_url


def generic_action(session, rid: str, server: str, payload: dict):
    response = session.post(farm_api_url(server), data=payload)
    response.raise_for_status()
    result = response.json()
    if result.get("status") == "error":
        print(f"Blad serwera: {result.get('msg', 'Nieznany blad')}")
    return result


def collect_any(session, rid: str, server: str, farm: int, position: int):
    payload = {"rid": rid, "mode": "inner_crop", "farm": farm, "position": position}
    result = generic_action(session, rid, server, payload)
    print(f"[Pozycja {position}] Proba zbioru.")
    return result


def start_any(
    session,
    rid: str,
    server: str,
    farm: int,
    position: int,
    pid: int,
    amount: int = 1,
):
    payload = {
        "rid": rid,
        "mode": "inner_feed",
        "farm": farm,
        "position": position,
        "pid": pid,
        "c": f"{pid}_1|",
        "amount": amount,
    }
    result = generic_action(session, rid, server, payload)
    print(f"[Pozycja {position}] Start produkcji (ID: {pid})")
    return result


def run_farm_cycle(
    session,
    rid: str,
    server: str,
    farm: int = 1,
    positions=range(1, 7),
    has_premium: bool = False,
):
    print("START inteligentnego cyklu farmy")

    payload = {"rid": rid, "mode": "getfarms", "farm": farm, "position": 0}
    response = session.post(farm_api_url(server), data=payload)
    response.raise_for_status()
    data = response.json()
    farm_data = data.get("updateblock", {}).get("farms", {}).get("farms", {}).get(str(farm), {})

    for pos in positions:
        pos_key = str(pos)
        if pos_key not in farm_data:
            continue

        slot = farm_data[pos_key]
        if slot.get("premium") and not has_premium:
            continue

        building_id = slot.get("buildingid")
        print(f"Obsluga pozycji {pos} (Budynek ID: {building_id})")

        collect_any(session, rid, server, farm, pos)
        time.sleep(random.uniform(1.0, 2.0))

        if building_id:
            start_any(session, rid, server, farm, pos, pid=int(building_id))
            time.sleep(random.uniform(1.0, 2.0))

    print("KONIEC cyklu")
