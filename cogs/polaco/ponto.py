import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timedelta
from pytz import timezone

class Menu(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.value = None

    @discord.ui.button(label='Iniciar/Fechar turno', style=discord.ButtonStyle.grey, custom_id='persistent_view:button_turno')
    async def menu(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        await interaction.channel.purge(limit=1)

        ponto = discord.Embed(description='Reaja para **INICIAR** / **ENCERAR** seu turno', color=discord.Color.from_rgb(47, 49, 54))
        ponto.set_author(icon_url='https://i.imgur.com/fwJ50Qh.png', name='Ponto Automático LBPD')

        # Entrada
        hora = datetime.now(timezone('Brazil/East')).strftime("%H:%M:%S")
        entrada = discord.Embed(description=f'`ENTRADA` {hora[0:5]}\n`TRABALHANDO NO MOMENTO`', color=discord.Color.from_rgb(255, 204, 0))
        entrada.set_author(name=f'{interaction.user.name}', icon_url=interaction.user.avatar)

        await interaction.channel.send(embed=entrada)
        await interaction.channel.send(embed=ponto, view=Menu())

class Ponto(commands.Cog):
    def __init__(self, client:commands.Bot):
        self.client = client

    @app_commands.command(name='setupponto', description='Setup do menu Ponto.')
    async def setupponto(self, interaction: discord.Interaction):
        await interaction.response.send_message("Painel do Ponto Automático criado.", ephemeral=True)

        embed = discord.Embed(description='Reaja para **INICIAR** / **ENCERAR** seu turno', color=discord.Color.from_rgb(47, 49, 54))
        embed.set_author(icon_url='https://i.imgur.com/fwJ50Qh.png', name='Ponto Automático LBPD')

        await interaction.channel.send(embed=embed, view=Menu())

async def setup(client:commands.Bot) -> None:
    await client.add_cog(Ponto(client))

