import discord
from discord import app_commands
from discord.ext import commands
from colorama import init, Back, Fore, Style
import cogs.polaco.ponto as ponto
import cogs.polaco.help_center as help_center
import cogs.coreano.random_picker as random
import time
import platform
import json

# Colorama
init(convert=True)

class Client(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or("."), intents=discord.Intents.all())
        self.cogslist = ["cogs.coreano.random_picker"]

    async def setup_hook(self) -> None:
        self.add_view(ponto.Menu())
        self.add_view(help_center.DropdownView())
        for ext in self.cogslist:
            await self.load_extension(ext)

    async def on_ready(self):
        prfx = (Fore.BLACK + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + Back.RESET + Fore.MAGENTA)
        print("[" + prfx + "] [INFO    ] Logged in as " + Fore.WHITE + self.user.name)
        print("[" + prfx + "] [INFO    ] Bot ID " + Fore.WHITE + str(self.user.id))
        print("[" + prfx + "] [INFO    ] Discord.py Version " + Fore.WHITE + discord.__version__)
        print("[" + prfx + "] [INFO    ] Python Version " + Fore.WHITE + str(platform.python_version()))
        synced = await self.tree.sync()
        print("[" + prfx + "] [INFO    ] Slash CMDs Synced " + Fore.WHITE + str(len(synced)) + " Commands")

client = Client()

with open("config.json", "r") as f:
    data = json.load(f)
    TOKEN = data["TOKEN"]

client.run(TOKEN)