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

class sellroleView(nextcord.ui.View):

    def __init__(self, message: nextcord.Message, value: str):
        super().__init__(timeout=None)
        self.message = message
        self.value = value

    @nextcord.ui.button(
        emoji='<a:1_:1135481166955298907',
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
        emoji='🐙',
        label=' วิธีใช้',
        custom_id='how',
        style=nextcord.ButtonStyle.primary,
        row=1
    )
    async def how(self, button: nextcord.Button, interaction: 
      nextcord.Interaction):
        embed = nextcord.Embed(description='''> __**วิธีเติมเงิน**__ กดเติมเงินและนำลิ้งค์ซองไปกรอกในช่องที่ให้ 
        
> __**วิธีซื้อสินค้า**__ กดไปที่คำว่า [ 🛒 เลือกยศที่คุณต้องการซื้อ ] และเลือกสินค้าที่ต้องการซื้อ และกดยืนยันการซื้อยศอีกครั้ง''', color=0x7300ff)
        embed.set_image(url='https://cdn.discordapp.com/attachments/1153966496150736928/1198262788657778848/IMG_20240118_133437.png?ex=65be442f&is=65abcf2f&hm=9106d332802925e0d4e3985d67d8289c0d386d6ca26c8043354171f29440662e&')
        embed.set_footer(text='© 2024 Black Market! All rights reserved', icon_url='https://cdn.discordapp.com/attachments/1153966496150736928/1198262788657778848/IMG_20240118_133437.png?ex=65be442f&is=65abcf2f&hm=9106d332802925e0d4e3985d67d8289c0d386d6ca26c8043354171f29440662e&')
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
    embed.set_image(url='https://cdn.discordapp.com/attachments/1186277649035841536/1186303385578778654/topup.png?ex=6592c21f&is=65804d1f&hm=141f4fc86ab69e95f53a4b9b2f504e8feece4f5079eb61492a0676091be9eab9&')
    embed.title = '**Black Market! ซื้อยศผ่านบอทอัตโนมัติ**'
    embed.set_footer(text='© 2024 Black Market! All rights reserved', icon_url='https://cdn.discordapp.com/attachments/1168590553127067659/1180531764167454771/standard_1.gif?ex=657dc2e1&is=656b4de1&hm=b0b9f434cd611c3ae6842028592c293ac4c9458d12d6afe8a5de1913a677cc71&')
    embed.color = 0x7300ff 
    await interaction.channel.send(embed=embed, view=setupView())    
    await interaction.channel.send('''>>> ** # ซื้อยศผ่านบอทอัตโนมัติ ไม่ต้องรอแอดมิน **
    
**ถ้าเกิดบอทดับเปิดตั๋วมาซื้อกับแอดมินได้เลยครับ**

** ถ้าต้องการชำระเงินผ่านธนาคาร เปิดตั๋วมาได้เลยครับ || @everyone || **''')
    await interaction.response.send_message(content=':Check~1:', ephemeral=True)



bot.run(bots)
