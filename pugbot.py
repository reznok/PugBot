import json
import os

import discord

# Commands #
from commands.pug import pug

CLIENT = discord.Client()


def config_value(key):
    with open(os.path.join(os.path.dirname(__file__), 'config.json')) as config_file:
        config = json.load(config_file)

    try:
        value = os.environ[key.upper()]
    except KeyError:
        value = config.get(key)
    return value


@CLIENT.event
async def on_ready():
    print('Logged in as')
    print(CLIENT.user.name)
    print(CLIENT.user.id)
    print('------')


@CLIENT.event
async def on_message(message):

    if message.content.startswith('!info') or message.content.startswith('!help'):
        await CLIENT.send_message(message.channel, "I'm PugBot, the pug analyzer!\n"
                                                   "Use: !pug <name> <server> <region> \n"
                                                   "Example: !pug Basimot Lightbringer us")

    if message.content.startswith('!pug'):
        await pug(CLIENT, DEFAULT_REGION, BLIZZARD_API_KEY, message)


if __name__ == '__main__':
    BLIZZARD_API_KEY = config_value('blizzard_api_key')
    DEFAULT_REGION = config_value('default_region')
    DISCORD_TOKEN = config_value('discord_token')
    CLIENT.run(DISCORD_TOKEN)
