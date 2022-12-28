"""
hello everyone, piracy/undaunted here
looking through this, you will realise that im a total python noob
im learning, and i recently came across this old lil' project i had worked on in september(ish)
decided it to os it so that others who are learning (like me) are able to see how i did what i did
but dont stop here guys, theres always room for improvement
even months later i already see the amounts of changes/overhauls i can make to this code, firstly by putting this mess into cogs
this file is a monster of a file

READ THIS !!!

ya'll gotta pipi poopoo install the following:

pycord
captcha
chat_exporter (for reports)

eg. pip install pycord

1. add the following channels in ur discord: 
(all public channels) -> buying, selling, trading, hiring, ads
(all mod-related channels) -> post-moderation, post-logs, case-logs

2. edit the variaiaiaiables right under the triple lipple tipple quotations

3. run (for your life) main.py

yummy
"""

# bot token
super_secret_launch_code = ""

# vetting channel (post-moderation) -> this is the channel the bot will send listings to for moderation/approval
vet = 0

# audit channel (post-logs) - > this is the channel the bot will audit all listings, eg. log whether they are rejected/approved by a moderator
audit = 0

# case channel (case-logs) -> this is where all cases will go, eg. when a case is concluded (after someone runs the /report commands, keep the ppl safe yk yk yk)
cascl = 0

# all these channels are the public channels, i.e. the ones that listings will be sent to if approved - ususally recommended that users CANNOT speak here lol mute them ez pz
buy_id = 0
sell_id = 0
trade_id = 0
hire_id = 0
ads_id = 0

# this is the channel, usually bot commands, where the bot will inform a user that their listing was rejected
cmds_id = 0

# staff id's (ROLE IDS NOT CHANNEL IDS)
moderator = 0 # post moderator - approve/deny whateverrr
judge = 0 # the ppl who handle reports!!!

# verification roles
member_joiner = 0 # this role is the role given to users who join, they will be required to run the command /verify in order to gain full access to your server
member_completed = 0 # this is the role give to users who complete the captcha (/verify) and have full access

# some branding if u ugys want idrc pls credit thxn
logo_small = "https://cdn.discordapp.com/attachments/1011603516911005757/1012242235674337290/diverr_2.png"
logo_big = "https://cdn.discordapp.com/attachments/1009750661094723594/1009751860124590150/diverr_2.png"

uni_colour = 0x0077e6 # embed colour

import discord
import random
import asyncio
import os
import chat_exporter
import io
from discord import option
from discord.ext import commands
from captcha.image import ImageCaptcha

# discord intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# diverr creation
bot = commands.Bot(command_prefix=f"diverr", intents=intents)

# the good morninger
@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="business! 💼"))
    print("A very good morning... to youuuuuuu! gm bbg")

# welcome + add roles
@bot.event
async def on_member_join(member: discord.Member):
    guild = member.guild
    verification_role = guild.get_role(member_joiner)
    await member.add_roles(verification_role)

# verification command
@bot.slash_command(name='verify', description='Verify your account so you can post!')
async def verify(ctx):

    verified_role = ctx.guild.get_role(member_completed)
    verification_role = ctx.guild.get_role(member_joiner)

    if verified_role in ctx.author.roles:
        await ctx.respond(f"You are already verified!", ephemeral=True)

    else:
        code = random.randrange(11111, 55555, 5)

        image = ImageCaptcha(width = 250, height = 90)
        captcha_text = f'{code}' 
        image.generate(captcha_text) 
        image.write(captcha_text, f'{ctx.author.id}.png')

        embed=discord.Embed(title="Diverr Automation here!", description=f"It seems that you, {ctx.author}, want to verify! We've generated a captcha for you! Just type out what you see in the image below!", color=0x0077e6)
        embed.set_thumbnail(url=logo_small)
        file = discord.File(f"{os.getcwd()}/{ctx.author.id}.png", filename=f"{ctx.author.id}.png")
        embed.set_image(url=f"attachment://{ctx.author.id}.png")
        embed.set_footer(text="Diverr 2022 | Online Marketplace | Process will be cancelled in 15 seconds")
            
        await ctx.respond(file=file, embed=embed, ephemeral=True)

        def check(m: discord.Message):
            return m.author == ctx.author and m.content.isdigit()

        try:
            msg = await bot.wait_for('message', check = check, timeout = 15.0)

        except asyncio.TimeoutError: 
            await ctx.respond(f"{ctx.author.mention}, you either entered the wrong code or took too long to respond! Try again!", ephemeral=True)
            return

        else:
            if msg.content == f"{code}":

                await msg.delete()

                embed1=discord.Embed(title="Verified", description="Welcome to Diverr, the free, online marketplace!", color=0x0077e6)
                embed1.set_thumbnail(url=logo_small)
                embed1.add_field(name="Username", value=f"{ctx.author.mention}", inline=True)
                embed1.add_field(name="User ID", value=f"{ctx.author.id}", inline=True)
                embed1.set_footer(text="Diverr 2022 | Free Online Marketplace | Get your information by using the /userinfo command!")

                await ctx.author.remove_roles(verification_role)
                await ctx.author.add_roles(verified_role)
                await ctx.respond(embed=embed1, ephemeral=True)

