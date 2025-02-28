# Written by Cuteheibai
import json
import asyncio

from datetime import datetime, timedelta
from khl import Message, Bot, GuildUser, Guild
from khl.card import Card, CardMessage, Module, Types, Element, Struct

# 读取配置文件
with open('..\\khl.py\\src\\config\\config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)
with open('..\\khl.py\\src\\cmdlist\\commands.json', 'r', encoding='utf-8') as g:
    commands = json.load(g)

# 定义变量
for command in commands["commands"]:
    name = command["name"]
    description = command["description"]
    admin_role_id = 34396762
    owner_role_id = 40657344
    pm_role_id = 40657805
    helper_role_id = 41731180
    veteran_role_id = 45630256
    premium_role_id = 45297442
    friend_role_id = 40657515
    booster_role_id = 40657489
    accepted_role_id = 40658439
    system_role_id = 45608346
    ann_chnnel_id = "8664560898306293"
    mute_list = {}
    muting_tasks = {}

# 初始化 Bot
bot = Bot(token=config['token'])

# 定义公告消息函数
async def ann_message(type, target_nickname, target_id, user_name, user_avatar, reason, time, duration):
    ch = await bot.client.fetch_public_channel(ann_chnnel_id)
    user_id = target_id[0]
    end_time = datetime.now() + timedelta(seconds=duration)
    
    cm = CardMessage()
    c = Card(
        Module.Header(f"惩罚|{target_nickname}"),
        Module.Divider(),
        Module.Section(f"(met){user_id}(met)"),
        Module.Section(
            Struct.Paragraph(
                3,
                Element.Text(f"**类型:**\n{type}", type=Types.Text.KMD),
                Element.Text(f"**原因:**\n{reason}", type=Types.Text.KMD),
                Element.Text(f"**时间:**\n{time}", type=Types.Text.KMD),
            )
        ),
        Module.Countdown(end_time, mode=Types.CountdownMode.SECOND),
        Module.Divider(),
        Module.Context(
            Element.Text(f"(font)管理员|(font)[pink]", type=Types.Text.KMD),
            Element.Image(src=user_avatar),
            Element.Text(f"(font){user_name}(font)[pink]", type=Types.Text.KMD),
        ),
        theme=Types.Theme.DANGER,
    )
    cm.append(c)
    try:
        await ch.send(cm)
    except Exception as e:
        print(f"发送卡片消息失败: {e}")

async def update_mute_countdown(target_id, original_roles, guild):
    bot_user = await bot.client.fetch_me()
    bot_avatar = bot_user.avatar
    bot_name = bot_user.username 
    bot_id = bot_user.id
    # 初始化任务
    task = asyncio.current_task()
    muting_tasks[target_id] = task  # 保存禁言任务以供取消

    start_time = datetime.now()
    duration = mute_list[target_id]["duration"]

    while duration > 0:
        current_time = datetime.now()
        elapsed_seconds = (current_time - start_time).total_seconds()
        remaining_seconds = max(duration - elapsed_seconds, 0)

        if remaining_seconds <= 0:
            # 倒计时结束，自动解除禁言
            del mute_list[target_id]
            for role_id in original_roles:
                await guild.grant_role(target_id, role_id)  # 恢复原有角色
            await guild.revoke_role(target_id, 45821814)  # 移除禁言角色

            # 发送解除禁言公告
            user = await guild.fetch_user(target_id)
            await unban_ann_message(
                "解除禁言",
                user.nickname,
                [user.id],
                bot_name,
                bot_avatar,  # 替换为实际的管理员头像
                "惩罚时间已结束，自动解除禁言"
            )
            break

        await asyncio.sleep(1)

async def unban_ann_message(type, target_nickname, target_id, user_name, user_avatar, reason):
    ch = await bot.client.fetch_public_channel(ann_chnnel_id)
    user_id = target_id[0]
    
    cm = CardMessage()
    c = Card(
        Module.Header(f"解除惩罚|{target_nickname}"),
        Module.Divider(),
        Module.Section(f"(met){user_id}(met)"),
        Module.Section(
            Struct.Paragraph(
                2,
                Element.Text(f"**类型:**\n{type}", type=Types.Text.KMD),
                Element.Text(f"**原因:**\n{reason}", type=Types.Text.KMD),
            )
        ),
        Module.Divider(),
        Module.Context(
            Element.Text(f"(font)管理员|(font)[success]", type=Types.Text.KMD),
            Element.Image(src=user_avatar),
            Element.Text(f"(font){user_name}(font)[success]", type=Types.Text.KMD),
        ),
        theme=Types.Theme.SUCCESS,  # 设置卡片主题为绿色
    )
    cm.append(c)
    try:
        await ch.send(cm)
    except Exception as e:
        print(f"发送卡片消息失败: {e}")

def parse_duration(duration_str: str) -> int:
    if not duration_str:
        return None
    
    # 正则表达式匹配时间格式
    import re
    match = re.match(r'^(\d+)([MHD]?)$', duration_str, re.IGNORECASE)
    if not match:
        return None
    
    value = int(match.group(1))
    unit = match.group(2).upper()
    
    if unit == 'M':
        return value * 60  # 分钟
    elif unit == 'H':
        return value * 3600  # 小时
    elif unit == 'D':
        return value * 86400  # 天
    else:
        return value  # 默认为秒


# 注册命令
@bot.command(name='help', case_sensitive=False)
async def world(msg: Message):
    cm = CardMessage()
    c = Card(
        Module.Header("服务器指令帮助"),
        Module.Section("**指令 - 描述**"),
    )
    for command in commands["commands"]:
        name = command["name"]
        description = command["description"]
        c.append(Module.Section(f"**{name} - {description}**"))
    
    c.append(Module.Divider())
    c.append(Module.Context(
        Element.Text("触发用户", type=Types.Text.KMD),
        Element.Image(src=msg.author.avatar),
        Element.Text(msg.author.nickname, type=Types.Text.KMD),
    ))
    cm.append(c)
    await msg.reply(cm)

# /mute 命令
# /mute 命令
# /mute 命令
@bot.command(name='mute', case_sensitive=False)
async def mute(msg: Message, *args):
    user: GuildUser = msg.author
    guild: Guild = msg.ctx.guild
    allowed_roles = {owner_role_id, admin_role_id, pm_role_id, helper_role_id, system_role_id}
    
    # 检查执行者的权限
    if any(role in user.roles for role in allowed_roles):
        # 检查参数
        if len(args) < 2:
            # 参数不足，提示用户
            cm = CardMessage()
            c = Card(
                Module.Header("参数不足"),
                Module.Section("请按照格式使用命令：/mute @xxx 时间 禁言原因"),
                Module.Divider(),
                Module.Context(
                    Element.Text("触发用户", type=Types.Text.KMD),
                    Element.Image(src=msg.author.avatar),
                    Element.Text(msg.author.nickname, type=Types.Text.KMD),
                )
            )
            cm.append(c)
            await msg.reply(cm)
            return
        
        # 获取目标用户
        target_id = msg.extra.get("mention", [])
        if not target_id:
            # 参数不足，提示用户
            cm = CardMessage()
            c = Card(
                Module.Header("你没有提及用户"),
                Module.Section("请选择你要禁言的用户"),
                Module.Divider(),
                Module.Context(
                    Element.Text("触发用户", type=Types.Text.KMD),
                    Element.Image(src=msg.author.avatar),
                    Element.Text(msg.author.nickname, type=Types.Text.KMD),
                )
            )
            cm.append(c)
            await msg.reply(cm)
            return
        
        # 获取禁言时间和原因
        duration_str = args[1]
        reason = ' '.join(args[2:]) if len(args) > 2 else ""
        
        duration = parse_duration(duration_str)
        if duration is None:
            # 时间格式错误，提示用户
            cm = CardMessage()
            c = Card(
                Module.Header("禁言时间格式错误"),
                Module.Section("禁言时间格式应为：数字 + 单位（M 表示分钟，H 表示小时，D 表示天），例如：30M、2H、7D"),
                Module.Divider(),
                Module.Context(
                    Element.Text("触发用户", type=Types.Text.KMD),
                    Element.Image(src=msg.author.avatar),
                    Element.Text(msg.author.nickname, type=Types.Text.KMD),
                )
            )
            cm.append(c)
            await msg.reply(cm)
            return
        
        target_id = target_id[0]
        target_user = await guild.fetch_user(target_id)
        user_roles = target_user.roles  # 获取用户的角色列表

        # 检查目标用户是否有管理员权限
        if any(role in allowed_roles for role in user_roles):
            # 提示无法禁言管理员
            cm = CardMessage()
            c = Card(
                Module.Header("你不能禁言该用户！"),
                Module.Divider(),
                Module.Section("该用户具有管理员权限，不能被禁言。"),
                Module.Context(
                    Element.Text("触发用户", type=Types.Text.KMD),
                    Element.Image(src=msg.author.avatar),
                    Element.Text(msg.author.nickname, type=Types.Text.KMD),
                ),
                theme=Types.Theme.DANGER
            )
            cm.append(c)
            await msg.reply(cm)
        else:
            # 获取用户原有角色
            original_roles = user_roles.copy()
            
            # 执行禁言操作
            for role_id in original_roles:
                await guild.revoke_role(target_id, role_id)  # 移除原有角色
            await guild.grant_role(target_id, 45821814)  # 添加禁言角色
            
            # 记录禁言信息
            mute_list[target_id] = {
                "original_roles": original_roles,
                "duration": duration
            }
            
            # 发送禁言公告
            if reason:
                await ann_message(
                "禁言",
                target_user.nickname,
                [target_id],
                user.nickname,
                user.avatar,
                reason,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                duration
            )
            else:
                await ann_message(
                "禁言",
                target_user.nickname,
                [target_id],
                user.nickname,
                user.avatar,
                "管理员未给出原因",
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                duration
            )
            
            # 提示禁言成功
            cm = CardMessage()
            c = Card(
                Module.Header("操作成功！"),
                Module.Section(f"已禁言用户 {target_user.nickname}，时长 {duration_str}。"),
                Module.Context(
                    Element.Text("触发用户", type=Types.Text.KMD),
                    Element.Image(src=msg.author.avatar),
                    Element.Text(msg.author.nickname, type=Types.Text.KMD),
                )
            )
            cm.append(c)
            await msg.reply(cm)
            
            # 启动禁言计时器
            asyncio.create_task(update_mute_countdown(target_id, original_roles, guild))
    else:
        # 提示无权限
        cm = CardMessage()
        c = Card(
            Module.Header("你没有权限使用该命令"),
            Module.Divider(),
            Module.Context(
                Element.Text("触发用户", type=Types.Text.KMD),
                Element.Image(src=msg.author.avatar),
                Element.Text(msg.author.nickname, type=Types.Text.KMD),
            ),
            theme=Types.Theme.DANGER
        )
        cm.append(c)
        await msg.reply(cm)
    
@bot.command(name='ban', case_sensitive=False)
async def ban(msg: Message, *args):
    user: GuildUser = msg.author
    guild: Guild = msg.ctx.guild
    allowed_roles = {owner_role_id, admin_role_id, pm_role_id, helper_role_id, system_role_id}
    
    # 检查执行者的权限
    if any(role in user.roles for role in allowed_roles):
        target_id = msg.extra.get("mention", [])
        reason = ' '.join(args) if args else ""
        
        if target_id:
            try:
                target_user = await guild.fetch_user(target_id[0])
                user_role_ids = target_user.roles  # 假设返回角色ID列表
                user_roles = [role_id for role_id in user_role_ids]
                
                # 检查用户是否有allowed_roles中的角色
                if any(role in allowed_roles for role in user_roles):
                    cm = CardMessage()
                    c = Card(
                        Module.Header("你不能封禁该用户！"),
                        Module.Divider(),
                        Module.Section("该用户具有管理员权限，不能被封禁。"),
                        Module.Context(
                            Element.Text("触发用户", type=Types.Text.KMD),
                            Element.Image(src=msg.author.avatar),
                            Element.Text(msg.author.nickname, type=Types.Text.KMD),
                        ),
                        theme=Types.Theme.DANGER  # 设置卡片主题为红色
                    )
                    cm.append(c)
                    await msg.reply(cm)
                else:
                    # 继续封禁逻辑
                    cm = CardMessage()
                    c = Card(
                        Module.Header("操作成功！"),
                        Module.Divider(),
                        Module.Section(f"已封禁用户 {target_user.nickname}")
                    )
                    cm.append(c)
                    await msg.reply(cm)
                    
                    target_nickname = target_user.nickname if target_user.nickname else target_user.username
                    if reason:
                        await ann_message("**服务器BAN**", target_nickname, target_id, user.nickname, user.avatar, reason, "**永久**")
                    else:
                        await ann_message("**服务器BAN**", target_nickname, target_id, user.nickname, user.avatar, "管理员未给出原因", "**永久**")
                    await guild.kickout(target_id[0])  # 使用 khl.py 提供的踢出方法
            except Exception as e:
                print(f"获取用户信息或角色失败: {e}")
                cm = CardMessage()
                c = Card(
                    Module.Header("无法封禁用户"),
                    Module.Divider(),
                    Module.Context(
                        Element.Text("触发用户", type=Types.Text.KMD),
                        Element.Image(src=msg.author.avatar),
                        Element.Text(msg.author.nickname, type=Types.Text.KMD),
                    )
                )
                cm.append(c)
                await msg.reply(cm)
        else:
            # 提示未提及用户
            cm = CardMessage()
            c = Card(
                Module.Header("你没有提及用户"),
                Module.Section("请选择你要封禁的用户"),
                Module.Divider(),
                Module.Context(
                    Element.Text("触发用户", type=Types.Text.KMD),
                    Element.Image(src=msg.author.avatar),
                    Element.Text(msg.author.nickname, type=Types.Text.KMD),
                )
            )
            cm.append(c)
            await msg.reply(cm)
    else:
        # 提示无权限
        cm = CardMessage()
        c = Card(
            Module.Header("你没有权限使用该命令"),
            Module.Divider(),
            Module.Context(
                Element.Text("触发用户", type=Types.Text.KMD),
                Element.Image(src=msg.author.avatar),
                Element.Text(msg.author.nickname, type=Types.Text.KMD),
            ),
            theme=Types.Theme.DANGER
        )
        cm.append(c)
        await msg.reply(cm)

# /unmute 命令
# /unmute 命令
@bot.command(name='unmute', case_sensitive=False)
async def unmute(msg: Message, *args):
    user: GuildUser = msg.author
    guild: Guild = msg.ctx.guild
    allowed_roles = {owner_role_id, admin_role_id, pm_role_id, helper_role_id, system_role_id}
    
    # 检查执行者的权限
    if any(role in user.roles for role in allowed_roles):
        # 检查参数
        if len(args) < 1:
            # 参数不足，提示用户
            cm = CardMessage()
            c = Card(
                Module.Header("参数不足"),
                Module.Section("请按照格式使用命令：/unmute @xxx 原因"),
                Module.Divider(),
                Module.Context(
                    Element.Text("触发用户", type=Types.Text.KMD),
                    Element.Image(src=msg.author.avatar),
                    Element.Text(msg.author.nickname, type=Types.Text.KMD),
                )
            )
            cm.append(c)
            await msg.reply(cm)
            return
        
        # 获取目标用户
        target_id = msg.extra.get("mention", [])
        if not target_id:
            # 参数不足，提示用户
            cm = CardMessage()
            c = Card(
                Module.Header("你没有提及用户"),
                Module.Section("请选择你要解除禁言的用户"),
                Module.Divider(),
                Module.Context(
                    Element.Text("触发用户", type=Types.Text.KMD),
                    Element.Image(src=msg.author.avatar),
                    Element.Text(msg.author.nickname, type=Types.Text.KMD),
                )
            )
            cm.append(c)
            await msg.reply(cm)
            return
        
        target_id = target_id[0]
        target_user = await guild.fetch_user(target_id)
        user_roles = target_user.roles  # 获取用户的角色列表

        # 检查目标用户是否被禁言
        if 45821814 in user_roles:
            # 获取用户原有角色
            original_roles = mute_list.get(target_id, {}).get("original_roles", [])
            
            # 停止禁言倒计时任务
            if target_id in muting_tasks:
                task = muting_tasks[target_id]
                task.cancel()  # 取消禁言倒计时任务
                del muting_tasks[target_id]
            
            # 执行解除禁言操作
            await guild.revoke_role(target_id, 45821814)  # 移除禁言角色
            for role_id in original_roles:
                await guild.grant_role(target_id, role_id)  # 恢复原有角色
            
            # 删除 mute_list 中的记录
            if target_id in mute_list:
                del mute_list[target_id]
            
            # 发送解除惩罚公告
            reason = ' '.join(args[1:]) if len(args) > 1 else "无"
            if reason:
                await unban_ann_message(
                "解除禁言",
                target_user.nickname,
                [target_id],
                user.nickname,
                user.avatar,
                reason
            )
            else:
                await unban_ann_message(
                "解除禁言",
                target_user.nickname,
                [target_id],
                user.nickname,
                user.avatar,
                "管理员未给出原因")

            
            # 提示解除禁言成功
            cm = CardMessage()
            c = Card(
                Module.Header("操作成功！"),
                Module.Section(f"已解除用户 {target_user.nickname} 的禁言。"),
                Module.Context(
                    Element.Text("触发用户", type=Types.Text.KMD),
                    Element.Image(src=msg.author.avatar),
                    Element.Text(msg.author.nickname, type=Types.Text.KMD),
                )
            )
            cm.append(c)
            await msg.reply(cm)
        else:
            # 提示用户未被禁言
            cm = CardMessage()
            c = Card(
                Module.Header("操作失败！"),
                Module.Section(f"用户 {target_user.nickname} 未被禁言。"),
                Module.Context(
                    Element.Text("触发用户", type=Types.Text.KMD),
                    Element.Image(src=msg.author.avatar),
                    Element.Text(msg.author.nickname, type=Types.Text.KMD),
                ),
                theme=Types.Theme.DANGER
            )
            cm.append(c)
            await msg.reply(cm)
    else:
        # 提示无权限
        cm = CardMessage()
        c = Card(
            Module.Header("你没有权限使用该命令"),
            Module.Divider(),
            Module.Context(
                Element.Text("触发用户", type=Types.Text.KMD),
                Element.Image(src=msg.author.avatar),
                Element.Text(msg.author.nickname, type=Types.Text.KMD),
            ),
            theme=Types.Theme.DANGER
        )
        cm.append(c)
        await msg.reply(cm)

# 运行机器人
bot.run()