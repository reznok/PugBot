import json

import requests

LEG_WITH_SOCKET = [
    132369, 132410, 137044, 132444, 132449, 132452, 132460, 133973, 133974, 137037, 137038, 137039, 137040,
    137041, 137042, 137043, 132378, 137045, 137046, 137047, 137048, 137049, 137050, 137051, 137052, 137054, 137055,
    137220, 137223, 137276, 137382, 138854
]

ENCHANTABLE_SLOTS = ["neck", "back", "finger1", "finger2"]

config = json.loads(open('config.json').read())  # Load Configs
API_KEY = config["blizzard_api_key"]


def get_sockets(player_dictionary):
    """
    Return dict with total sockets and count of equipped gems and slots that are missing

    :param player_dictionary: Retrieved player dict from API
    :return: dict()
    """
    sockets = 0
    equipped_gems = 0

    for item in player_dictionary["items"]:
        if item in "averageItemLevel" or item in "averageItemLevelEquipped":
            continue

        if int(player_dictionary["items"][item]["id"]) in LEG_WITH_SOCKET:
            sockets += 1

        for bonus in player_dictionary["items"][item]["bonusLists"]:
            if bonus == 1808:  # 1808 is Legion prismatic socket bonus
                sockets += 1

        for ttip in player_dictionary["items"][item]["tooltipParams"]:
            if item in "mainHand" or item in "offHand":  # Ignore Relic
                continue
            if "gem" in ttip:  # Equipped gems are listed as gem0, gem1, etc...
                equipped_gems += 1

    return {"total_sockets": sockets,
            "equipped_gems": equipped_gems}


def get_enchants(player_dictionary):
    """
    Get count of enchants missing and slots that are missing
    :param player_dictionary:
    :return: dict()
    """
    missing_enchant_slots = []
    for slot in ENCHANTABLE_SLOTS:
        if "enchant" not in player_dictionary["items"][slot]["tooltipParams"]:
            missing_enchant_slots.append(slot)

    return {
        "enchantable_slots": len(ENCHANTABLE_SLOTS),
        "missing_slots": missing_enchant_slots,
        "total_missing": len(missing_enchant_slots)
    }


def get_progress(player_dictionary, raid):
    r = [x for x in player_dictionary["progression"]
         ["raids"] if x["name"] in raid][0]
    normal = 0
    heroic = 0
    mythic = 0

    for boss in r["bosses"]:
        if boss["normalKills"] > 0:
            normal += 1
        if boss["heroicKills"] > 0:
            heroic += 1
        if boss["mythicKills"] > 0:
            mythic += 1

    return {"normal": normal,
            "heroic": heroic,
            "mythic": mythic,
            "total_bosses": len(r["bosses"])}


def get_char(name, server):
    r = requests.get(
        "https://us.api.battle.net/wow/character/%s/%s?fields=items&locale=en_US&apikey=%s" % (
            server, name, API_KEY))
    if r.status_code != 200:
        raise Exception("Could Not Find Character (No 200 from API)")

    player_item_dict = json.loads(r.text)

    r = requests.get(
        "https://us.api.battle.net/wow/character/%s/%s?fields=progression&locale=en_US&apikey=%s" % (
            server, name, API_KEY))
    if r.status_code != 200:
        raise Exception("Could Not Find Character (No 200 From API)")

    player_progression_dict = json.loads(r.text)

    r = requests.get(
        "https://us.api.battle.net/wow/data/character/classes?locale=en_US&apikey=%s" % (API_KEY))
    if r.status_code != 200:
        raise Exception("Could Not Find Character classes (No 200 From API)")
    class_dict = json.loads(r.text)
    class_dict = {c['id']: c['name'] for c in class_dict["classes"]}

    equipped_ivl = player_item_dict["items"]["averageItemLevelEquipped"]
    sockets = get_sockets(player_item_dict)
    enchants = get_enchants(player_item_dict)
    tov_progress = get_progress(player_progression_dict, "Trial of Valor")
    en_progress = get_progress(
        player_progression_dict, "The Emerald Nightmare")

    armory_url = 'http://us.battle.net/wow/en/character/{}/{}/advanced'.format(
        server, name)

    return_string = ''
    return_string += "**%s** - **%s**\n" % (
        name.title(), server.title())

    return_string += '{} | {}\n'.format(player_item_dict['level'], class_dict[
                                        player_item_dict['class']])
    return_string += '<{}>\n'.format(armory_url)
    return_string += '```Markdown\n'  # start Markdown

    # iLvL
    return_string += "Equipped Item Level: %s\n" % equipped_ivl

    # Raid Progression
    return_string += "EN: {1}/{0} (N), {2}/{0} (H), {3}/{0} (M)\n".format(en_progress["total_bosses"],
                                                                          en_progress[
                                                                              "normal"],
                                                                          en_progress[
                                                                              "heroic"],
                                                                          en_progress["mythic"])
    return_string += "TOV: {1}/{0} (N), {2}/{0} (H), {3}/{0} (M)\n".format(tov_progress["total_bosses"],
                                                                           tov_progress[
                                                                               "normal"],
                                                                           tov_progress[
                                                                               "heroic"],
                                                                           tov_progress["mythic"])

    # Gems
    return_string += "Gems Equipped: %s/%s\n" % (
        sockets["equipped_gems"], sockets["total_sockets"])

    # Enchants
    return_string += "Enchants: %s/%s\n" % (enchants["enchantable_slots"] - enchants["total_missing"],
                                            enchants["enchantable_slots"])
    if enchants["total_missing"] > 0:
        return_string += "Missing Enchants: {0}".format(
            ", ".join(enchants["missing_slots"]))

    return_string += '```'  # end Markdown
    return return_string


async def pug(client, message):
    try:
        i = str(message.content).split(' ')
        name = i[1]
        server = i[2]
        character_info = get_char(name, server)
        await client.send_message(message.channel, character_info)
    except Exception as e:
        await client.send_message(message.channel, "Error: %s" % e)