# -- BUY COMMAND --
@bot.slash_command(name="buy", description="Send out a listing to buy something!")
@option(
    "title", 
    description="Provide the title of your post.", 
    required=True)
@option(
    "description", 
    description='What are you buying?', 
    required=True)
@option(
    "pay", 
    description="What are you paying? Specify the amount in the next option.", 
    choices=["USD", "Discord Nitro", "Discord Nitro Classic", "Crypto"])
@option(
    "amount",
    description="If you are paying USD, how much are you paying? (put any amount if you are paying via nitro)",
    required=True
)
@option(
    'date', 
    description='When do you need this buy?', 
    required=False)
@option(
    "image",
    discord.Attachment,
    description="Upload an image.",
    required=False  # The default value will be None if the user doesn't provide a file.
)
async def buy(
    ctx: discord.ApplicationContext,
    title: str,
    description: str,
    pay: str,
    amount: float,
    date: str,
    image: discord.Attachment):

    imageprovided = True
    dateprovided = True

    if pay == "USD":
        pay_value = f"**USD** ($) {amount}"
    if pay == "Discord Nitro":
        pay_value = pay
    if pay == "Discord Nitro Classic":
        pay_value = pay
    if pay == "Crypto":
        pay_value = f"**CRYPTO** (₿) {amount}"

    if date == None:
        dateprovided = False

    if image == None:
        imageprovided = False

    buy=discord.Embed(title=f"{title}", description=f"{description}", color=uni_colour)
    buy.set_author(name=f"{ctx.author}", icon_url=f"{ctx.author.avatar}")
    buy.set_thumbnail(url=logo_small)
    buy.add_field(name="Payment Type", value=f"{pay_value}", inline=False)
    buy.add_field(name="Contact", value=f"Discord {ctx.author.mention}", inline=False)

    if dateprovided == True:
        buy.add_field(name="Needed By", value=f"{date}", inline=False)

    if imageprovided == True:
        buy.set_image(url=f"{image.url}")

    buy.set_footer(text=f"Diverr 2022 | Online Marketplace | ID {ctx.author.id}")

    class ReviewView(discord.ui.View):

        @discord.ui.button(label="Yes", style=discord.ButtonStyle.green, custom_id="reviewview:green")
        async def yes(self, button: discord.ui.Button, interaction: discord.Interaction):
            for child in self.children: # loop through all the children of the view
                child.disabled = True # set the button to disabled
            await interaction.response.edit_message(view=self)
                
            await ctx.respond("Alright, I've sent this listing for approval!", ephemeral=True)

            channel = bot.get_channel(vet)
            buying_channel = bot.get_channel(buy_id)

            vetting_channel = bot.get_channel(audit) # post auds

            class PersistentView(discord.ui.View):
                def __init__(self):
                    super().__init__(timeout=None)

                @discord.ui.button(label="Accept", style=discord.ButtonStyle.green, custom_id="persistent_view:green")
                async def accept(self, button: discord.ui.Button, interaction: discord.Interaction):
                    await interaction.response.send_message("Sent the listing!", ephemeral=True)
                    await buying_channel.send(f"{ctx.author.mention}", embed=buy)
                    await vetting_channel.send(f"{interaction.user.mention} **accepted** a `buying` post by {ctx.author.mention}", embed=buy)
                    await nice.delete()

                @discord.ui.button(label="Decline", style=discord.ButtonStyle.red, custom_id="persistent_view:red")
                async def deny(self, button: discord.ui.Button, interaction: discord.Interaction):
                    await interaction.response.send_message("Declined the listing!", ephemeral=True)
                    await vetting_channel.send(f"{interaction.user.mention} **denied** a `buying` post by {ctx.author.mention}", embed=buy)
                    await nice.delete()
                    try:
                        rejectionembed=discord.Embed(title="Your listing was rejected!", description=f"Your listing, '{title}', was rejected", color=0xdf2626)
                        rejectionembed.add_field(name="Confused? Contact the marketplace staff that rejected your listing!", value=f"{interaction.user.mention}", inline=False)
                        rejectionembed.set_thumbnail(url=logo_small)
                        await ctx.author.dm_channel.send(embed=rejectionembed)
                    except:
                        informchannel = bot.get_channel(cmds_id)
                        await informchannel.send(f"{ctx.author.mention}, your listing, '{title}', was rejected by {interaction.user.mention}!")
                        print("L")

            nice = await channel.send(f"There is a new post request <@&{moderator}>!", embed=buy, view=PersistentView())

        @discord.ui.button(label="No", style=discord.ButtonStyle.red, custom_id="reviewview:red")
        async def no(self, button: discord.ui.Button, interaction: discord.Interaction):
            for child in self.children: # loop through all the children of the view
                child.disabled = True # set the button to disabled
            await interaction.response.edit_message(view=self)
            
            await interaction.response.send_message("Alright, cancelled the listing!", ephemeral=True)

    await ctx.respond(f"{ctx.author.mention}, are you sure you want to send this listing for approval?", embed=buy, view=ReviewView(), ephemeral=True)

