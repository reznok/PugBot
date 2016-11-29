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

    if message.content.startswith('!info') or message.content.startswith('!help'):
        await client.send_message(message.channel, "I'm PugBot, the pug analyzer!\n"
                                                   "Use: !pug <name> <server> <region> \n"
                                                   "Example: !pug Basimot Lightbringer us")

    if message.content.startswith('!pug'):
        await pug(client, message)

client.run(DISCORD_TOKEN)
