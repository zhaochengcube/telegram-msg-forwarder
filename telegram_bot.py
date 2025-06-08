import os
import re
import logging
import random
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telethon import TelegramClient, events

# 配置日志
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.ERROR
)
logger = logging.getLogger(__name__)

# Telegram API 凭证
# 从 https://my.telegram.org 获取
API_ID = 'your_api_id'
API_HASH = 'your_api_hash'
BOT_TOKEN = 'your_bot_token'

# 代理配置
proxy = ('http', '127.0.0.1', 7890)
# 创建 Telethon 客户端
client = TelegramClient('message_forwarder_session', API_ID, API_HASH, proxy=proxy)

# 消息链接正则表达式模式
# 匹配格式：https://t.me/channel_name/message_id 或 https://t.me/c/channel_id/message_id
MESSAGE_LINK_PATTERN = r'https?://t\.me/(?:c/(\d+)|([^/]+))/(\d+)'

# 存储每个用户最近发送的消息ID，用于批量删除
user_sent_messages = {}
# 存储用户发送的指令消息ID
user_command_messages = {}

async def track_bot_message(user_id, message):
    """跟踪机器人发送的消息，用于后续删除"""
    if user_id not in user_sent_messages:
        user_sent_messages[user_id] = []
    user_sent_messages[user_id].append(message.message_id)
    return message

async def track_user_message(update):
    """跟踪用户发送的消息，用于后续删除"""
    user_id = update.effective_user.id
    if user_id not in user_command_messages:
        user_command_messages[user_id] = []
    user_command_messages[user_id].append(update.message.message_id)