# -- SELL COMMAND --
@bot.slash_command(name="sell", description="Send out a listing to sell something!")
@option(
    "title", 
    description="Provide the title of your post.", 
    required=True)
@option(
    "description", 
    description='What are you selling?', 
    required=True)
@option(
    "pay", 
    description="What payment type do you accept? Specify the amount in the next option.", 
    choices=["USD", "Discord Nitro", "Discord Nitro Classic", "Crypto"])
@option(
    "price",
    description="How much are you selling this for?",
    required=True
)
@option(
    'date', 
    description='When are you selling this?', 
    required=False)
@option(
    "image",
    discord.Attachment,
    description="Upload an image.",
    required=False  # The default value will be None if the user doesn't provide a file.
)
async def sell(
    ctx: discord.ApplicationContext,
    title: str,
    description: str,
    pay: str,
    price: float,
    date: str,
    image: discord.Attachment):

    imageprovided = True
    dateprovided = True

    if pay == "USD":
        pay_value = f"**USD** ($) {price}"
    if pay == "Discord Nitro":
        pay_value = pay
    if pay == "Discord Nitro Classic":
        pay_value = pay
    if pay == "Crypto":
        pay_value = f"**CRYPTO** (₿) {price}"

    if date == None:
        dateprovided = False

    if image == None:
        imageprovided = False

    buy=discord.Embed(title=f"{title}", description=f"{description}", color=uni_colour)
    buy.set_author(name=f"{ctx.author}", icon_url=f"{ctx.author.avatar}")
    buy.set_thumbnail(url=logo_small)
    buy.add_field(name="Price", value=f"{pay_value}", inline=False)
    buy.add_field(name="Contact", value=f"Discord {ctx.author.mention}", inline=False)

    if dateprovided == True:
        buy.add_field(name="Needed By", value=f"{date}", inline=False)

    if imageprovided == True:
        buy.set_image(url=f"{image.url}")

    buy.set_footer(text=f"Diverr 2022 | Online Marketplace | ID {ctx.author.id}")

    class ReviewView(discord.ui.View):

        @discord.ui.button(label="Yes", style=discord.ButtonStyle.green, custom_id="reviewview:green")
        async def yes(self, button: discord.ui.Button, interaction: discord.Interaction):
            for child in self.children: # loop through all the children of the view
                child.disabled = True # set the button to disabled
            await interaction.response.edit_message(view=self)
                
            await ctx.respond("Alright, I've sent this listing for approval!", ephemeral=True)

            channel = bot.get_channel(vet)
            buying_channel = bot.get_channel(sell_id)

            vetting_channel = bot.get_channel(audit) # post auds

            class PersistentView(discord.ui.View):
                def __init__(self):
                    super().__init__(timeout=None)

                @discord.ui.button(label="Accept", style=discord.ButtonStyle.green, custom_id="persistent_view:green")
                async def accept(self, button: discord.ui.Button, interaction: discord.Interaction):
                    await interaction.response.send_message("Sent the listing!", ephemeral=True)
                    await buying_channel.send(f"{ctx.author.mention}", embed=buy)
                    await vetting_channel.send(f"{interaction.user.mention} **accepted** a `selling` post by {ctx.author.mention}", embed=buy)
                    await nice.delete()

                @discord.ui.button(label="Decline", style=discord.ButtonStyle.red, custom_id="persistent_view:red")
                async def deny(self, button: discord.ui.Button, interaction: discord.Interaction):
                    await interaction.response.send_message("Declined the listing!", ephemeral=True)
                    await vetting_channel.send(f"{interaction.user.mention} **denied** a `selling` post by {ctx.author.mention}", embed=buy)
                    await nice.delete()
                    try:
                        rejectionembed=discord.Embed(title="Your listing was rejected!", description=f"Your listing, '{title}', was rejected", color=0xdf2626)
                        rejectionembed.add_field(name="Confused? Contact the marketplace staff that rejected your listing!", value=f"{interaction.user.mention}", inline=False)
                        rejectionembed.set_thumbnail(url=logo_small)
                        await ctx.author.dm_channel.send(embed=rejectionembed)
                    except:
                        informchannel = bot.get_channel(cmds_id)
                        await informchannel.send(f"{ctx.author.mention}, your listing, '{title}', was rejected by {interaction.user.mention}!")
                        print("L")

            nice = await channel.send(f"There is a new post request <@&{moderator}>!", embed=buy, view=PersistentView())

        @discord.ui.button(label="No", style=discord.ButtonStyle.red, custom_id="reviewview:red")
        async def no(self, button: discord.ui.Button, interaction: discord.Interaction):
            for child in self.children: # loop through all the children of the view
                child.disabled = True # set the button to disabled
            await interaction.response.edit_message(view=self)
            
            await interaction.response.send_message("Alright, cancelled the listing!", ephemeral=True)

    await ctx.respond(f"{ctx.author.mention}, are you sure you want to send this listing for approval?", embed=buy, view=ReviewView(), ephemeral=True)

