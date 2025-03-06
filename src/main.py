# Written by Cuteheibai
import re
import json
import asyncio

from datetime import datetime, timedelta
from khl import Bot, GuildUser, Guild,Message,Channel
from khl.card import Card, CardMessage, Module, Types, Element, Struct

# 读取配置文件
with open('./config/config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)
with open('./config/commands.json', 'r', encoding='utf-8') as g:
    commands = json.load(g)

# 定义变量
for command in commands["commands"]:
    name = command["name"]
    description = command["description"]
    admin_role_id = 34396762
    owner_role_id = 40657344
    pm_role_id = 40657805
    volunteer_role_id = 41731180
    veteran_role_id = 45630256
    premium_role_id = 45297442
    friend_role_id = 40657515
    booster_role_id = 40657489
    accepted_role_id = 40658439
    system_role_id = 45608346
    ann_channel_id = "8664560898306293"
    muting_tasks = {}
    has_permission = {owner_role_id, admin_role_id, pm_role_id, system_role_id}
    


# 初始化 Bot
bot = Bot(token=config['token'])

def load_mute_list():
    try:
        with open('./stat/mute_list.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data
    except FileNotFoundError:
        return {}

def save_mute_list(data):
    with open('./stat/mute_list.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

mute_list = load_mute_list()

# async def get_message_list(channel_id: str, msg_id: str = None, page_size: int = 50):
#     channel = await bot.client.fetch_public_channel(channel_id)
#     messages = await channel.list_messages(msg_id=msg_id, page_size=page_size)
#     return messages
# 定义公告消息函数
async def send_clean_announcement(msg: Message, target_user: GuildUser, reason: str):
    # 获取公告频道
    channel = await bot.client.fetch_public_channel(ann_channel_id)
    
    # 获取管理员信息
    admin_user = msg.author
    
    # 创建卡片消息
    cm = CardMessage()
    c = Card(
        Module.Header(f"清除警告记录|{target_user.nickname}"),
        Module.Section(f"(met){target_user.id}(met)"),
        Module.Section(
            Struct.Paragraph(
                2,
                Element.Text(f"**类型:**\n清除警告记录", type=Types.Text.KMD),
                Element.Text(f"**原因:**\n{reason}", type=Types.Text.KMD),
            )
        ),
        Module.Divider(),
        Module.Context(
            Element.Text(f"(font)管理员|(font)[clean]", type=Types.Text.KMD),
            Element.Image(src=admin_user.avatar),
            Element.Text(f"(font){admin_user.nickname}(font)[clean]", type=Types.Text.KMD),
        ),
        theme=Types.Theme.SUCCESS,
    )
    cm.append(c)
    
    # 发送公告
    try:
        await channel.send(cm)
    except Exception as e:
        print(f"发送清除警告记录公告失败: {e}")

def load_warning_data():
    try:
        with open('./stat/warning_counting.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data
    except FileNotFoundError:
        return {}

# 保存警告记录
def save_warning_data(data):
    with open('./stat/warning_counting.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

async def ann_message(type, target_nickname, target_id, user_name, user_avatar, reason, time, duration= None):
    ch = await bot.client.fetch_public_channel(ann_channel_id)
    user_id = target_id[0]
    if not duration is None:
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
    else:
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
            # 删除 mute_list 中的记录
            if target_id in mute_list:
                del mute_list[target_id]
                # 保存到文件
                save_mute_list(mute_list)
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
    ch = await bot.client.fetch_public_channel(ann_channel_id)
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

async def send_error_response(msg: Message, content: str, theme=Types.Theme.DANGER):
    cm = CardMessage()
    c = Card(
        Module.Header("错误"),
        Module.Section(content),
        Module.Divider(),
        Module.Context(
            Element.Text("触发用户", type=Types.Text.KMD),
            Element.Image(src=msg.author.avatar),
            Element.Text(msg.author.nickname, type=Types.Text.KMD),
        ),
        theme=theme,
    )
    cm.append(c)
    await msg.reply(cm)


async def send_success_response(msg: Message, content: str, theme=Types.Theme.SUCCESS):
    cm = CardMessage()
    c = Card(
        Module.Header("操作成功！"),
        Module.Section(content),
        Module.Divider(),
        Module.Context(
            Element.Text("触发用户", type=Types.Text.KMD),
            Element.Image(src=msg.author.avatar),
            Element.Text(msg.author.nickname, type=Types.Text.KMD),
        ),
        theme=theme,
    )
    cm.append(c)
    await msg.reply(cm)


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
        c.append(Module.Section(f"`{name}` - {description}"))
    
    c.append(Module.Divider())
    c.append(Module.Context(
        Element.Text("触发用户", type=Types.Text.KMD),
        Element.Image(src=msg.author.avatar),
        Element.Text(msg.author.nickname, type=Types.Text.KMD),
    ))
    cm.append(c)
    await msg.reply(cm)

# /mute 命令
@bot.command(name='mute', case_sensitive=False)
async def mute(msg: Message, *args):
    user: GuildUser = msg.author
    guild: Guild = msg.ctx.guild

    # 检查执行者的权限
    if any(role in user.roles for role in has_permission):
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
        reason = ' '.join(args[2:]) if len(args) > 2 else "未提供原因"
        reason = re.sub(r'<@\!?(\d+)>', '', reason).strip()
        
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
        if any(role in has_permission for role in user_roles):
            # 提示无法禁言管理员
            cm = CardMessage()
            c = Card(
                Module.Header("你不能禁言该用户！"),
                Module.Divider(),
                Module.Section("该用户具有管理员权限，不能被禁言。"),
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
        else:
            # 获取用户原有角色
            original_roles = user_roles.copy()
            
            # 执行禁言操作
            for role_id in original_roles:
                await guild.revoke_role(target_id, role_id)  # 移除原有角色
            await guild.grant_role(target_id, 45821814)  # 添加禁言角色
            
            # 记录禁言信息
            # 记录禁言信息
            mute_list[target_id] = {
            "original_roles": original_roles,
            "duration": duration
            }
            # 保存到文件
            save_mute_list(mute_list)
            
            # 发送禁言公告
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
            # 提示禁言成功
            cm = CardMessage()
            c = Card(
                Module.Header("操作成功！"),
                Module.Section(f"已禁言用户 {target_user.nickname}，时长 {duration_str}。"),
                Module.Divider(),
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
    
    # 检查执行者的权限
    if any(role in user.roles for role in has_permission):
        target_id = msg.extra.get("mention", [])
        reason = ' '.join(args) if args else "未提供原因"
        reason = re.sub(r'<@\!?(\d+)>', '', reason).strip()
        
        if target_id:
            try:
                target_user = await guild.fetch_user(target_id[0])
                user_role_ids = target_user.roles  # 假设返回角色ID列表
                user_roles = [role_id for role_id in user_role_ids]
                
                # 检查用户是否有has_permission中的角色
                if any(role in has_permission for role in user_roles):
                    cm = CardMessage()
                    c = Card(
                        Module.Header("你不能封禁该用户！"),
                        Module.Divider(),
                        Module.Section("该用户具有管理员权限，不能被封禁。"),
                        Module.Divider(),
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
                        await ann_message(
                            "**服务器BAN**",
                            target_nickname,
                            target_id,
                            user.nickname,
                            user.avatar,
                            reason,
                            "**永久**"
                        )
                    else:
                        await ann_message(
                            "**服务器BAN**",
                            target_nickname,
                            target_id,
                            user.nickname,
                            user.avatar,
                            "管理员未给出原因",
                            "**永久**"
                        )
                    # await guild.kickout(target_id[0])
                      # 使用 khl.py 提供的踢出方法
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
@bot.command(name='unmute', case_sensitive=False)
async def unmute(msg: Message, *args):
    user: GuildUser = msg.author
    guild: Guild = msg.ctx.guild
    
    # 检查执行者的权限
    if any(role in user.roles for role in has_permission):
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
                Module.Header("你没有选择用户"),
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
            reason = ' '.join(args[1:]) if len(args) > 1 else "未提供原因"
            reason = re.sub(r'<@\!?(\d+)>', '', reason).strip()
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
                    "管理员未给出原因"
                )
            
            # 提示解除禁言成功
            cm = CardMessage()
            c = Card(
                Module.Header("操作成功！"),
                Module.Section(f"已解除用户 {target_user.nickname} 的禁言。"),
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
            # 提示用户未被禁言
            cm = CardMessage()
            c = Card(
                Module.Header("操作失败！"),
                Module.Section(f"用户 {target_user.nickname} 未被禁言。"),
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

@bot.command(name='warn', case_sensitive=False)
async def warn_command(msg: Message, *args):
    user: GuildUser = msg.author
    guild: Guild = msg.ctx.guild
    
    # 检查权限
    if any(role in user.roles for role in has_permission):
        # 检查参数
        if len(args) < 1:
            await send_error_response(msg, "参数不足，请按照格式使用命令：/warn @xxx 原因 或 /warn clean @xxx 原因")
            return
        
        # 判断是否为 'clean' 子命令
        if args[0].lower() == 'clean':
            await handle_clean_command(msg, args[1:])
            return
        
        # 常规警告逻辑
        target_id = msg.extra.get("mention", [])
        if not target_id:
            await send_error_response(msg, "你没有提及用户，请选择要警告的用户")
            return
        
        target_id = target_id[0]
        reason = ' '.join(args[1:]) if len(args) > 1 else "未提供原因"
        reason = re.sub(r'<@\!?(\d+)>', '', reason).strip()
        
        # 更新警告次数
        warning_counts = load_warning_data()
        if target_id not in warning_counts:
            warning_counts[target_id] = 1
        else:
            warning_counts[target_id] += 1
        
        # 保存警告记录到文件
        save_warning_data(warning_counts)
        
        # 发送警告公告
        target_user = await guild.fetch_user(target_id)
        await ann_message(
                "警告",
                target_user.nickname,
                [target_id],
                user.nickname,
                user.avatar,
                reason,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
        
        # 提示警告成功
        await send_success_response(msg, f"已警告用户 {target_user.nickname}，原因：{reason}")
    else:
        # 提示无权限
        await send_error_response(msg, "你没有权限使用该命令", theme=Types.Theme.DANGER)

# 处理清除命令
async def handle_clean_command(msg: Message, args):
    guild: Guild = msg.ctx.guild
    user: GuildUser = msg.author
    
    # 检查权限
    if not any(role in user.roles for role in has_permission):
        await send_error_response(msg, "你没有权限使用该命令", theme=Types.Theme.DANGER)
        return
    
    # 检查参数
    if len(args) < 1:
        await send_error_response(msg, "参数不足，请按照格式使用命令：/warn clean @xxx 原因")
        return
    
    # 获取目标用户
    target_id = msg.extra.get("mention", [])
    if not target_id:
        await send_error_response(msg, "你没有提及用户，请选择要清除警告记录的用户")
        return
    
    target_id = target_id[0]
    reason = ' '.join(args) if args else "未提供原因"

    
    # 检查目标用户是否存在
    try:
        target_user = await guild.fetch_user(target_id)
    except:
        await send_error_response(msg, f"未找到用户 ID 为 {target_id} 的用户")
        return
    
    # 清除警告次数
    warning_counts = load_warning_data()
    if target_id in warning_counts:
        del warning_counts[target_id]
        # 保存警告记录到文件
        save_warning_data(warning_counts)
        await send_clean_announcement(msg, target_user, reason)
        await send_success_response(msg, f"已清除用户 {target_user.nickname} 的警告记录，原因：{reason}")
    else:
        await send_error_response(msg, f"用户 {target_user.nickname} 没有警告记录")


# 添加命令 /clean
# @bot.command(name='clean', case_sensitive=False)
# async def clean_command(msg: Message):
#     user: GuildUser = msg.author
#     channel_id: Channel = msg.ctx.channel.id
#
#     messages = await get_message_list(channel_id)
#
#     # 检查执行者是否有管理员权限
#     if any(role in user.roles for role in has_permission):
#         # 获取消息列表
#         try:
#             for message in messages:
#                 await delete()
#
#         except:
#             await msg.reply("删除消息失败")
#             return
#         # 发送删除成功的消息
#         cm = CardMessage()
#         c = Card(
#             Module.Header(f"成功清除消息"),
#             Module.Context(
#                 Element.Text("触发用户"),
#                 Element.Image(src=user.avatar),
#                 Element.Text(user.nickname)
#             )
#         )
#         cm.append(c)
#         await msg.reply(cm)
#     else:
#         # 提示无权限
#         cm = CardMessage()
#         c = Card(
#             Module.Header("你没有权限使用该命令"),
#             Module.Context(
#                 Element.Text("触发用户"),
#                 Element.Image(src=user.avatar),
#                 Element.Text(user.nickname)
#             )
#         )
#         cm.append(c)
#         await msg.reply(cm)
# 运行机器人
bot.run()