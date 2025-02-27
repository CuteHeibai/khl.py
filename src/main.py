import json

from khl import Message, Bot
from khl.card import Card, CardMessage, Module, Types, Element, Struct


with open('..\khl.py\src\config\config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)
with open('..\khl.py\src\cmdlist\commands.json', 'r', encoding='utf-8') as g:
    commands = json.load(g)
for command in commands["commands"]:
    # 访问每个命令的 name 和 description
    name = command["name"]
    description = command["description"]
    

# init Bot
bot = Bot(token=config['token'])

# register command
@bot.command(name='help')
async def world(msg: Message):
    cm = CardMessage()
    c = Card(
        Module.Header("服务器指令帮助"),
        Module.Section("**指令 - 描述**"),
    )
    for command in commands["commands"]:
        # 访问每个命令的 name 和 description
        name = command["name"]
        description = command["description"]
        c.append(Module.Section(f"**{name} - {description}**"))
    cm.append(c)
    await msg.reply(cm)

#run bot
bot.run()