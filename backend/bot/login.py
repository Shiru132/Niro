import re
import time

import requests


def login_wolnifarmerzy(
    username: str,
    password: str,
    server: str = "1",
    ref: str = "",
    retid: str = "",
):
    session = requests.Session()
    now_ms = int(time.time() * 1000)

    token_url = "https://www.wolnifarmerzy.pl/ajax/createtoken2.php"
    payload = {
        "server": server,
        "username": username,
        "password": password,
        "ref": ref,
        "retid": retid,
    }

    response = session.post(token_url, params={"n": now_ms}, data=payload, timeout=20)
    response.raise_for_status()
    result = response.json()

    if not isinstance(result, list) or len(result) < 2:
        raise ValueError("Nieprawidlowy format odpowiedzi logowania.")

    if result[0] == 0:
        raise ValueError(f"Logowanie nieudane: {result[1]}")

    redirect_url = result[1]
    if not redirect_url:
        raise ValueError("Brak przekierowania po logowaniu.")

    html = session.get(redirect_url, timeout=20).text
    match = re.search(r'id="rid"\s+value="([0-9a-f]+)"', html)
    if not match:
        match = re.search(r"var\s+rid\s*=\s*'([0-9a-f]+)'", html)
    if not match:
        raise ValueError("Nie udalo sie odczytac RID z HTML.")

    rid = match.group(1)
    return session, rid