async def should_respond_in_group(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """检查在群聊中是否应该响应消息"""
    # 私聊中总是响应
    if update.message.chat.type == 'private':
        return True
    
    # 群聊中检查是否@了机器人
    message_text = update.message.text or ""
    bot_username = context.bot.username
    
    # 检查消息中是否包含@机器人
    if update.message.entities:
        for entity in update.message.entities:
            if entity.type == 'mention':
                mention = message_text[entity.offset:entity.offset + entity.length]
                if mention == f"@{bot_username}":
                    return True
    
    # 也检查回复消息是否是回复给机器人的
    if update.message.reply_to_message:
        if update.message.reply_to_message.from_user.username == bot_username:
            return True
    
    return False

def parse_link(link):
    """解析消息链接，返回entity和message_id"""
    matches = re.search(MESSAGE_LINK_PATTERN, link)
    if not matches:
        return None, None
    
    channel_id, channel_username, message_id = matches.groups()
    message_id = int(message_id)
    
    if channel_id:  # 私有频道
        channel_id = int(channel_id)
        entity = -1000000000000 - channel_id
    else:  # 公开频道
        entity = channel_username
    
    return entity, message_id

def build_link(entity, message_id):
    """构建消息链接"""
    if isinstance(entity, str):  # 公开频道
        return f"https://t.me/{entity}/{message_id}"
    else:  # 私有频道
        original_channel_id = str(abs(entity + 1000000000000))
        return f"https://t.me/c/{original_channel_id}/{message_id}"

async def send_message_to_user(entity, message_id, user_id, add_link=True):
    """发送单个消息给用户"""
    try:
        # 获取消息组, 前后10条
        message_ids = list(range(message_id - 10, message_id + 10))
        messages = await client.get_messages(entity, ids=message_ids)
        
        # 找到目标消息和同组消息
        target_msg = next((msg for msg in messages if msg and msg.id == message_id), None)
        if not target_msg:
            return False
        
        # 获取同组消息
        if target_msg.grouped_id:
            valid_messages = [msg for msg in messages if msg and msg.grouped_id == target_msg.grouped_id]
        else:
            valid_messages = [target_msg]
        
        valid_messages.sort(key=lambda x: x.id)
        sent_message_ids = []
        
        # 收集媒体文件
        media_list = [msg.media for msg in valid_messages if msg.media]
        
        # 准备文本内容 - 遍历所有消息找到第一个非空文本
        text_content = ""
        for msg in valid_messages:
            if msg.text:
                text_content = msg.text
                break
        
        if add_link:
            text_content += f"\n\n🔗 原始消息: {build_link(entity, message_id)}"
        
        if media_list:
            # 发送媒体组
            caption = text_content[:1024] if len(text_content) > 1024 else text_content
            
            sent_messages = await client.send_file(
                user_id, 
                file=media_list, 
                caption=caption
            )
            
            # 记录消息ID
            if isinstance(sent_messages, list):
                sent_message_ids.extend([msg.id for msg in sent_messages])
            else:
                sent_message_ids.append(sent_messages.id)
            
            # 如果文本太长，单独发送
            if len(text_content) > 1024:
                text_msg = await client.send_message(user_id, f"完整内容：\n{text_content}")
                sent_message_ids.append(text_msg.id)
        
        elif text_content:
            # 只发送文本
            text_msg = await client.send_message(user_id, text_content)
            sent_message_ids.append(text_msg.id)
        
        # 记录发送的消息
        if user_id not in user_sent_messages:
            user_sent_messages[user_id] = []
        user_sent_messages[user_id].extend(sent_message_ids)
        
        return True
    
    except Exception as e:
        logger.error(f"发送消息失败: {e}")
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """当用户发送 /start 命令时的处理函数"""
    await track_user_message(update)
    user = update.effective_user
    message = await update.message.reply_text(f'你好，{user.first_name}！\n'
                                   f'请发送 Telegram 消息链接，我会将消息转发给你。\n\n'
                                   f'💡 在群聊中使用时，请@我或回复我的消息。')
    await track_bot_message(user.id, message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """当用户发送 /help 命令时的处理函数"""
    await track_user_message(update)
    help_text = '将 Telegram 消息链接发送给我，我会尝试获取并转发该消息给你。\n'
    help_text += '支持的链接格式：\n'
    help_text += '- https://t.me/channel_name/message_id\n'
    help_text += '- https://t.me/c/channel_id/message_id\n\n'
    help_text += '另外，你也可以使用以下命令：\n'
    help_text += '/random https://t.me/channel_name/message_id     # 随机发送10条消息\n'
    help_text += '/random https://t.me/channel_name/message_id 5   # 随机发送5条消息\n'
    help_text += '/clear                                           # 删除最近发送的消息\n\n'
    help_text += '📌 群聊使用提示：\n'
    help_text += '• 在群聊中需要@我才会响应\n'
    help_text += '• 也可以回复我的消息来触发\n'
    help_text += '• 命令始终有效，无需@我'
    
    message = await update.message.reply_text(help_text)
    await track_bot_message(update.effective_user.id, message)

async def process_message_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理用户发送的消息链接"""
    # 检查是否应该响应（群聊中需要@机器人）
    if not await should_respond_in_group(update, context):
        return
    
    await track_user_message(update)
    entity, message_id = parse_link(update.message.text)
    
    if not entity:
        message = await update.message.reply_text('请发送有效的 Telegram 消息链接。')
        await track_bot_message(update.effective_user.id, message)
        return
    
    success = await send_message_to_user(entity, message_id, update.effective_user.id)
    
    if not success:
        message = await update.message.reply_text('无法获取该消息，请检查链接或权限。')
        await track_bot_message(update.effective_user.id, message)

async def random_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """根据提供的消息链接随机发送指定数量的消息"""
    await track_user_message(update)
    try:
        args = context.args if hasattr(context, 'args') else []
        if not args:
            message = await update.message.reply_text('请提供消息链接。\n用法: /random https://t.me/channel_name/message_id [数量]')
            await track_bot_message(update.effective_user.id, message)
            return
        
        entity, max_message_id = parse_link(args[0])
        
        if not entity:
            message = await update.message.reply_text('请发送有效的 Telegram 消息链接。')
            await track_bot_message(update.effective_user.id, message)
            return
        
        # 解析发送数量，默认为10条
        send_count = 10
        if len(args) > 1:
            try:
                send_count = int(args[1])
                if send_count <= 0:
                    message = await update.message.reply_text('发送数量必须大于0。')
                    await track_bot_message(update.effective_user.id, message)
                    return
                if send_count > 50:
                    message = await update.message.reply_text('发送数量不能超过50条。')
                    await track_bot_message(update.effective_user.id, message)
                    return
            except ValueError:
                message = await update.message.reply_text('请输入有效的数字作为发送数量。')
                await track_bot_message(update.effective_user.id, message)
                return
        
        # 清空该用户之前的消息记录，为新的批次做准备
        user_sent_messages[update.effective_user.id] = []
        user_command_messages[update.effective_user.id] = []
        
        sent_count = 0
        attempts = 0
        max_attempts = send_count * 5  # 最多尝试次数为目标数量的5倍
        
        while sent_count < send_count and attempts < max_attempts:
            rand_id = random.randint(1, max_message_id)
            attempts += 1
            
            success = await send_message_to_user(entity, rand_id, update.effective_user.id)
            if success:
                sent_count += 1
        
        if sent_count > 0:
            message = await update.message.reply_text(f'已成功发送 {sent_count} 条随机消息！\n使用 /clear 可以删除这些消息。')
            await track_bot_message(update.effective_user.id, message)
        else:
            message = await update.message.reply_text('未能找到有效消息，请检查链接或稍后重试。')
            await track_bot_message(update.effective_user.id, message)

    except Exception as e:
        logger.error(f'随机消息处理错误: {e}')
        message = await update.message.reply_text(f'获取随机消息时出错: {str(e)}')
        await track_bot_message(update.effective_user.id, message)

async def clear_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """删除最近发送给用户的消息以及用户的指令消息"""
    try:
        user_id = update.effective_user.id
        
        # 获取要删除的消息列表
        bot_messages = user_sent_messages.get(user_id, [])
        user_messages = user_command_messages.get(user_id, [])
        all_messages = bot_messages + user_messages
        
        if not all_messages:
            message = await update.message.reply_text('没有可删除的消息。')
            await track_bot_message(user_id, message)
            return
        
        # 添加当前清理命令消息到删除列表
        all_messages.append(update.message.message_id)
        
        deleted_count = 0
        status_message = await update.message.reply_text(f'正在删除 {len(all_messages)} 条消息...')
        
        # 批量删除消息
        for msg_id in all_messages:
            try:
                await client.delete_messages(user_id, msg_id)
                deleted_count += 1
            except Exception as e:
                logger.error(f"删除消息 {msg_id} 失败: {e}")
        
        # 清空记录
        user_sent_messages[user_id] = []
        user_command_messages[user_id] = []
        
        # 删除状态消息
        try:
            await client.delete_messages(user_id, status_message.message_id)
        except:
            pass
        
        if deleted_count > 0:
            result_message = await update.message.reply_text(f'已成功删除 {deleted_count} 条消息！')
            # 延迟删除结果消息
            import asyncio
            await asyncio.sleep(3)
            try:
                await client.delete_messages(user_id, result_message.message_id)
            except:
                pass
        else:
            message = await update.message.reply_text('删除失败，可能消息已被删除或超过48小时。')
            await track_bot_message(user_id, message)
    
    except Exception as e:
        logger.error(f'删除消息时出错: {e}')
        message = await update.message.reply_text(f'删除消息时出错: {str(e)}')
        await track_bot_message(update.effective_user.id, message)

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理非链接消息"""
    # 检查是否应该响应（群聊中需要@机器人）
    if not await should_respond_in_group(update, context):
        return
    
    await track_user_message(update)
    message = await update.message.reply_text('请发送 Telegram 消息链接。如需帮助，请使用 /help 命令。')
    await track_bot_message(update.effective_user.id, message)

def main() -> None:
    # 创建应用程序
    application = Application.builder().token(BOT_TOKEN).build()

    # 添加命令处理器
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("clear", clear_messages))
    
    # 添加消息处理器，处理消息链接
    application.add_handler(MessageHandler(
        filters.TEXT & filters.Regex(MESSAGE_LINK_PATTERN) & ~filters.COMMAND, 
        process_message_link
    ))
    
    # 处理其他消息
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # 添加随机消息处理器
    application.add_handler(CommandHandler("random", random_message))

    # 启动 Telethon 客户端
    client.start(bot_token=BOT_TOKEN)
    print("机器人已启动")
    
    # 运行机器人直到按下 Ctrl-C
    application.run_polling()
    
    # 关闭 Telethon 客户端
    client.disconnect()

if __name__ == '__main__':
    main()