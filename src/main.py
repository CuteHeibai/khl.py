from khl import Bot

import json
import cmdlist.cmdHandle as cmdHandle

with open('..\khl.py\src\config\config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# init Bot
bot = Bot(token=config['token'])

# register command
@Bot.on_startup
async def bot_init(bot:Bot):
    #帮助调用
    cmdHandle.helpCard(bot)
#run bot
bot.run()