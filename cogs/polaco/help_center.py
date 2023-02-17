import discord
from discord.ext import commands
from discord import app_commands

class Dropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(value="ajuda",label="Ajuda", emoji="👋"),
            discord.SelectOption(value="atendimento",label="Atendimento", emoji="📨"),
        ]
        super().__init__(
            placeholder="Selecione uma opção...",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="persistent_view:dropdown_help"
        )
    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "ajuda":
            await interaction.response.send_message("Se você precisar de ajuda, coloque nos comentários do vídeo",ephemeral=True)
        elif self.values[0] == "atendimento":
            await interaction.response.send_message("Clique abaixo para criar um ticket",ephemeral=True,view=CreateTicket())

class DropdownView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

        self.add_item(Dropdown())

class CreateTicket(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)
        self.value = None

    @discord.ui.button(label="Abrir Ticket", style=discord.ButtonStyle.blurple, emoji="➕")
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = True
        self.stop()

        ticket = None
        for thread in interaction.channel.threads:
            if f"{interaction.user.id}" in thread.name:
                if thread.archived:
                    ticket = thread
                else:
                    await interaction.response.send_message(ephemeral=True, content=f"Você já tem um atendimento em andamento!")
                    return

        async for thread in interaction.channel.archived_threads(private=True):
            if f"{interaction.user.id}" in thread.name:
                if thread.archived:
                    ticket = thread
                else:
                    await interaction.edit_original_response(content=f"Você já tem um atendimento em andamento!", view=None)
                    return

        if ticket != None:
            await ticket.edit(archived=False)
            await ticket.edit(name=f"{interaction.user.name} ({interaction.user.id})", auto_archive_duration=10080, invitable=False)
        else:
            ticket = await interaction.channel.create_thread(name=f"{interaction.user.name} ({interaction.user.id})",
                                                             auto_archive_duration=10080)  # ,type=discord.ChannelType.public_thread)
            await ticket.edit(invitable=False)

        await interaction.response.send_message(ephemeral=True, content=f"Criei um ticket para você! {ticket.mention}")
        await ticket.send(
            f"📩  **|** {interaction.user.mention} ticket criado! Envie todas as informações possíveis sobre seu caso e aguarde até que um atendente responda.\n\nApós a sua questão ser sanada, você pode usar `/fecharticket` para encerrar o atendimento!")

class HelpCenter(commands.Cog):
    def __init__(self, client:commands.Bot):
        self.client = client
        self.adm_id = 1015784676725633025
    
    @app_commands.command(name='setupcenter', description='Setup do menu Help Center.')
    @commands.has_permissions(manage_guild=True)
    async def setupcenter(self, interaction: discord.Interaction):
        await interaction.response.send_message("Mensagem do painel", ephemeral=True)

        help_center = discord.Embed(title="Central de Suporte da FIAP", description="Aqui você pode tirar dúvidas ou entrar em contato com a nossa equipe para assuntos em específico.\n\nPara evitar problemas, leia com atençãoas instruções passadas ao selecionar alguma opção.",color=discord.Color.blurple())
        help_center.set_image(url="https://www.fiap.com.br/wp-content/themes/fiap2016/images/sharing/fiap.png")
        await interaction.channel.send(embed=help_center, view=DropdownView())

    @app_commands.command(name="fecharticket",description='Feche um atendimento atual.')
    async def _fecharticket(self, interaction: discord.Interaction):
        mod = interaction.guild.get_role(self.adm_id)
        if str(interaction.user.id) in interaction.channel.name or mod in interaction.author.roles:
            await interaction.response.send_message(f"O ticket foi arquivado por {interaction.user.mention}, obrigado por entrar em contato!")
            await interaction.channel.edit(archived=True)
        else:
            await interaction.response.send_message("Isso não pode ser feito aqui...")

async def setup(client:commands.Bot) -> None:
    await client.add_cog(HelpCenter(client))

