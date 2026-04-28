import sys
from typing import Any


def wyjscie() -> None:
    print("Koniec programu.")
    sys.exit()


def farm_api_url(server: str) -> str:
    return f"https://s{server}.wolnifarmerzy.pl/ajax/farm.php"


def check_and_get_login_bonus(session, rid: str, server: str) -> bool:
    payload = {"rid": rid, "mode": "getupdateblock"}
    response = session.post(farm_api_url(server), data=payload)
    response.raise_for_status()
    data = response.json()

    login_bonus = data.get("updateblock", {}).get("menue", {}).get("loginbonus", {})
    first_daily_visit = login_bonus.get("firstdailyvisit")

    if first_daily_visit != 1:
        print("Dzienny bonus jest juz odebrany.")
        return False

    day = login_bonus.get("day", 1)
    print(f"Dostepny dzienny bonus (day={day}), odbieram...")

    reward_payload = {"rid": rid, "mode": "loginbonus_getreward", "day": day}
    reward_response = session.post(farm_api_url(server), data=reward_payload)
    reward_response.raise_for_status()

    print("Dzienny bonus odebrany.")
    return True


def get_farms(session, rid: str, server: str) -> dict[str, Any]:
    payload = {"rid": rid, "mode": "getfarms", "farm": 1, "position": 0}
    response = session.post(farm_api_url(server), data=payload)
    response.raise_for_status()
    return response.json()


def garden_init(session, rid: str, server: str, farm: int, position: int) -> dict[str, Any]:
    payload = {
        "rid": rid,
        "mode": "garden_init",
        "farm": farm,
        "position": position,
    }
    response = session.post(farm_api_url(server), data=payload)
    response.raise_for_status()
    return response.json()


def get_all_buildings(session, rid: str, server: str) -> dict[int, dict[int, Any]]:
    payload = {"rid": rid, "mode": "getfarms"}
    response = session.post(farm_api_url(server), data=payload)
    response.raise_for_status()
    data = response.json()

    farms_data = data.get("updateblock", {}).get("farms", {}).get("farms", {})
    result: dict[int, dict[int, Any]] = {}

    if isinstance(farms_data, dict):
        farms_iter = farms_data.items()
    else:
        farms_iter = enumerate(farms_data, start=1)

    for farm_index, farm in farms_iter:
        if not isinstance(farm, dict):
            continue

        farm_key = int(farm_index)
        result[farm_key] = {}

        for position_key, position in farm.items():
            if not isinstance(position, dict):
                continue

            building_id = position.get("buildingid")
            if building_id is None:
                continue

            try:
                position_index = int(position_key)
            except (TypeError, ValueError):
                continue

            result[farm_key][position_index] = building_id

    return result