# -- TRADE COMMAND --
@bot.slash_command(name="trade", description="Send out a listing to trade something!")
@option(
    "title", 
    description="Provide the title of your post.", 
    required=True)
@option(
    "description", 
    description='What are you trading? (Include notes, wishes, etc.)', 
    required=True)
@option(
    "trade", 
    description="What are you looking for in return?", 
    required=True)
@option(
    'date', 
    description='When are you looking to commit to the trade?', 
    required=False)
@option(
    "image",
    discord.Attachment,
    description="Upload an image.",
    required=False  # The default value will be None if the user doesn't provide a file.
)
async def trade(
    ctx: discord.ApplicationContext,
    title: str,
    description: str,
    trade: str,
    date: str,
    image: discord.Attachment):

    imageprovided = True
    dateprovided = True

    if date == None:
        dateprovided = False

    if image == None:
        imageprovided = False

    buy=discord.Embed(title=f"{title}", description=f"{description}", color=uni_colour)
    buy.set_author(name=f"{ctx.author}", icon_url=f"{ctx.author.avatar}")
    buy.set_thumbnail(url=logo_small)
    buy.add_field(name=f"{ctx.author} wants in return", value=f"{trade}", inline=False)
    buy.add_field(name="Contact", value=f"Discord {ctx.author.mention}", inline=False)

    if dateprovided == True:
        buy.add_field(name="Needed By", value=f"{date}", inline=False)

    if imageprovided == True:
        buy.set_image(url=f"{image.url}")

    buy.set_footer(text=f"Diverr 2022 | Online Marketplace | ID {ctx.author.id}")

    class ReviewView(discord.ui.View):

        @discord.ui.button(label="Yes", style=discord.ButtonStyle.green, custom_id="reviewview:green")
        async def yes(self, button: discord.ui.Button, interaction: discord.Interaction):
            for child in self.children: # loop through all the children of the view
                child.disabled = True # set the button to disabled
            await interaction.response.edit_message(view=self)
                
            await ctx.respond("Alright, I've sent this listing for approval!", ephemeral=True)

            channel = bot.get_channel(vet) # xx-request
            buying_channel = bot.get_channel(trade_id) # xx-post

            vetting_channel = bot.get_channel(audit) # xx-postauds

            class PersistentView(discord.ui.View):
                def __init__(self):
                    super().__init__(timeout=None)

                @discord.ui.button(label="Accept", style=discord.ButtonStyle.green, custom_id="persistent_view:green")
                async def accept(self, button: discord.ui.Button, interaction: discord.Interaction):
                    await interaction.response.send_message("Sent the listing!", ephemeral=True)
                    await buying_channel.send(f"{ctx.author.mention}", embed=buy)
                    await vetting_channel.send(f"{interaction.user.mention} **accepted** a `trading` post by {ctx.author.mention}", embed=buy)
                    await nice.delete()

                @discord.ui.button(label="Decline", style=discord.ButtonStyle.red, custom_id="persistent_view:red")
                async def deny(self, button: discord.ui.Button, interaction: discord.Interaction):
                    await interaction.response.send_message("Declined the listing!", ephemeral=True)
                    await vetting_channel.send(f"{interaction.user.mention} **denied** a `trading` post by {ctx.author.mention}", embed=buy)
                    await nice.delete()
                    try:
                        rejectionembed=discord.Embed(title="Your listing was rejected!", description=f"Your listing, '{title}', was rejected", color=0xdf2626)
                        rejectionembed.add_field(name="Confused? Contact the marketplace staff that rejected your listing!", value=f"{interaction.user.mention}", inline=False)
                        rejectionembed.set_thumbnail(url=logo_small)
                        await ctx.author.dm_channel.send(embed=rejectionembed)
                    except:
                        informchannel = bot.get_channel(cmds_id)
                        await informchannel.send(f"{ctx.author.mention}, your listing, '{title}', was rejected by {interaction.user.mention}!")
                        print("L")

            nice = await channel.send(f"There is a new post request <@&{moderator}>!", embed=buy, view=PersistentView())

        @discord.ui.button(label="No", style=discord.ButtonStyle.red, custom_id="reviewview:red")
        async def no(self, button: discord.ui.Button, interaction: discord.Interaction):
            for child in self.children: # loop through all the children of the view
                child.disabled = True # set the button to disabled
            await interaction.response.edit_message(view=self)
            
            await interaction.response.send_message("Alright, cancelled the listing!", ephemeral=True)

    await ctx.respond(f"{ctx.author.mention}, are you sure you want to send this listing for approval?", embed=buy, view=ReviewView(), ephemeral=True)

