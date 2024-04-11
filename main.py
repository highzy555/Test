import nextcord, datetime, json, re, httpx, certifi, os, flask
from nextcord.ext import commands
from threading import Thread
from os import system
from rgbprint import gradient_print, Color
from re import search
from secrets import token_hex
import requests, threading, os
from os import system
from time import sleep
from requests import Session
from httpx import get
from nextcord import Interaction, ButtonStyle, Embed
from nextcord.ui import View
import asyncio
from datetime import datetime, timedelta
from nextcord import Activity, ActivityType, Status
import itertools
from colorama import Fore
from time import sleep
from requests import get
from os import system
from httpx import Client
from bs4 import BeautifulSoup as bs
from user_agent import generate_user_agent
from requests import Session, post, get
from flask import Flask, render_template
from threading import Thread
app = Flask('')
@app.route('/')
def home():
  return "bot python is online!"
def index():
  return render_template("index.html")
def run():
  app.run(host='0.0.0.0', port=8080)
def high():
  t = Thread(target=run)
  t.start()
high()
token = os.environ.get('bot')
bots = token
name = os.environ.get('name')
log_channel_id = 1227929360187654255

try:
    os.mkdir("data")
except FileExistsError:
    print("โฟลเดอร์มีอยู่แล้ว")
else:
    print("สร้างโฟลเดอร์สำเร็จ")


config = json.load(open('./highzy_store_config.json', 'r', encoding='utf-8'))

bot = commands.Bot(
    command_prefix='!',
    help_command=None,
    intents=nextcord.Intents.all(),
    strip_after_prefix=True,
    case_insensitive=True, 
)

class topupModal(nextcord.ui.Modal):

    def __init__(self):
        super().__init__(title='Black Market เติมเงิน', timeout=None, custom_id='topup-modal')
        self.link = nextcord.ui.TextInput(
            label = 'กรอกลิ้งค์ซองอั่งเปา',
            placeholder = 'https://gift.truemoney.com/campaign/?v=xxxxxxxxxxxxxxx',
            style = nextcord.TextInputStyle.short,
            required = True
        )
        self.add_item(self.link)

    async def callback(self, interaction: nextcord.Interaction):
        link = str(self.link.value).replace(' ', '')
        message = await interaction.response.send_message(content='checking.', ephemeral=True)
        if re.match(r'https:\/\/gift\.truemoney\.com\/campaign\/\?v=+[a-zA-Z0-9]{18}', link):
            voucher_hash = link.split('?v=')[1]
            response = httpx.post(
                url = f'https://gift.truemoney.com/campaign/vouchers/{voucher_hash}/redeem',
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/8a0.0.3987.149 Safari/537.36'
                },
                json = {
                    'mobile': config['phoneNumber'],
                    'voucher_hash': f'{voucher_hash}'
                },
                verify=certifi.where(),
            )
            if (response.status_code == 200 and response.json()['status']['code'] == 'SUCCESS'):
                data = response.json()
                amount = int(float(data['data']['my_ticket']['amount_baht']))
                userJSON = json.load(open('./users.json', 'r', encoding='utf-8'))
                if (str(interaction.user.id) not in userJSON):
                    userJSON[str(interaction.user.id)] = {
                        "userId": interaction.user.id,
                        "point": amount,
                        "all-point": amount,
                        "transaction": [
                            {
                                "topup": {
                                    "url": link,
                                    "amount": amount,
                                    "time": str(datetime.datetime.now())
                                }
                            }
                        ]
                    }
                else:
                    userJSON[str(interaction.user.id)]['point'] += amount
                    userJSON[str(interaction.user.id)]['all-point'] += amount
                    userJSON[str(interaction.user.id)]['transaction'].append({
                        "topup": {
                            "url": link,
                            "amount": amount,
                            "time": str(datetime.datetime.now())
                        }
                    })
                json.dump(userJSON, open('./users.json', 'w', encoding='utf-8'), indent=4, ensure_ascii=False)
                embed = nextcord.Embed(description=':Correct_03~1: **เติมเงินสำเร็จ**', color=nextcord.Color.green())
            else:
                embed = nextcord.Embed(description='**เติมเงินไม่สำเร็จ**', color=nextcord.Color.red())
        else:
            embed = nextcord.Embed(description='**รูปแบบลิ้งค์ไม่ถูกต้อง**', color=nextcord.Color.red())
        await message.edit(content=None,embed=embed)
        
