import discord
from discord.ext import commands
from discord import app_commands
import json
import random
import asyncio

lang = "en_us"
with open(f"lang/{lang}.json", "r", encoding='utf-8') as file:
    label = json.load(file)

class Buttons(discord.ui.View):
    def __init__(self, title = None, description = None, embed = None):
        super().__init__(timeout=None)
        self.members = {}
        self.queue = []
        self.count = 0
        self.title = title
        self.description = description
        self.embed_msg = embed

    # join_
    @discord.ui.button(emoji="🐸", label=f"{label['join_label']}", style=discord.ButtonStyle.grey, custom_id="persistent_view:button_join")
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
        
        if not int(interaction.user.id) in self.queue:
            self.members[self.count] = {"member":int(interaction.user.id)}
            self.queue.append(int(interaction.user.id))
            self.count = self.count + 1

            new_embed = discord.Embed(title=f"{self.title}".title(), description=f"{self.description}".capitalize(), color=discord.Color.from_rgb(47, 49, 54))
            new_embed.set_footer(text=f"{label['join_footer']}: {self.count}")
            await self.embed_msg.edit(embed=new_embed)

            await interaction.response.send_message(f"{label['join_response_1']}", ephemeral=True)   
        elif int(interaction.user.id) in self.queue:
            await interaction.response.send_message(f"{label['join_response_2']}", ephemeral=True)

    @discord.ui.button(emoji="❌", label=f"{label['close_label']}", style=discord.ButtonStyle.grey, custom_id="persistent_view:button_close")
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        #if interaction.user.top_role.position >= 3: #Select roles above one specific to approve
        if "ADM" in str(interaction.user.roles): #Select only one specific role to approve
            await interaction.response.defer()
            await self.embed_msg.delete()

            embed = discord.Embed(title="Random Picker",description=f"{label['close_embed_description']}", color=discord.Color.from_rgb(47, 49, 54))
            await interaction.channel.send(embed=embed)

            with open("cogs/coreano/members.json", "w") as file:
                json.dump(self.members, file, ensure_ascii=False, indent=4)
        else:
            await interaction.response.send_message(f"{label['close_response_1']}", ephemeral=True)
        
class RandomPicker(commands.Cog):
    def __init__(self, client:commands.Bot):
        self.client = client
        #Config
        self.title = f"{label['random_picker_title']}"
        self.description = f"{label['random_picker_description']}"
        self.time = 15
        #Sorteio
        self.already = []
        self.auth = 0
    
    # Config
    @app_commands.command(name="config", description=f"{label['config_command_description']}")
    @app_commands.describe(title=f"{label['config_describe_title']}", description=f"{label['config_describe_description']}", time=f"{label['config_describe_time']}")
    async def config(self, interaction: discord.Interaction, title: str = None, description: str = None, time: int = None):
        attributes = dict(list(locals().items())[2:])
        for k, v in attributes.items():
            if (v) != None:
                vars(self)[k] = v   
        await interaction.response.send_message(f"{label['config_response_1']}", ephemeral=True)

    # Picker
    @app_commands.command(name="picker", description=f"{label['picker_command_description']}")
    @app_commands.describe(title=f"{label['picker_describe_title']}", description=f"{label['picker_describe_description']}")
    async def picker(self, interaction: discord.Interaction, title: str = None, description: str = None):
        if title == "0" or title == None:
            title = self.title
        if description == "0" or description == None:
            description = self.description

        embed = discord.Embed(title=f"{title}".title(), description=f"{description}".capitalize(), color=discord.Color.from_rgb(47, 49, 54))
        embed.set_footer(text=f"{label['picker_footer']}")

        button = Buttons(title=title, description=description)   
        embed_msg = await interaction.channel.send(embed=embed, view=button)
        button.embed_msg = embed_msg

        await interaction.response.send_message(f"{label['picker_response_1']}", ephemeral=True)

    # Raffle
    @app_commands.command(name="raffle", description=f"{label['raffle_command_description']}")
    @app_commands.describe(qty=f"{label['raffle_describe_qty']}", key=f"{label['raffle_describe_key']}")
    async def raffle(self, interaction:discord.Interaction, qty: int, key: str):
        with open ("cogs/coreano/members.json", "r") as file:
            data = json.load(file)

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
            await interaction.response.send_message(f"{label['raffle_response_qty']}: {len(chosen)}\n{label['raffle_response_key']}: {key}",ephemeral=True)
            await interaction.followup.send(f"{label['raffle_response_all']}",ephemeral=True)
            self.auth = 1
        elif len(self.already) == len(data) and self.auth == 1:
            await interaction.response.send_message(f"{label['raffle_response_all']}.",ephemeral=True)
        elif len(self.already) == len(data) and self.auth == 0:
            await interaction.response.send_message(f"{label['raffle_response_qty']}: {len(chosen)}\n{label['raffle_response_key']}: {key}",ephemeral=True)
            await interaction.followup.send(f"{label['raffle_response_all']}.",ephemeral=True)
            self.auth = 1
        else:
            await interaction.response.send_message(f"{label['raffle_response_qty']}: {len(chosen)}\n{label['raffle_response_key']}: {key}",ephemeral=True)

        # Criação do Canal de Texto
        thread = await interaction.channel.create_thread(name=f"{label['raffle_thread_name']}")
        for c in chosen:
            user = await interaction.guild.fetch_member(data[f"{c}"]["member"])
            await thread.add_user(user)
        code = discord.Embed(color=discord.Color.from_rgb(47, 49, 54))
        code.add_field(name="", value=f"{key}")
        msg = await thread.send(f"{label['raffle_thread_warning']}")
        await thread.send(embed=code)
        await msg.edit(content=f"{label['raffle_thread_warning']}")
        for i in range(0, (self.time - 1)):
            await asyncio.sleep(1)
            await msg.edit(content=f"{label['raffle_thread_text']} {self.time-i} {label['raffle_thread_time']}")
        await thread.delete()

async def setup(client:commands.Bot) -> None:
    await client.add_cog(RandomPicker(client))
