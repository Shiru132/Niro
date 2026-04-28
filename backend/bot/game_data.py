PRODUCT_NAMES = {
    1: "Krowa",
    2: "Kura",
    3: "Swinia",
    4: "Owca",
    5: "Krolik",
    17: "Zboze",
    18: "Koniczyna",
    19: "Zyto",
    20: "Pszenica",
    21: "Jeczmien",
    22: "Owies",
    23: "Kukurydza",
    24: "Buraki",
    25: "Ziemniaki",
    108: "Rzepak",
    109: "Marchew",
}

# Rozmiar rosliny w ogrodzie:
# 1 = pojedyncze pole, 2 = 1x2, 4 = 2x2.
# Na razie wspieramy jawnie tylko:
# - zboze PID 1 -> size 2
# - marchew PID 17 -> size 1
# - rzepak PID 4 -> size 4
CROP_SIZES = {
    1: 2,
    17: 1,
    4: 4,
}

BUILDING_NAMES = {
    "1": "Pole",
    "2": "Krowy",
    "3": "Kury",
    "4": "Swinie",
    "5": "Owce",
    "6": "Mlyn",
    "7": "Piekarnia",
    "8": "Browar",
    "9": "Tkalnia",
    "10": "Serowarnia",
    "11": "Wedzarnia",
    "12": "Masarnia",
    "15": "Kroliki",
}

ANIMAL_PID_BY_BUILDING = {
    "2": 1,
    "3": 2,
    "4": 3,
    "5": 4,
    "15": 5,
}
