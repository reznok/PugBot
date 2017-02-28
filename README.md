#PugBot

PugBot is an open source Discord bot (built off of the amazing work of [discord.py](https://github.com/Rapptz/discord.py)) that gives you a quick glance at a World of Warcraft character. Use it to get a quick summary of any character (like Pugs!).

Example: [Screenshot](https://i.gyazo.com/2be324f099431ebf04e8914a50b98091.png)

## Usage
!pug name server

Example:
!pug Basimot Lightbringer


## Add To Your Server
I (Reznok) am not currently hosting PugBot. Please either self host it, or find someone who is hosting it.
  
If you need help with setup, feel free to message me on reddit ([/u/xeznok](https://www.reddit.com/user/xeznok/)), and I will be happy to help.  
  
If you are hosting PugBot and want to spread the love, submit a PR with your Bot invite link or send me a reddit message, and I'll add him here!

## Configuration
If you want to download PugBot and host him yourself, you will need the following:

+ A Discord Bot Token ([Click Here](https://discordapp.com/developers/applications/))
+ A WoW API Key ([dev.battle.net](https://dev.battle.net))

Add the token and api key to config.json and run pugbot.py

### Docker

Once you have a Discord Bot Token and WoW API Key, simply:

```sh
docker run --name pugbot -e DISCORD_TOKEN=<your token> -e BLIZZARD_API_KEY=<your key> jadametz/wow-pugbot
```

This can be used to run your own PugBot on any laptop or server running [Docker](https://www.docker.com/).
