import farming
import helpers
from backend.bot.garden import garden_water
from backend.bot.resources import show_inventory


def _pause() -> None:
    input("\nENTER aby wrocic...")


def _read_int(prompt: str) -> int | None:
    raw = input(prompt).strip()
    try:
        return int(raw)
    except ValueError:
        print("Niepoprawna liczba.")
        return None


def menu(session, rid: str, server: str, has_premium: bool):
    _ = has_premium

    while True:
        print("\n" + "=" * 40)
        print("MENU GLOWNE")
        print("=" * 40)
        print("1. Auto cykl farmy")
        print("2. Sadz na polu")
        print("3. Zbierz z pola")
        print("4. Karm zwierzeta")
        print("5. Zbierz od zwierzat")
        print("6. Status farmy")
        print("7. Ekwipunek")
        print("8. Dzienny bonus")
        print("9. Podlewanie ogrodu")
        print("0. Wyjscie")
        print("=" * 40)

        choice = input("Wybierz opcje: ").strip()

        if choice == "1":
            farming.auto_farm_cycle(session, rid, server)
            _pause()
            continue

        if choice == "2":
            position = _read_int("Numer pola (1-6): ")
            if position is None:
                _pause()
                continue

            print("\nDostepne rosliny:")
            print("1. Zboze (PID 17)")
            print("2. Koniczyna (PID 18)")
            print("3. Zyto (PID 19)")
            print("4. Pszenica (PID 20)")
            print("5. Jeczmien (PID 21)")
            selected = input("Wybierz (1-5): ").strip()
            pid = {"1": 17, "2": 18, "3": 19, "4": 20, "5": 21}.get(selected, 17)
            farming.field_plant(session, rid, server, position=position, pid=pid)
            _pause()
            continue

        if choice == "3":
            position = _read_int("Numer pola (1-6): ")
            if position is not None:
                farming.field_harvest(session, rid, server, position=position)
            _pause()
            continue

        if choice == "4":
            position = _read_int("Pozycja zwierzat (2-krowy,3-kury,4-swinie,5-owce): ")
            if position is None:
                _pause()
                continue

            print("\nWybierz zwierzeta:")
            print("1. Krowy (PID 1)")
            print("2. Kury (PID 2)")
            print("3. Swinie (PID 3)")
            print("4. Owce (PID 4)")
            selected = input("Wybierz (1-4): ").strip()
            pid = {"1": 1, "2": 2, "3": 3, "4": 4}.get(selected, 1)
            farming.feed_animal(session, rid, server, position=position, pid=pid)
            _pause()
            continue

        if choice == "5":
            position = _read_int("Pozycja zwierzat: ")
            if position is not None:
                farming.collect_animal(session, rid, server, position=position)
            _pause()
            continue

        if choice == "6":
            farming.farm_status(session, rid, server)
            _pause()
            continue

        if choice == "7":
            try:
                show_inventory(session, rid, server)
            except Exception as exc:
                print(f"Blad: {exc}")
            _pause()
            continue

        if choice == "8":
            helpers.check_and_get_login_bonus(session, rid, server)
            _pause()
            continue

        if choice == "9":
            product = _read_int("PID rosliny do podlewania: ")
            if product is None:
                _pause()
                continue

            mode = input("1=wszystkie (1-121), 2=zakres: ").strip()
            if mode == "1":
                fields = list(range(1, 122))
            elif mode == "2":
                start = _read_int("Od grzadki (1-121): ")
                end = _read_int("Do grzadki (1-121): ")
                if start is None or end is None or not (1 <= start <= end <= 121):
                    print("Niepoprawny zakres.")
                    _pause()
                    continue
                fields = list(range(start, end + 1))
            else:
                print("Niepoprawna opcja.")
                _pause()
                continue

            garden_water(
                session,
                rid,
                server,
                farm=1,
                position=2,
                start_fields=fields,
                product=product,
            )
            _pause()
            continue

        if choice == "0":
            print("Do widzenia.")
            helpers.wyjscie()

        print("Niepoprawny wybor.")
        _pause()