class Button(View):
    def __init__(self, log_channel_id):
        super().__init__(timeout=None)
        self.log_channel_id = log_channel_id
        self.cooldowns = {} 

    @nextcord.ui.button(label="เซฟยศ", style=ButtonStyle.primary, emoji="<a:1_:1135481166955298907>")
    async def save(self, button: nextcord.Button, interaction: Interaction):
        user = interaction.user
        if user.id in self.cooldowns and user.id != 1153965156376776754:
            time_remaining = self.cooldowns[user.id] - datetime.now()
            if time_remaining.total_seconds() > 0:
                await interaction.response.send_message(f"> `รอ {int(time_remaining.total_seconds() // 3600)} ชั่วโมง {int((time_remaining.total_seconds() % 3600) // 60)} นาที เพื่อกดเซฟอีกครั้ง ` ❗", ephemeral=True)
                return
        
        role_data = [role.name for role in user.roles if "@everyone" not in role.name]
        file_path = f"data/role_{user.name}.json"
        with open(file_path, "w") as f:
            json.dump(role_data, f)
        
        self.cooldowns[user.id] = datetime.now() + timedelta(days=1)
        
        embed = Embed(title="บันทึกยศที่เซฟ", color=0xdddddd)
        formatted_roles = "\n".join(role_data)
        embed.add_field(name="ยศที่เซฟ", value=f"```\n{formatted_roles}```", inline=False)
        current_time = datetime.now().strftime("%d/%m/%y %H:%M")
        await interaction.send(embed=embed, ephemeral=True)

        log_channel = bot.get_channel(self.log_channel_id)
        if log_channel:
            log_embed = Embed(title="บันทึกเรียบร้อยครับ 📝", color=0xdddddd)
            log_embed.add_field(name="ยศที่เซฟ", value=f"```\n{formatted_roles}```", inline=False)
            log_embed.add_field(name="วันที่เซฟ", value=current_time, inline=False)
            log_message = f"📝 {user.name} ได้ทำการบันทึกยศเรียบร้อยแล้ว"
            log_embed.set_footer(text=log_message)
            if user.avatar:
                    log_embed.set_author(name=f"{user.name} ทำการบันทึกยศเรียบร้อยแล้ว", icon_url=user.avatar.url)
            else:
                log_embed.set_author(name=f"{user.name} ทำการบันทึกยศเรียบร้อยแล้ว", icon_url=None)

            await log_channel.send(embed=log_embed)

    @nextcord.ui.button(label="รับยศคืน", style=ButtonStyle.green, emoji="<a:34:1135479872374968391>")
    async def get(self, button: nextcord.Button, interaction: Interaction):
        user = interaction.user
        file_path = f"data/role_{user.name}.json"
        try:
            with open(file_path, "r") as f:
                role_data = json.load(f)
                for role_name in role_data:
                    roles = nextcord.utils.get(interaction.guild.roles, name=role_name)
                    await user.add_roles(roles)
            await interaction.send("> `คืนยศให้คุณเรียบร้อยแล้วครับ`", ephemeral=True)
        except FileNotFoundError:
            await interaction.send("** # __คุณยังไม่ได้เซฟยศครับไอสัส__ **", ephemeral=True)
        
    @nextcord.ui.button(label="คนเซฟยศ", style=nextcord.ButtonStyle.blurple, emoji="<a:Emoji:1158903282572476426>")
    async def check_saved_roles(self, button: nextcord.Button, interaction: nextcord.Interaction):
        folder_path = "data"  # ตั้งค่า path ของโฟลเดอร์ที่เก็บข้อมูล
        files = os.listdir(folder_path)
        saved_roles_count = len(files)

        await interaction.response.send_message(f"> **จำนวนผู้เซฟยศทั้งหมด:** {saved_roles_count}", ephemeral=True)
        
    @nextcord.ui.button(label="ดูข้อมูลผู้ใช้", style=ButtonStyle.red, emoji="<a:1417_Bell:1075037232928407662>")
    async def get_user_info(self, button: nextcord.Button, interaction: nextcord.Interaction):
        user = interaction.user

        created_since = (interaction.message.created_at - user.created_at).days
        created_since_str = f"{created_since} วันที่ผ่านมา"

        user_info_embed = nextcord.Embed(title=f"ข้อมูลของ {user.display_name}", color=nextcord.Color.blurple())

        if user.avatar:
            user_info_embed.set_thumbnail(url=user.avatar.url)
        else:
            user_info_embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1179255248787873953/1180415784967745536/high.png?ex=657d56de&is=656ae1de&hm=cc029525f43241fcb400d0befaaa53d0be8831b7d0e1cf83e3565ff8eaa51144&")

        user_info_embed.add_field(name="ID Discord", value=user.id, inline=False)
        user_info_embed.add_field(name="วันที่สร้างบัญชี", value=created_since_str, inline=False)

        if len(user.roles) > 1:
            roles = ", ".join([role.mention for role in user.roles[1:]])
            user_info_embed.add_field(name="บทบาท", value=roles, inline=False)

        if user.premium_since:
            user_info_embed.add_field(name="Nitro Boost", value="เป็น Nitro Boost ตั้งแต่: " + user.premium_since.strftime("%Y-%m-%d"), inline=False)


        await interaction.response.send_message(embed=user_info_embed, ephemeral=True)

    @nextcord.ui.button(label="วิธีการใช้งาน", style=ButtonStyle.grey, emoji="<:rules:1175261596587663470>")
    async def usage(self, button: nextcord.Button, interaction: Interaction):
        instructions = "```วิธีการใช้งาน:\n1. คลิกปุ่ม 'เซฟยศ' เพื่อบันทึกยศของคุณ\n2. หากต้องการคืนยศให้กับตัวเอง คลิกปุ่ม 'รับยศคืน' "

        embed = Embed(title="วิธีการใช้งานบอท", description=instructions, color=0x7289da)
        embed.set_footer(text="Blackmarket!")

        await interaction.send(embed=embed, ephemeral=True)        

