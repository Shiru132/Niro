import random
import time

from backend.bot.game_data import CROP_SIZES
from backend.bot.helpers import farm_api_url, get_all_buildings
from backend.bot.resources import show_inventory

GARDEN_WIDTH = 12
GARDEN_MAX_FIELD = 121


def garden_crop(session, rid: str, server: str, farm: int = 1, position: int = 2):
    payload = {
        "rid": rid,
        "mode": "cropgarden",
        "farm": str(farm),
        "position": str(position),
    }

    print(f"\nZbieranie z farmy {farm}, pozycja {position}")
    try:
        response = session.post(farm_api_url(server), data=payload)
        response.raise_for_status()
        result = response.json()
    except Exception as exc:
        print(f"Blad zbioru: {exc}")
        return None

    if result.get("status") == "error":
        print(f"Blad zbioru: {result.get('msg', 'Nieznany')}")
    else:
        print("Zebrano pomyslnie.")
    return result


def _resolve_crop_size(pid: int) -> int:
    size = int(CROP_SIZES.get(pid, 1))
    if size not in (1, 2, 4):
        return 1
    return size


def _iter_start_fields(size: int, max_field: int = GARDEN_MAX_FIELD) -> list[int]:
    rows = (max_field - 1) // GARDEN_WIDTH + 1
    starts: list[int] = []

    for row in range(rows):
        if size == 4 and row % 2 == 1:
            continue

        if size in (2, 4):
            col_values = range(1, GARDEN_WIDTH + 1, 2)
        else:
            col_values = range(1, GARDEN_WIDTH + 1)

        for col in col_values:
            field = row * GARDEN_WIDTH + col
            if field > max_field:
                continue

            if size == 2:
                if col + 1 > GARDEN_WIDTH or field + 1 > max_field:
                    continue
            elif size == 4:
                if col + 1 > GARDEN_WIDTH:
                    continue
                if field + GARDEN_WIDTH > max_field:
                    continue
                if field + GARDEN_WIDTH + 1 > max_field:
                    continue

            starts.append(field)

    return starts


def garden_plant(
    session,
    rid: str,
    server: str,
    farm: int = 1,
    position: int = 2,
    pflanze_id: int = 17,
    fields: list[int] | None = None,
    cid: int | None = None,
    request_delay: float | None = None,
):
    if cid is None:
        raise ValueError("Parametr cid jest wymagany dla garden_plant.")

    size = _resolve_crop_size(pflanze_id)
    start_fields = fields or _iter_start_fields(size)

    print(f"\nSadzenie na farmie {farm}, pozycja {position}, CID: {cid}")
    print(f"Roslina ID: {pflanze_id}, size={size}, liczba requestow: {len(start_fields)}")

    results = []
    for field in start_fields:
        block = _fields_block(field, size=size)
        params = {
            "rid": rid,
            "mode": "garden_plant",
            "farm": str(farm),
            "position": str(position),
            "cid": str(cid),
            "pflanze[0]": str(pflanze_id),
            "feld[0]": str(field),
            "felder[0]": ",".join(map(str, block)),
        }

        try:
            response = session.get(farm_api_url(server), params=params)
            response.raise_for_status()
            result = response.json()
            results.append(result)
            status = result.get("status")
            if status == "error":
                print(
                    f"[PLANT] feld={field} felder={','.join(map(str, block))} "
                    f"BLAD: {result.get('msg', 'Nieznany')}"
                )
            else:
                print(f"[PLANT] feld={field} felder={','.join(map(str, block))} OK")
        except Exception as exc:
            print(
                f"[PLANT] feld={field} felder={','.join(map(str, block))} "
                f"BLAD requestu: {exc}"
            )

        time.sleep(request_delay if request_delay is not None else random.uniform(1.283, 1.962))

    return results


def _fields_block(field: int, product: int | None = None, size: int | None = None) -> list[int]:
    if size is None:
        if product is None:
            size = 1
        else:
            size = _resolve_crop_size(product)

    if size == 4:
        return [field, field + 1, field + GARDEN_WIDTH, field + GARDEN_WIDTH + 1]
    if size == 2:
        return [field, field + 1]
    return [field]