# -- HIRE COMMAND --
@bot.slash_command(name="hire", description="Send out a listing to hire people!")
@option(
    "title", 
    description="Provide the title of your post.", 
    required=True)
@option(
    "description", 
    description='What are you hiring people for?', 
    required=True)
@option(
    "pay", 
    description="What are you paying? Specify the amount in the next option.", 
    choices=["USD", "Discord Nitro", "Discord Nitro Classic", "Crypto"])
@option(
    "amount",
    description="If you are paying USD, how much are you paying? (put any amount if you are paying via nitro)",
    required=True
)
@option(
    "amount of people",
    description="How many people are you hiring?",
    required=True
)
@option(
    'date', 
    description='When do you need this buy?', 
    required=False)
@option(
    "image",
    discord.Attachment,
    description="Upload an image.",
    required=False  # The default value will be None if the user doesn't provide a file.
)
async def hire(
    ctx: discord.ApplicationContext,
    title: str,
    description: str,
    pay: str,
    amount: float,
    amount_of_people: str,
    date: str,
    image: discord.Attachment):

    imageprovided = True
    dateprovided = True

    if pay == "USD":
        pay_value = f"**USD** ($) {amount}"
    if pay == "Discord Nitro":
        pay_value = pay
    if pay == "Discord Nitro Classic":
        pay_value = pay
    if pay == "Crypto":
        pay_value = f"**CRYPTO** (₿) {amount}"

    if date == None:
        dateprovided = False

    if image == None:
        imageprovided = False

    buy=discord.Embed(title=f"{title}", description=f"{description}", color=uni_colour)
    buy.set_author(name=f"{ctx.author}", icon_url=f"{ctx.author.avatar}")
    buy.set_thumbnail(url=logo_small)
    buy.add_field(name="Payment Type", value=f"{pay_value}", inline=False)
    buy.add_field(name="# of People Needed", value=f"{amount_of_people}", inline=False)
    buy.add_field(name="Contact", value=f"Discord {ctx.author.mention}", inline=False)

    if dateprovided == True:
        buy.add_field(name="Needed By", value=f"{date}", inline=False)

    if imageprovided == True:
        buy.set_image(url=f"{image.url}")

    buy.set_footer(text=f"Diverr 2022 | Online Marketplace | ID {ctx.author.id}")

    class ReviewView(discord.ui.View):

        @discord.ui.button(label="Yes", style=discord.ButtonStyle.green, custom_id="reviewview:green")
        async def yes(self, button: discord.ui.Button, interaction: discord.Interaction):
            for child in self.children: # loop through all the children of the view
                child.disabled = True # set the button to disabled
            await interaction.response.edit_message(view=self)
                
            await ctx.respond("Alright, I've sent this listing for approval!", ephemeral=True)

            channel = bot.get_channel(vet)
            buying_channel = bot.get_channel(hire_id)

            vetting_channel = bot.get_channel(audit) # post auds

            class PersistentView(discord.ui.View):
                def __init__(self):
                    super().__init__(timeout=None)

                @discord.ui.button(label="Accept", style=discord.ButtonStyle.green, custom_id="persistent_view:green")
                async def accept(self, button: discord.ui.Button, interaction: discord.Interaction):
                    await interaction.response.send_message("Sent the listing!", ephemeral=True)
                    await buying_channel.send(f"{ctx.author.mention}", embed=buy)
                    await vetting_channel.send(f"{interaction.user.mention} **accepted** a `hiring` post by {ctx.author.mention}", embed=buy)
                    await nice.delete()

                @discord.ui.button(label="Decline", style=discord.ButtonStyle.red, custom_id="persistent_view:red")
                async def deny(self, button: discord.ui.Button, interaction: discord.Interaction):
                    await interaction.response.send_message("Declined the listing!", ephemeral=True)
                    await vetting_channel.send(f"{interaction.user.mention} **denied** a `hiring` post by {ctx.author.mention}", embed=buy)
                    await nice.delete()
                    try:
                        rejectionembed=discord.Embed(title="Your listing was rejected!", description=f"Your listing, '{title}', was rejected", color=0xdf2626)
                        rejectionembed.add_field(name="Confused? Contact the marketplace staff that rejected your listing!", value=f"{interaction.user.mention}", inline=False)
                        rejectionembed.set_thumbnail(url=logo_small)
                        await ctx.author.dm_channel.send(embed=rejectionembed)
                    except:
                        informchannel = bot.get_channel(cmds_id)
                        await informchannel.send(f"{ctx.author.mention}, your listing, '{title}', was rejected by {interaction.user.mention}!")
                        print("L")

            nice = await channel.send(f"There is a new post request <@&{moderator}>!", embed=buy, view=PersistentView())

        @discord.ui.button(label="No", style=discord.ButtonStyle.red, custom_id="reviewview:red")
        async def no(self, button: discord.ui.Button, interaction: discord.Interaction):
            for child in self.children: # loop through all the children of the view
                child.disabled = True # set the button to disabled
            await interaction.response.edit_message(view=self)
            
            await interaction.response.send_message("Alright, cancelled the listing!", ephemeral=True)

    await ctx.respond(f"{ctx.author.mention}, are you sure you want to send this listing for approval?", embed=buy, view=ReviewView(), ephemeral=True)