class sellroleView(nextcord.ui.View):

    def __init__(self, message: nextcord.Message, value: str):
        super().__init__(timeout=None)
        self.message = message
        self.value = value

    @nextcord.ui.button(
        emoji='<a:1_:1135481166955298907>',
        label='ยืนยัน',
        custom_id='already',
        style=nextcord.ButtonStyle.primary,
        row=1
    )
    async def already(self, button: nextcord.Button, interaction: nextcord.Interaction):
        roleJSON = json.load(open('./roles.json', 'r', encoding='utf-8'))
        userJSON = json.load(open('./users.json', 'r', encoding='utf-8'))
        if (str(interaction.user.id) not in userJSON):
            embed = nextcord.Embed(description="# เติมเงินเพื่อเปิดบัญชี", color=nextcord.Color.red())
        else:
            if (userJSON[str(interaction.user.id)]['point'] >= roleJSON[self.value]['price']):
                userJSON[str(interaction.user.id)]['point'] -= roleJSON[self.value]['price']
                userJSON[str(interaction.user.id)]['transaction'].append({
                    "payment": {
                        "roleId": self.value,
                        "time": str(datetime.datetime.now())
                    }
                })
                json.dump(userJSON, open('./users.json', 'w', encoding='utf-8'), indent=4, ensure_ascii=False)
                if ('package' in self.value):
                    for roleId in roleJSON[self.value]['roleIds']:
                      try:
                          await interaction.user.add_roles(nextcord.utils.get(interaction.user.guild.roles, id = roleId))
                      except:
                            pass
                    channelLog = bot.get_channel(config['channelLog'])
                    if (channelLog):
                        embed = nextcord.Embed()
                        embed.description = f'''**Black Market ประวัติการซื้อยศ**
\n> **ชื่อผู้ใช้งาน** 
\n** <@{interaction.user.id}> **

> **ราคายศ** 
\n** 💸 {roleJSON[self.value]['price']} บาท **

> **ยศที่ซื้อ** 
\n** 🛒 <@&{roleJSON[self.value]["roleId"]}> **
'''
                        embed.set_footer(text=f'N. {interaction.user.name} - I. {interaction.user.id}', icon_url=interaction.user.avatar.url)
                        embed.color = 0x7300ff
                        await channelLog.send(embed=embed)
                    embed = nextcord.Embed(description=f'''**Black Market ซื้อยศสำเร็จ**
\n> **ชื่อผู้ใช้งาน** 
\n** <@{interaction.user.id}> **

> **ราคายศ** 
\n** 💸 {roleJSON[self.value]['price']} บาท **

> **ยศที่ซื้อ** 
\n** 🛒 <@&{roleJSON[self.value]["roleId"]}> **
''', color=nextcord.Color.green())
                else:
                    channelLog = bot.get_channel(config['channelLog'])
                    if (channelLog):
                        embed = nextcord.Embed()
                        embed.description = f'''**Black Market! ประวัติการซื้อยศ**
\n> **ชื่อผู้ใช้งาน** 
\n** <@{interaction.user.id}> **

> **ราคายศ** 
\n** 💸 {roleJSON[self.value]['price']} บาท **

> **ยศที่ซื้อ** 
\n** 🛒 <@&{roleJSON[self.value]["roleId"]}> ** _ _\n
'''
                        embed.set_footer(text=f'N. {interaction.user.name} - I. {interaction.user.id}', icon_url=interaction.user.avatar.url)
                        embed.color = 0x7300ff
                        await channelLog.send(embed=embed)
                    embed = nextcord.Embed(description=f'''**Black Market! ซื้อยศสำเร็จ**
\n> **ชื่อผู้ใช้งาน** 
\n** <@{interaction.user.id}> **

> **ราคายศ** 
\n** 💸 {roleJSON[self.value]['price']} บาท **

> **ยศที่ซื้อ** 
\n** 🛒 <@&{roleJSON[self.value]["roleId"]}> **
''', color=0x7300ff)
                    embed.set_footer(text=f'N. {interaction.user.name} - I. {interaction.user.id}', icon_url=interaction.user.avatar.url)
                    role = nextcord.utils.get(interaction.user.guild.roles, id = roleJSON[self.value]['roleId'])
                    await interaction.user.add_roles(role)
            else:
                embed = nextcord.Embed(description=f'> **เงินของท่านไม่เพียงพอ ขาดอีก {roleJSON[self.value]["price"] - userJSON[str(interaction.user.id)]["point"]} บาท**', color=nextcord.Color.red())
        return await self.message.edit(embed=embed, view=None, content=None)

    @nextcord.ui.button(
        emoji='<a:2_:1136812316600574022>',
        label='ยกเลิก',
        custom_id='cancel',
        style=nextcord.ButtonStyle.red,
        row=1
    )
    async def cancel(self, button: nextcord.Button, interaction: nextcord.Interaction):
        return await self.message.edit(content='> **<a:1_:1135481166955298907> ยกเลิกสำเร็จ**',embed=None, view=None)