def garden_water(
    session,
    rid: str,
    server: str,
    farm: int = 1,
    position: int = 2,
    start_fields: list[int] | None = None,
    product: int | None = None,
    request_delay: float | None = None,
):
    if product is None:
        raise ValueError("Parametr product (PID) jest wymagany do podlewania.")

    size = _resolve_crop_size(product)
    fields = start_fields or _iter_start_fields(size)

    print(
        f"Podlewanie farma={farm}, pozycja={position}, PID={product}, "
        f"size={size}, liczba requestow: {len(fields)}"
    )

    for field in fields:
        block = _fields_block(field, size=size)
        params = {
            "rid": rid,
            "mode": "garden_water",
            "farm": str(farm),
            "position": str(position),
            "feld[]": str(field),
            "felder[]": ",".join(map(str, block)),
        }

        try:
            response = session.get(farm_api_url(server), params=params)
            response.raise_for_status()
            print(f"[WATER] feld={field} felder={','.join(map(str, block))} OK")
        except Exception as exc:
            print(
                f"[WATER] feld={field} felder={','.join(map(str, block))} "
                f"BLAD requestu: {exc}"
            )

        time.sleep(request_delay if request_delay is not None else random.uniform(1.283, 1.962))


def test_garden(session, rid: str, server: str, cid: int):
    print("\n" + "=" * 50)
    print("TEST SADZENIA")
    print("=" * 50)
    show_inventory(session, rid, server)

    raw_pid = input("Podaj PID rosliny: ").strip()
    try:
        product = int(raw_pid)
    except ValueError:
        print("Niepoprawny PID.")
        return

    garden_crop(session, rid, server, farm=1, position=2)
    garden_plant(
        session,
        rid,
        server,
        farm=1,
        position=2,
        pflanze_id=product,
        cid=cid,
    )
    garden_water(
        session,
        rid,
        server,
        farm=1,
        position=2,
        product=product,
    )


def plant_and_water_building_one_on_farms(
    session,
    rid: str,
    server: str,
    pid: int,
    cid: int,
    farm_start: int = 1,
    farm_end: int = 4,
):
    buildings = get_all_buildings(session, rid, server)
    done: list[tuple[int, int]] = []
    skipped: list[tuple[int, int, str]] = []

    for farm_id in range(farm_start, farm_end + 1):
        farm_positions = buildings.get(farm_id, {})
        if not farm_positions:
            print(f"Farma {farm_id}: brak danych lub brak pozycji.")
            continue

        target_positions = [
            position
            for position, building_id in farm_positions.items()
            if str(building_id) == "1"
        ]

        if not target_positions:
            print(f"Farma {farm_id}: brak pozycji z buildingid=1.")
            continue

        sorted_positions = sorted(target_positions)
        for idx, position in enumerate(sorted_positions):
            print(
                f"\n[Farma {farm_id}, pozycja {position}] "
                f"crop -> plant(PID={pid}) -> water"
            )
            try:
                garden_crop(session, rid, server, farm=farm_id, position=position)
                plant_result = garden_plant(
                    session,
                    rid,
                    server,
                    farm=farm_id,
                    position=position,
                    pflanze_id=pid,
                    cid=cid,
                )
                if any(
                    isinstance(item, dict) and item.get("status") == "error"
                    for item in (plant_result or [])
                ):
                    reason = "co najmniej jeden request sadzenia zwrocil blad"
                    skipped.append((farm_id, position, reason))
                    print(f"Pominieto: {reason}")
                else:
                    garden_water(
                        session,
                        rid,
                        server,
                        farm=farm_id,
                        position=position,
                        product=pid,
                    )
                    done.append((farm_id, position))
            except Exception as exc:
                skipped.append((farm_id, position, str(exc)))
                print(f"Pominieto przez wyjatek: {exc}")

            if idx < len(sorted_positions) - 1:
                time.sleep(random.uniform(5.374, 7.823))

    print("\n=== PODSUMOWANIE ===")
    print(f"Wykonane: {len(done)}")
    for farm_id, position in done:
        print(f"- Farma {farm_id}, pozycja {position}")

    print(f"Pominiete: {len(skipped)}")
    for farm_id, position, reason in skipped:
        print(f"- Farma {farm_id}, pozycja {position}: {reason}")

    return {"done": done, "skipped": skipped}
