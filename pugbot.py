import discord
import json

# Commands #
from commands.pug import pug


config = json.loads(open('config.json').read())  # Load Configs
DISCORD_TOKEN = config["discord_token"]
client = discord.Client()


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


@client.event
async def on_message(message):
    if message.content.startswith('!pug'):
        print(str(message.author))
        await pug(client, message)

client.run(DISCORD_TOKEN)
