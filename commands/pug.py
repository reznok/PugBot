import json

import requests

LEG_WITH_SOCKET = [
    132369, 132410, 137044, 132444, 132449, 132452, 132460, 133973, 133974, 137037, 137038, 137039, 137040,
    137041, 137042, 137043, 132378, 137045, 137046, 137047, 137048, 137049, 137050, 137051, 137052, 137054, 137055,
    137220, 137223, 137276, 137382, 138854
]

ENCHANTABLE_SLOTS = ["neck", "back", "finger1", "finger2"]
RAIDS = [('The Emerald Nightmare', 'EN'), ('Trial of Valor', 'TOV'), ('The Nighthold', 'NH')]


region_locale = {
    'us': ['us', 'en_US', 'en'],
#    'kr': ['kr', 'ko_KR', 'ko'],
#    'tw': ['tw', 'zh_TW', 'zh'],
    'eu': ['eu', 'en_GB', 'en']
}

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
        else:
            for bonus in player_dictionary["items"][item]["bonusLists"]:
                if bonus == 1808:  # 1808 is Legion prismatic socket bonus
                    sockets += 1

            if item in ["neck", "finger1", "finger2"]:
                if player_dictionary["items"][item]["context"] == "trade-skill":
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


def get_raid_progression(player_dictionary, raid):
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


def get_mythic_progression(player_dictionary):
    achievements = player_dictionary["achievements"]
    plus_two = 0
    plus_five = 0
    plus_ten = 0

    if 33096 in achievements["criteria"]:
        index = achievements["criteria"].index(33096)
        plus_two = achievements["criteriaQuantity"][index]

    if 33097 in achievements["criteria"]:
        index = achievements["criteria"].index(33097)
        plus_five = achievements["criteriaQuantity"][index]

    if 33098 in achievements["criteria"]:
        index = achievements["criteria"].index(33098)
        plus_ten = achievements["criteriaQuantity"][index]

    return {
        "plus_two": plus_two,
        "plus_five": plus_five,
        "plus_ten": plus_ten
    }


def get_char(name, server, target_region, api_key):
    r = requests.get("https://%s.api.battle.net/wow/character/%s/%s?fields=items+progression+achievements&locale=%s&apikey=%s" % (
            region_locale[target_region][0], server, name, region_locale[target_region][1], api_key))

    if r.status_code != 200:
        raise Exception("Could Not Find Character (No 200 from API)")

    player_dict = json.loads(r.text)

    r = requests.get(
        "https://%s.api.battle.net/wow/data/character/classes?locale=%s&apikey=%s" % (
            region_locale[target_region][0], region_locale[target_region][1], api_key))
    if r.status_code != 200:
        raise Exception("Could Not Find Character Classes (No 200 From API)")
    class_dict = json.loads(r.text)
    class_dict = {c['id']: c['name'] for c in class_dict["classes"]}

    equipped_ivl = player_dict["items"]["averageItemLevelEquipped"]
    sockets = get_sockets(player_dict)
    enchants = get_enchants(player_dict)

    mythic_progress = get_mythic_progression(player_dict)

    # Build raid progression
    raid_progress = {}
    for raid in RAIDS:
        raid_name = raid[0]
        raid_abrv = raid[1]
        raid_progress[raid_name] = {
            'abrv': raid_abrv,
            'progress': get_raid_progression(player_dict, raid_name)
        }

    armory_url = 'http://{}.battle.net/wow/{}/character/{}/{}/advanced'.format(
        region_locale[target_region][0], region_locale[target_region][2], server, name)

    return_string = ''
    return_string += "**%s** - **%s** - **%s %s**\n" % (
        name.title(), server.title(), player_dict['level'], class_dict[player_dict['class']])
    return_string += '<{}>\n'.format(armory_url)
    return_string += '```CSS\n'  # start Markdown

    # iLvL
    return_string += "Equipped Item Level: %s\n" % equipped_ivl

    # Mythic Progression
    return_string += "Mythics: +2: %s, +5: %s, +10: %s\n" % (mythic_progress["plus_two"],
                                                             mythic_progress["plus_five"],
                                                             mythic_progress["plus_ten"])

    # Raid Progression
    for raid, data in raid_progress.items():
        progress = data['progress']
        return_string += '{abrv}: {normal}/{total} (N), {heroic}/{total} (H), {mythic}/{total} (M)\n'.format(
            abrv=data['abrv'],
            normal=progress['normal'],
            heroic=progress['heroic'],
            mythic=progress['mythic'],
            total=progress['total_bosses']
        )

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


async def pug(client, region, api_key, message):
    target_region = region
    try:
        i = str(message.content).split(' ')
        name = i[1]
        server = i[2]
        if len(i) == 4 and i[3].lower() in region_locale.keys():
            target_region = i[3].lower()
        character_info = get_char(name, server, target_region, api_key)
        await client.send_message(message.channel, character_info)
    except Exception as e:
        print(e)
        await client.send_message(message.channel, "Error With Name or Server\n"
                                                   "Use: !pug <name> <server> <region>\n"
                                                   "Hyphenate Two Word Servers (Ex: Twisting-Nether)")