# -- ADVERTISE COMMAND --
@bot.slash_command(name="advertise", description="Promote something!")
@option(
    "title", 
    description="Provide the title of your post.", 
    required=True)
@option(
    "description", 
    description='What are you advertising?', 
    required=True)
@option(
    "link",
    description="Provide a URL to your Discord server, community or organisation!",
    required=True
)
@option(
    "image",
    discord.Attachment,
    description="Upload an image.",
    required=False  # The default value will be None if the user doesn't provide a file.
)
async def advertise(
    ctx: discord.ApplicationContext,
    title: str,
    description: str,
    link: str,
    image: discord.Attachment):

    imageprovided = True

    if image == None:
        imageprovided = False

    buy=discord.Embed(title=f"{title}", description=f"{description}", color=uni_colour)
    buy.set_author(name=f"{ctx.author}", icon_url=f"{ctx.author.avatar}")
    buy.set_thumbnail(url=logo_small)
    buy.add_field(name="Links", value=f"[Linked attachment]({link})", inline=False)
    buy.add_field(name="Contact", value=f"Discord {ctx.author.mention}", inline=False)

    if imageprovided == True:
        buy.set_image(url=f"{image.url}")

    buy.set_footer(text=f"Diverr 2022 | Online Marketplace | ID {ctx.author.id}")

    class ReviewView(discord.ui.View):

        @discord.ui.button(label="Yes", style=discord.ButtonStyle.green, custom_id="reviewview:green")
        async def yes(self, button: discord.ui.Button, interaction: discord.Interaction):
            for child in self.children: # loop through all the children of the view
                child.disabled = True # set the button to disabled
            await interaction.response.edit_message(view=self)
                
            await ctx.respond("Alright, I've sent this listing for approval!", ephemeral=True)

            channel = bot.get_channel(vet)
            buying_channel = bot.get_channel(ads_id)

            vetting_channel = bot.get_channel(audit) # post auds

            class PersistentView(discord.ui.View):
                def __init__(self):
                    super().__init__(timeout=None)

                @discord.ui.button(label="Accept", style=discord.ButtonStyle.green, custom_id="persistent_view:green")
                async def accept(self, button: discord.ui.Button, interaction: discord.Interaction):
                    await interaction.response.send_message("Sent the listing!", ephemeral=True)
                    await buying_channel.send(f"{ctx.author.mention}", embed=buy)
                    await vetting_channel.send(f"{interaction.user.mention} **accepted** a `advertising` post by {ctx.author.mention}", embed=buy)
                    await nice.delete()

                @discord.ui.button(label="Decline", style=discord.ButtonStyle.red, custom_id="persistent_view:red")
                async def deny(self, button: discord.ui.Button, interaction: discord.Interaction):
                    await interaction.response.send_message("Declined the listing!", ephemeral=True)
                    await vetting_channel.send(f"{interaction.user.mention} **denied** a `advertising` post by {ctx.author.mention}", embed=buy)
                    await nice.delete()
                    try:
                        rejectionembed=discord.Embed(title="Your listing was rejected!", description=f"Your listing, '{title}', was rejected", color=0xdf2626)
                        rejectionembed.add_field(name="Confused? Contact the marketplace staff that rejected your listing!", value=f"{interaction.user.mention}", inline=False)
                        rejectionembed.set_thumbnail(url=logo_small)
                        await ctx.author.dm_channel.send(embed=rejectionembed)
                    except:
                        informchannel = bot.get_channel(cmds_id)
                        await informchannel.send(f"{ctx.author.mention}, your listing, '{title}', was rejected by {interaction.user.mention}!")
                        print("L")

            nice = await channel.send(f"There is a new post request <@&{moderator}>!", embed=buy, view=PersistentView())

        @discord.ui.button(label="No", style=discord.ButtonStyle.red, custom_id="reviewview:red")
        async def no(self, button: discord.ui.Button, interaction: discord.Interaction):
            for child in self.children: # loop through all the children of the view
                child.disabled = True # set the button to disabled
            await interaction.response.edit_message(view=self)
            
            await interaction.response.send_message("Alright, cancelled the listing!", ephemeral=True)

    await ctx.respond(f"{ctx.author.mention}, are you sure you want to send this listing for approval?", embed=buy, view=ReviewView(), ephemeral=True)

