from khl import Message, GuildUser, bot

@bot.command(name='ban')
async def ban(msg : Message):
    user: GuildUser = msg.author
    """ 你先研究下怎么弄更好，不然一堆if else史山了 """