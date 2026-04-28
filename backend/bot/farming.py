import random
import time

from backend.bot.game_data import ANIMAL_PID_BY_BUILDING, BUILDING_NAMES
from backend.bot.helpers import farm_api_url


def _post_action(session, server: str, payload: dict):
    response = session.post(farm_api_url(server), data=payload)
    response.raise_for_status()
    return response.json()


def _fetch_farm_snapshot(session, rid: str, server: str, farm: int = 1) -> dict:
    payload = {"rid": rid, "mode": "getfarms", "farm": str(farm), "position": "0"}
    data = _post_action(session, server, payload)
    farms = data.get("updateblock", {}).get("farms", {}).get("farms", {})
    return farms.get(str(farm), {})


def farm_status(session, rid: str, server: str, farm: int = 1):
    try:
        farms = _fetch_farm_snapshot(session, rid, server, farm)
    except Exception as exc:
        print(f"Blad odczytu farmy: {exc}")
        return None

    print(f"\nSTAN FARMY {farm}:")
    print("-" * 40)
    for pos, field in farms.items():
        if not isinstance(field, dict):
            continue

        building_id = str(field.get("buildingid", ""))
        name = BUILDING_NAMES.get(building_id, f"Budynek {building_id}")
        status = int(field.get("status", 0))

        if building_id == "1":
            if status == 1:
                status_text = "Gotowe do zbioru"
            elif status == 2:
                status_text = "Rosnie"
            else:
                status_text = "Gotowe do sadzenia"
            print(f"Pole {pos}: {name} - {status_text}")
        else:
            if status == 1:
                status_text = "Gotowe do zebrania"
            elif status == 2:
                status_text = "W produkcji"
            else:
                status_text = "Gotowe do karmienia"
            print(f"Poz.{pos}: {name} - {status_text}")

    print("-" * 40)
    return farms


def field_plant(session, rid: str, server: str, farm: int = 1, position: int = 1, pid: int = 17):
    try:
        farm_data = _fetch_farm_snapshot(session, rid, server, farm)
        field_data = farm_data.get(str(position), {})
        building_id = str(field_data.get("buildingid", ""))
        status = int(field_data.get("status", 0))
    except Exception as exc:
        print(f"Nie mozna odczytac danych pola {position}: {exc}")
        return None

    if building_id != "1":
        print(f"Pozycja {position} to nie pole (budynek {building_id}).")
        return None
    if status == 2:
        print(f"Na polu {position} juz cos rosnie.")
        return None

    payload = {
        "rid": rid,
        "mode": "plant",
        "farm": str(farm),
        "position": str(position),
        "pid": str(pid),
    }
    print(f"Sadzenie na polu {position} (PID={pid})...")

    try:
        result = _post_action(session, server, payload)
    except Exception as exc:
        print(f"Wyjatek sadzenia: {exc}")
        return None

    if result.get("status") == "error":
        print(f"Blad: {result.get('msg', 'Nieznany blad')}")
    else:
        print("Posadzono pomyslnie.")
    return result


def field_harvest(session, rid: str, server: str, farm: int = 1, position: int = 1):
    payload = {
        "rid": rid,
        "mode": "harvest",
        "farm": str(farm),
        "position": str(position),
    }
    print(f"Zbior pola {position}...")

    try:
        result = _post_action(session, server, payload)
    except Exception as exc:
        print(f"Wyjatek zbioru: {exc}")
        return None

    if result.get("status") == "error":
        print(f"Blad: {result.get('msg', 'Nieznany blad')}")
    else:
        print("Zebrano pomyslnie.")
    return result


def feed_animal(session, rid: str, server: str, farm: int = 1, position: int = 2, pid: int = 4):
    payload = {
        "rid": rid,
        "mode": "feed",
        "farm": str(farm),
        "position": str(position),
        "pid": str(pid),
        "c": f"{pid}_1|",
        "amount": "1",
    }
    print(f"Karmienie zwierzat na pozycji {position} (PID={pid})...")

    try:
        result = _post_action(session, server, payload)
    except Exception as exc:
        print(f"Wyjatek karmienia: {exc}")
        return None

    if result.get("status") == "error":
        print(f"Blad: {result.get('msg', 'Nieznany blad')}")
    else:
        print("Nakarmiono.")
    return result


def collect_animal(session, rid: str, server: str, farm: int = 1, position: int = 2):
    payload = {
        "rid": rid,
        "mode": "collect",
        "farm": str(farm),
        "position": str(position),
    }
    print(f"Zbieranie od zwierzat na pozycji {position}...")

    try:
        result = _post_action(session, server, payload)
    except Exception as exc:
        print(f"Wyjatek zbioru od zwierzat: {exc}")
        return None

    if result.get("status") == "error":
        print(f"Blad: {result.get('msg', 'Nieznany blad')}")
    else:
        print("Zebrano.")
    return result


def auto_farm_cycle(
    session,
    rid: str,
    server: str,
    farm: int = 1,
    positions=range(1, 7),
):
    print("\n" + "=" * 50)
    print("AUTO CYKL FARMY")
    print("=" * 50)

    try:
        farms = _fetch_farm_snapshot(session, rid, server, farm)
    except Exception as exc:
        print(f"Blad w cyklu: {exc}")
        return

    for pos in positions:
        pos_key = str(pos)
        if pos_key not in farms:
            continue

        field = farms[pos_key]
        building_id = str(field.get("buildingid", ""))
        status = int(field.get("status", 0))
        print(f"\nPozycja {pos} (budynek {building_id})")

        if building_id == "1":
            if status == 1:
                field_harvest(session, rid, server, farm, pos)
                time.sleep(random.uniform(1.0, 2.0))
                field_plant(session, rid, server, farm, pos, pid=17)
            elif status == 0:
                field_plant(session, rid, server, farm, pos, pid=17)
        elif building_id in ANIMAL_PID_BY_BUILDING:
            animal_pid = ANIMAL_PID_BY_BUILDING[building_id]
            if status == 1:
                collect_animal(session, rid, server, farm, pos)
                time.sleep(random.uniform(1.0, 2.0))
                feed_animal(session, rid, server, farm, pos, animal_pid)
            elif status == 0:
                feed_animal(session, rid, server, farm, pos, animal_pid)

        time.sleep(random.uniform(1.0, 2.5))

    print("\n" + "=" * 50)
    print("CYKL ZAKONCZONY")
    print("=" * 50)
