import json
import cmdlist

import cmdlist.cmdHandle
from khl import Bot

with open('..\khl.py\src\config\config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# init Bot
bot = Bot(token=config['token'])

# register command
@Bot.on_startup
async def bot_init(bot:Bot):
    cmdlist.cmdHandle.helpCard(bot)
#run bot
bot.run()