import discord
from discord.ext import commands
from discord import app_commands
import json
import random

class MenuOffline(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.value = None
        self.members = {}
        self.count = 0
        self.entry = []
    
    @discord.ui.button(label='Participar', style=discord.ButtonStyle.grey, custom_id='persistent_view:button_participar', emoji="🐸")
    async def participar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if int(interaction.user.id) in self.entry:
            await interaction.response.send_message('Você já está participando.', ephemeral=True)
        else:
            self.members[self.count] = {"member":int(interaction.user.id)}
            self.count = self.count + 1
            self.entry.append(int(interaction.user.id))
            await interaction.response.send_message('Você entrou pra fila de sorteio.', ephemeral=True)

    @discord.ui.button(label='Encerrar', style=discord.ButtonStyle.grey, custom_id='persistent_view:button_encerrar', emoji="❌")
    async def encerrar(self, interaction: discord.Interaction, button: discord.ui.Button):
        #if "ADM" == str(interaction.user.roles[(len(interaction.user.roles)-1)]): #Select the top role to approve
        #if interaction.user.top_role.position >= 3: #Select roles above one specific to approve
        if "ADM" in str(interaction.user.roles): #Select only one specific role to approve
            await interaction.response.defer()
            await interaction.channel.purge(limit=1)

            embed = discord.Embed(title='Random Picker',description='Tempo para participar esgotado, os administradores irão começar a sortear logo.', color=discord.Color.from_rgb(47, 49, 54))
            await interaction.channel.send(embed=embed)
            with open('cogs/coreano/members.json', 'w') as f:
                json.dump(self.members, f, ensure_ascii=False, indent=4)
        else:
            await interaction.response.send_message('Você não tem permissão para isto.', ephemeral=True)

class MenuOnline(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.value = None

    @discord.ui.button(label='Iniciar', style=discord.ButtonStyle.grey, custom_id='persistent_view:button_menuoffline', emoji="✅")
    async def menu(self, interaction: discord.Interaction, button: discord.ui.Button):
        #if "ADM" == str(interaction.user.roles[(len(interaction.user.roles)-1)]): #Select the top role to approve
        #if interaction.user.top_role.position >= 3: #Select roles above one specific to approve
        if "ADM" in str(interaction.user.roles): #Select only one specific role to approve
            await interaction.response.defer()
            await interaction.channel.purge(limit=1)
            embed = discord.Embed(title='Random Picker', description='Menu Online', color=discord.Color.from_rgb(47, 49, 54))
            await interaction.channel.send(embed=embed, view=MenuOffline())
        else:
            await interaction.response.send_message('Você não tem permissão para isto.', ephemeral=True)

class RandomPicker(commands.Cog):
    def __init__(self, client:commands.Bot):
        self.client = client
        self.already = []
        self.auth = 0

    @app_commands.command(name='setuppicker', description='Setup para o Random Picker.')
    async def setuppicker(self, interaction: discord.Interaction):
        await interaction.response.send_message("Setup do Random Picker criado com sucesso.", ephemeral=True)
        embed = discord.Embed(title='Random Picker', description='Atualmente o Random Picker está offline, aguarde até um moderador iniciar.', color=discord.Color.from_rgb(47, 49, 54))
        #embed.set_author(icon_url='https://i.imgur.com/fwJ50Qh.png', name='Ponto Automático LBPD')
        await interaction.channel.send(embed=embed, view=MenuOnline())

    @app_commands.command(name='picker', description='Iniciar o Random Picker.')
    async def picker(self, interaction: discord.Interaction):
        await interaction.response.send_message("Random Picker criado com sucesso.", ephemeral=True)
        embed = discord.Embed(title='Random Picker', description='Menu Online', color=discord.Color.from_rgb(47, 49, 54))
        await interaction.channel.send(embed=embed, view=MenuOffline())
    
    @app_commands.command(name='sortear', description="Criará um canal com as pessoas sorteadas.")
    @app_commands.describe(qtd='Quantidade que será sorteada.', key='Chave que será sorteada.')
    async def sortear(self, interaction:discord.Interaction, qtd: int, key: str):
        with open ('cogs/coreano/members.json', 'r') as f:
            data = json.load(f)
        
        chosen = []
        for i in range(0, qtd):
            n = random.randint(0, (len(data)-1))
            while n in self.already:
                if len(self.already) == len(data):
                        break
                n = random.randint(0, (len(data)-1))
                while n in chosen:
                    n = random.randint(0, (len(data)-1))
            else:
                chosen.append(n)
                self.already.append(n)

        if qtd == len(data):
            await interaction.response.send_message(f'Quantidade: {len(chosen)}\nChave: {key}',ephemeral=True)
            await interaction.followup.send('Todos participantes sorteados.',ephemeral=True)
            self.auth = 1
        elif len(self.already) == len(data) and self.auth == 1:
            await interaction.response.send_message('Todos participantes sorteados.',ephemeral=True)
        elif len(self.already) == len(data) and self.auth == 0:
            await interaction.response.send_message(f'Quantidade: {len(chosen)}\nChave: {key}',ephemeral=True)
            await interaction.followup.send('Todos participantes sorteados.',ephemeral=True)
            self.auth = 1
        else:
            await interaction.response.send_message(f'Quantidade: {len(chosen)}\nChave: {key}',ephemeral=True)

            
        print(f'Chosen: {chosen}\nAlready: {self.already}')
        for x in chosen:
            print(data[f'{x}']['member'])



async def setup(client:commands.Bot) -> None:
    await client.add_cog(RandomPicker(client))

