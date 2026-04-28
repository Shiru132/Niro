from backend.bot.helpers import farm_api_url


def get_player_data(session, rid: str, server: str):
    payload = {"rid": rid, "mode": "getfarms", "farm": 1, "position": 0}
    response = session.post(farm_api_url(server), data=payload)
    response.raise_for_status()
    data = response.json()

    menu = data.get("updateblock", {}).get("menue", {})
    level = menu.get("levelnum", 0)
    guild_name = menu.get("guildname", "")
    name = menu.get("uname", "")
    premium_flag = menu.get("premium", 0)

    if premium_flag == 1:
        premium = "Konto premium aktywne"
    elif premium_flag == 0:
        premium = "Brak konta premium"
    else:
        premium = "Nieznany status premium"

    return level, name, guild_name, premium