class sellroleSelect(nextcord.ui.Select):

    def __init__(self):
        options = []
        roleJSON = json.load(open('./roles.json', 'r', encoding='utf-8'))
        for role in roleJSON:
            options.append(nextcord.SelectOption(
                label=roleJSON[role]['name'],
                description=roleJSON[role]['description'],
                value=role,
                emoji=roleJSON[role]['emoji']
            ))
        super().__init__(
            custom_id='select-role',
            placeholder='[ 🛒 เลือกยศที่คุณต้องการซื้อได้เลยครับ ]',
            min_values=1,
            max_values=1,
            options=options,
            row=0
        )
    async def callback(self, interaction: nextcord.Interaction):
        message = await interaction.response.send_message(content='กำลังตรวจสอบ...', ephemeral=True)
        selected = self.values[0]
        if ('package' in selected):
            roleJSON = json.load(open('./roles.json', 'r', encoding='utf-8'))
            embed = nextcord.Embed()
            embed.description = f'''
E {roleJSON[selected]['name']}**
'''
            await message.edit(content=None,embed=embed,view=sellroleView(message=message, value=selected))
        else:
            roleJSON = json.load(open('./roles.json', 'r', encoding='utf-8'))
            embed = nextcord.Embed()
            embed.title = '**กรุณากดยืนยันที่จะซื้อยศ**'
            embed.description = f'''**> <@&{roleJSON[selected]['roleId']}>**'''
            embed.color = 0x7300ff
            await message.edit(content=None,embed=embed,view=sellroleView(message=message, value=selected))

