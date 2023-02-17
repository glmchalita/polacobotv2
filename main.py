import discord
from discord import app_commands
from discord.ext import commands
from colorama import Back, Fore, Style
import cogs.polaco.ponto as ponto
import cogs.polaco.help_center as help_center
import time
import platform 

class Client(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or('.'), intents=discord.Intents.all())
        self.cogslist = ["cogs.coreano.random_picker", "cogs.polaco.help_center"]

    async def setup_hook(self) -> None:
        self.add_view(ponto.Menu())
        self.add_view(help_center.DropdownView())
        for ext in self.cogslist:
            await self.load_extension(ext)

    async def on_ready(self):
        prfx = (Fore.BLACK + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + Back.RESET + Fore.MAGENTA)
        print(prfx + " INFO     Logged in as " + Fore.WHITE + self.user.name)
        print(prfx + " INFO     Bot ID " + Fore.WHITE + str(self.user.id))
        print(prfx + " INFO     Discord.py Version " + Fore.WHITE + discord.__version__)
        print(prfx + " INFO     Python Version " + Fore.WHITE + str(platform.python_version()))
        synced = await self.tree.sync()
        print(prfx + " INFO     Slash CMDs Synced " + Fore.WHITE + str(len(synced)) + " Commands")

client = Client()

@client.tree.command(name="loadcog")
async def loadcog(interaction: discord.Interaction, cog: str):
    await client.load_extension(cog)
    await interaction.response.send_message(content=f"{cog} carregado com sucesso.", ephemeral=True)

@client.tree.command(name="reloadcog")
async def reloadcog(interaction: discord.Interaction, cog: str):
    await client.reload_extension(cog)
    await interaction.response.send_message(content=f"{cog} recarregado com sucesso.", ephemeral=True)

@client.tree.command(name="unloadcog")
async def unloadcog(interaction: discord.Interaction, cog: str):
    await client.unload_extension(cog)
    await interaction.response.send_message(content=f"{cog} descarregado com sucesso.", ephemeral=True)

with open("token.txt", "r") as f:
    lines = f.readlines()
    TOKEN = lines[0].strip()
client.run(TOKEN)