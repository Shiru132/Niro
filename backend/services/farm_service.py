from requests import session

from backend.bot import garden, farming
from backend.bot.login import login_wolnifarmerzy
from backend.bot.player_data import get_player_data
import os

SESSION = None
RID = None
SERVER = "13"


def init():
    global SESSION, RID
    if SESSION is None:
        user = os.getenv("WF_USER")
        password = os.getenv("WF_PASS")
        server = os.getenv("WF_SERVER", "13")

        SESSION, RID = login_wolnifarmerzy(user, password, server)

        level, name, guild, premium = get_player_data(SESSION, RID, SERVER)
        print("Zalogowany jako:", name)


def run_garden_service(pid: int, cid: int):
    init()
    garden.plant_and_water_building_one_on_farms(
        SESSION,
        RID,
        SERVER,
        pid=pid,
        cid=cid
    )
    return {"status": "ok"}


def get_status():
    init()
    data = farming.farm_status(SESSION, RID, SERVER)
    return {"data": data}