class setupView(nextcord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(sellroleSelect())

    @nextcord.ui.button(
        emoji='<a:7y4badgesrole:1135479816280358984>',
        label=' เติมเงิน',
        custom_id='topup',
        style=nextcord.ButtonStyle.primary,
        row=1
    )
    async def topup(self, button: nextcord.Button, interaction: nextcord.Interaction):
        await interaction.response.send_modal(topupModal())

    @nextcord.ui.button(
        emoji='<a:1_:1135481166955298907>',
        label=' เช็คยอดเงิน',
        custom_id='balance',
        style=nextcord.ButtonStyle.primary,
        row=1
    )
    async def balance(self, button: nextcord.Button, interaction: nextcord.Interaction):
        userJSON = json.load(open('./users.json', 'r', encoding='utf-8'))
        if (str(interaction.user.id) not in userJSON):
            embed = nextcord.Embed(description='> **เติมเงินเพื่อเปิดบัญชี**', color=nextcord.Color.red())
        else:
            embed = nextcord.Embed(description=f'> ** ยอดเงินคงเหลือ {userJSON[str(interaction.user.id)]["point"]} บาท **', color=nextcord.Color.green())
        return await interaction.response.send_message(embed=embed, ephemeral=True)

    @nextcord.ui.button(
        emoji='<a:34:1135479872374968391>',
        label=' วิธีใช้',
        custom_id='how',
        style=nextcord.ButtonStyle.primary,
        row=1
    )
    async def how(self, button: nextcord.Button, interaction: 
      nextcord.Interaction):
        embed = nextcord.Embed(description='''> __**วิธีเติมเงิน**__ กดเติมเงินและนำลิ้งค์ซองไปกรอกในช่องที่ให้ 
        
> __**วิธีซื้อสินค้า**__ กดไปที่คำว่า [ 🛒 เลือกยศที่คุณต้องการซื้อ ] และเลือกสินค้าที่ต้องการซื้อ และกดยืนยันการซื้อยศอีกครั้ง''', color=0x7300ff)
        embed.set_image(url='https://cdn.discordapp.com/attachments/1217085743005044786/1219003029349732524/truemoney-wallet.png?ex=6609b80a&is=65f7430a&hm=c8d1e8da1cdc128c3083cae9a37d83da68b52a05e657acfdcf6f6d474dabe2a5&')
        embed.set_footer(text='© 2024 Black Market! All rights reserved', icon_url='https://cdn.discordapp.com/attachments/1169309802955026494/1219000309540585492/truemoney-wallet.png?ex=6609b581&is=65f74081&hm=4a794a5230b9e462810f0600c575693f8d54b6aa0a715b54459bb060becb6a8d&')
        return await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.event
async def on_ready():
  bot.add_view(setupView())
  system('cls')
  print(f"Bot {bot.user.name} is ready!")
  await bot.change_presence(activity=nextcord.Streaming(
      name='Black Market !', url='https://www.twitch.tv/example_channel'))

@bot.slash_command(
    name='setup',
    description='setup',
    guild_ids=[config['serverId']]
)
async def setup(interaction: nextcord.Interaction):
    if (interaction.user.id not in config['ownerIds']):
        return await interaction.response.send_message(content='[ERROR] No Permission For Use This Command.', ephemeral=True)
    embed = nextcord.Embed()
    embed.set_image(url='https://cdn.discordapp.com/attachments/1217085743005044786/1219002707172524162/1422685976-5cm-o.jpg?ex=6609b7bd&is=65f742bd&hm=54dbc70bfa7c8869e688cb53c320e5f17ae565f8d788068160920e3dd9245d0a&')
    embed.title = '**Black Market! ซื้อยศผ่านบอทอัตโนมัติ**'
    embed.set_footer(text='© 2024 Black Market! All rights reserved', icon_url='https://cdn.discordapp.com/attachments/1217085743005044786/1219002707172524162/1422685976-5cm-o.jpg?ex=6609b7bd&is=65f742bd&hm=54dbc70bfa7c8869e688cb53c320e5f17ae565f8d788068160920e3dd9245d0a&')
    embed.color = 0x7300ff 
    await interaction.channel.send(embed=embed, view=setupView())    
    await interaction.channel.send('''>>> ** # ซื้อยศผ่านบอทอัตโนมัติ ไม่ต้องรอแอดมิน **
    
**ถ้าเกิดบอทดับเปิดตั๋วมาซื้อกับแอดมินได้เลยครับ**

** ถ้าต้องการชำระเงินผ่านธนาคาร เปิดตั๋วมาได้เลยครับ || @everyone || **''')
    await interaction.response.send_message(content=':Check~1:', ephemeral=True)
    
@bot.command()
async def setup(ctx: Interaction):
    if ctx.author.name == name:
        await ctx.message.delete()
        embed = Embed(title="** __BOTSAVEROLEAUTO__ **",
                      description="** ซื้อยศแล้ว อย่าลืมมาเซฟยศกันนะครับ\nกันหลุดออกจากดิส ไม่มีการคืนยศใดๆ หากท่านไม่ได้เซฟยศเอาไว้**",
                      color=0xdddddd)
        embed.set_image(url="https://cdn.discordapp.com/attachments/1217085743005044786/1219002707172524162/1422685976-5cm-o.jpg?ex=6609b7bd&is=65f742bd&hm=54dbc70bfa7c8869e688cb53c320e5f17ae565f8d788068160920e3dd9245d0a&")
        embed.set_footer(text="Blackmarket!")
        await ctx.send(embed=embed, view=Button(log_channel_id))    



bot.run(bots)
