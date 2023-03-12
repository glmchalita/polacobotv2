import discord
from discord.ext import commands
from discord import app_commands
import json
import random
import asyncio

class MenuOffline(discord.ui.View):
    def __init__(self, titulo, descricao, msg):
        super().__init__(timeout=None)
        self.value = None
        self.members = {}
        self.count = 0
        self.entry = []
        self.titulo = titulo
        self.descricao = descricao
        self.msg = msg

    @discord.ui.button(label='Participar', style=discord.ButtonStyle.grey, custom_id='persistent_view:button_participar', emoji="🐸")
    async def participar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if int(interaction.user.id) in self.entry:
            await interaction.response.send_message('Você já está participando.', ephemeral=True)
        else:
            self.members[self.count] = {"member":int(interaction.user.id)}
            self.count = self.count + 1
            self.entry.append(int(interaction.user.id))

            embed = discord.Embed(title=f'{self.titulo}'.title(), description=f'{self.descricao}'.capitalize(), color=discord.Color.from_rgb(47, 49, 54))
            embed.set_footer(text=f"Participantes: {self.count}")
            await self.msg.edit(embed=embed)

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
        #config
        self.titulo = "Título"
        self.descricao = "Descrição"
        self.tempo = 15
        #sortear
        self.already = []
        self.auth = 0

            
    # Setup Picker DESCONTINUADO
    @app_commands.command(name='setuppicker', description='Setup para o Random Picker.')
    async def setuppicker(self, interaction: discord.Interaction):
        await interaction.response.send_message("Setup do Random Picker criado com sucesso.", ephemeral=True)
        embed = discord.Embed(title='Random Picker', description='Atualmente o Random Picker está offline, aguarde até um moderador iniciar.', color=discord.Color.from_rgb(47, 49, 54))
        #embed.set_author(icon_url='https://i.imgur.com/fwJ50Qh.png', name='Ponto Automático LBPD')
        await interaction.channel.send(embed=embed, view=MenuOnline())
    
    # Config
    @app_commands.command(name='config', description='Definir opções para o comando Picker')
    @app_commands.describe(titulo='Definir título padrão do /picker', descricao='Definir descrição padrão do /picker', tempo='Definir tempo para resgate (segundos) do /sortear.')
    async def config(self, interaction: discord.Interaction, titulo: str = None, descricao: str = None, tempo: int = None):
        attributes = dict(list(locals().items())[2:])
        for k, v in attributes.items():
            if (v) != None:
                vars(self)[k] = v   
        await interaction.response.send_message(f'Definições padrões atualizadas com sucesso.', ephemeral=True)

    # Picker
    @app_commands.command(name='picker', description='Iniciar o Random Picker.')
    @app_commands.describe(titulo='Título da mensagem', descricao='Descrição da mensagem')
    async def picker(self, interaction: discord.Interaction, titulo: str = None, descricao: str = None):
        if titulo == "0" or titulo == None:
            titulo = self.titulo
        if descricao == "0" or descricao == None:
            descricao = self.descricao
        embed = discord.Embed(title=f'{titulo}'.title(), description=f'{descricao}'.capitalize(), color=discord.Color.from_rgb(47, 49, 54))
        embed.set_footer(text="Participantes: 0")
        msg = await interaction.channel.send(embed=embed)
        await interaction.channel.send(view=MenuOffline(titulo=titulo, descricao=descricao, msg=msg))
        await interaction.response.send_message("Random Picker criado com sucesso.", ephemeral=True)

    # Sortear
    @app_commands.command(name='sortear', description="Criará um canal para as pessoas sorteadas.")
    @app_commands.describe(qtd='Quantidade de membros sorteados.', key='Chave que será sorteada.')
    async def sortear(self, interaction:discord.Interaction, qtd: int, key: str):
        with open ('cogs/coreano/members.json', 'r') as f:
            data = json.load(f)

        # Sortear
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
        #print(f'Chosen: {chosen}\nAlready: {self.already}')

        # Mensagens do Sistema
        if qtd == len(data) and self.auth == 0:
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

        # Criação do Canal de Texto
        thread = await interaction.channel.create_thread(name='sorteio')
        for c in chosen:
            user = await interaction.guild.fetch_member(data[f'{c}']['member'])
            await thread.add_user(user)
        code = discord.Embed(color=discord.Color.from_rgb(47, 49, 54))
        code.add_field(name='', value='CÓDIGO123')
        msg = await thread.send('A sala será deletada em 15 segundos')
        await thread.send(embed=code)
        await msg.edit(content='A sala será deletada em 15 segundos')
        for i in range(0, (self.tempo - 1)):
            await asyncio.sleep(1)
            await msg.edit(content=f'A sala será deletada em {self.tempo-i} segundos')
        await thread.delete()

async def setup(client:commands.Bot) -> None:
    await client.add_cog(RandomPicker(client))
