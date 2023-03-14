import discord
from discord.ext import commands
from discord import app_commands
import json
import random
import asyncio

class Buttons(discord.ui.View):
    def __init__(self, title = None, description = None, embed = None):
        super().__init__(timeout=None)
        self.members = {}
        self.queue = []
        self.count = 0
        self.title = title
        self.description = description
        self.embed_msg = embed

    @discord.ui.button(emoji="🐸", label="Participar", style=discord.ButtonStyle.grey, custom_id="persistent_view:button_join")
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
        
        if not int(interaction.user.id) in self.queue:
            self.members[self.count] = {"member":int(interaction.user.id)}
            self.queue.append(int(interaction.user.id))
            self.count = self.count + 1

            new_embed = discord.Embed(title=f"{self.title}".title(), description=f"{self.description}".capitalize(), color=discord.Color.from_rgb(47, 49, 54))
            new_embed.set_footer(text=f"Participantes: {self.count}")
            await self.embed_msg.edit(embed=new_embed)

            await interaction.response.send_message("Você entrou pra fila de sorteio.", ephemeral=True)   
        elif int(interaction.user.id) in self.queue:
            await interaction.response.send_message("Você já está participando.", ephemeral=True)

    @discord.ui.button(emoji="❌", label="Encerrar", style=discord.ButtonStyle.grey, custom_id="persistent_view:button_close")
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        #if interaction.user.top_role.position >= 3: #Select roles above one specific to approve
        if "ADM" in str(interaction.user.roles): #Select only one specific role to approve
            await interaction.response.defer()
            await self.embed_msg.delete()

            embed = discord.Embed(title="Random Picker",description="Tempo para participar esgotado, os administradores irão começar a sortear logo.", color=discord.Color.from_rgb(47, 49, 54))
            await interaction.channel.send(embed=embed)

            with open("cogs/coreano/members.json", "w") as file:
                json.dump(self.members, file, ensure_ascii=False, indent=4)
        else:
            await interaction.response.send_message("Você não tem permissão para isto.", ephemeral=True)
        
class RandomPicker(commands.Cog):
    def __init__(self, client:commands.Bot):
        self.client = client
        #Config
        self.title = "Título"
        self.description = "Descrição"
        self.tempo = 15
        #Sorteio
        self.already = []
        self.auth = 0
    
    # Config
    @app_commands.command(name="config", description="Definir opções para o comando Picker")
    @app_commands.describe(title="Definir título padrão do /picker", description="Definir descrição padrão do /picker", tempo="Definir tempo para resgate (segundos) do /sortear.")
    async def config(self, interaction: discord.Interaction, title: str = None, description: str = None, tempo: int = None):
        attributes = dict(list(locals().items())[2:])
        for k, v in attributes.items():
            if (v) != None:
                vars(self)[k] = v   
        await interaction.response.send_message(f"Definições padrões atualizadas com sucesso.", ephemeral=True)

    # Picker
    @app_commands.command(name="picker", description="Iniciar o Random Picker.")
    @app_commands.describe(title="Título da mensagem", description="Descrição da mensagem")
    async def picker(self, interaction: discord.Interaction, title: str = None, description: str = None):
        if title == "0" or title == None:
            title = self.title
        if description == "0" or description == None:
            description = self.description

        embed = discord.Embed(title=f"{title}".title(), description=f"{description}".capitalize(), color=discord.Color.from_rgb(47, 49, 54))
        embed.set_footer(text="Participantes: 0")

        button = Buttons(title=title, description=description)   
        embed_msg = await interaction.channel.send(embed=embed, view=button)
        button.embed_msg = embed_msg

        await interaction.response.send_message("Random Picker criado com sucesso.", ephemeral=True)

    # Sortear
    @app_commands.command(name="sortear", description="Criará um canal para as pessoas sorteadas.")
    @app_commands.describe(qty="Quantidade de membros sorteados.", key="Chave que será sorteada.")
    async def sortear(self, interaction:discord.Interaction, qty: int, key: str):
        with open ("cogs/coreano/members.json", "r") as f:
            data = json.load(f)

        # Sorteio
        chosen = []
        for i in range(0, qty):
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

        # Mensagens do Sistema
        if qty == len(data) and self.auth == 0:
            await interaction.response.send_message(f"Quantidade: {len(chosen)}\Código: {key}",ephemeral=True)
            await interaction.followup.send("Todos participantes sorteados.",ephemeral=True)
            self.auth = 1
        elif len(self.already) == len(data) and self.auth == 1:
            await interaction.response.send_message("Todos participantes sorteados.",ephemeral=True)
        elif len(self.already) == len(data) and self.auth == 0:
            await interaction.response.send_message(f"Quantidade: {len(chosen)}\Código: {key}",ephemeral=True)
            await interaction.followup.send("Todos participantes sorteados.",ephemeral=True)
            self.auth = 1
        else:
            await interaction.response.send_message(f"Quantidade: {len(chosen)}\Código: {key}",ephemeral=True)

        # Criação do Canal de Texto
        thread = await interaction.channel.create_thread(name="sorteio")
        for c in chosen:
            user = await interaction.guild.fetch_member(data[f"{c}"]["member"])
            await thread.add_user(user)
        code = discord.Embed(color=discord.Color.from_rgb(47, 49, 54))
        code.add_field(name="", value="CÓDIGO123")
        msg = await thread.send("A sala será deletada em 15 segundos")
        await thread.send(embed=code)
        await msg.edit(content="A sala será deletada em 15 segundos")
        for i in range(0, (self.tempo - 1)):
            await asyncio.sleep(1)
            await msg.edit(content=f"A sala será deletada em {self.tempo-i} segundos")
        await thread.delete()

async def setup(client:commands.Bot) -> None:
    await client.add_cog(RandomPicker(client))