# -- USER REPORT -- 
@bot.slash_command(name="report", description="Report a user for breaking the rules!")
@option(
    "user", 
    description="Who are you reporting?", 
    required=True)
@option(
    "reason", 
    description="Why are you reporting this user?", 
    required=True)
@option(
    "offensive material", 
    description="Provide any offensive material", 
    required=False)
@option(
    "image",
    discord.Attachment,
    description="Upload an image.",
    required=False  # The default value will be None if the user doesn't provide a file.
    )
async def report(
    ctx: discord.ApplicationContext,
    user: discord.Member,
    reason: str,
    offensive_material: str):

    member = ctx.author
    guild = member.guild
    supporteam = ctx.guild.get_role(judge)

    offensive_material_provided = True

    perms = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        ctx.author: discord.PermissionOverwrite(embed_links=True, view_channel=True, send_messages=True),
        supporteam: discord.PermissionOverwrite(embed_links=True, view_channel=True, send_messages=True)
    }

    addsusperct = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        user: discord.PermissionOverwrite(embed_links=True, view_channel=True, send_messages=True)
    }

    closeperms = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        ctx.author: discord.PermissionOverwrite(view_channel=False, send_messages=False),
        supporteam: discord.PermissionOverwrite(embed_links=True, view_channel=True, send_messages=True)
    }

    if offensive_material_provided == None:
        offensive_material_provided = False

    support_channel = await guild.create_text_channel(name=f"{ctx.author.name}-{ctx.author.id}", overwrites=perms)

    await ctx.respond("Report opened!", ephemeral=True)
    
    embed=discord.Embed(title=f"Report submitted by {ctx.author}", description=f"{reason}", color=0xd22828)
    embed.add_field(name="Report issued by", value=f"{ctx.author.mention}", inline=True)
    embed.add_field(name="Reported user", value=f"{user.mention}", inline=True)

    if offensive_material_provided == True:
        embed.add_field(name="Offensive material", value=f"{offensive_material}", inline=True)

    embed.set_thumbnail(url=logo_small)

    embed.set_footer(text="Welcome to the centre of Diverr Investigations, please send all evidence as we get to your report! Please be patient, we have many reports to handle | Diverr 2022")

    class PersistentView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=None)

        @discord.ui.button(label="Close Case", style=discord.ButtonStyle.red, custom_id="persistent_view:close")
        async def close(self, button: discord.ui.Button, interaction: discord.Interaction):

            if support_channel:
                transcript = await chat_exporter.export(support_channel)
                transcript_file = discord.File(io.BytesIO(transcript.encode()),
                                            filename=f"{support_channel.name}.html")
                
                vetlogs = bot.get_channel(cascl)
                await vetlogs.send(f"{ctx.author.mention} vs {user.mention} DCI 22", embed=embed, file=transcript_file)

            class CloseDelete(discord.ui.View):
                @discord.ui.button(label="Delete Case", style=discord.ButtonStyle.red)
                async def button_callback(self, button, interaction):
                    await support_channel.delete()

            await interaction.response.send_message(f"Case sent in <#{cascl}>!", view=CloseDelete())


            
            for child in self.children:
                child.disabled = True
            await interaction.response.edit_message(view=self)

            await support_channel.edit(overwrites=closeperms)

        @discord.ui.button(label="Add Suspect", style=discord.ButtonStyle.red, custom_id="persistent_view:suspect")
        async def add(self, button: discord.ui.Button, interaction: discord.Interaction):
            
            await interaction.response.send_message(f"{interaction.user} added {user.mention}.")
            await support_channel.edit(overwrites=addsusperct)

            button.disabled = True # set button.disabled to True to disable the button
            button.label = "Suspect Added" # change the button's label to something else
            
            await interaction.response.edit_message(view=self) # edit the message's view

    await support_channel.send(f"> {ctx.author.mention} needs assistance! \n> <@&{judge}> will assist you soon!", embed=embed, view=PersistentView())

bot.run(super_secret_launch_code)
