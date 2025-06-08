# Telegram消息转发机器人 📬

一个功能强大的Telegram机器人，能够转发指定链接的消息，支持随机消息获取和批量消息管理。

## ✨ 功能特性

- 🔗 **消息链接解析**: 支持解析公开频道和私有频道的消息链接
- 📨 **智能转发**: 自动转发消息内容，包括文本、图片、视频等媒体文件
- 🎲 **随机消息**: 根据指定链接随机获取指定数量的历史消息
- 🧹 **批量清理**: 一键删除机器人发送的所有消息
- 📷 **媒体组支持**: 完整转发媒体组消息
- 🔒 **突破转发限制**: 支持转发被限制的频道消息

## 🛠️ 技术栈

- **Python 3.7+**
- **python-telegram-bot**: 处理机器人API
- **Telethon**: 访问Telegram客户端API
- **python-socks**: 支持代理


## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/zhaochengcube/telegram-msg-forwarder.git
cd telegram-msg-forwarder
```

### 2. 安装依赖

```bash
# 创建虚拟环境
python3 -m venv venv
# 激活虚拟环境-Windows
.\venv\Scripts\Acticate.ps1
# 激活虚拟环境-Mac/Linux
source venv/bin/activate
# 安装依赖
pip install python-telegram-bot telethon python-socks
# 退出虚拟环境-Windows
Ctrl+C
# 退出虚拟环境-Mac/Linux
deactivate
```

### 3. 获取API凭证

#### 获取Bot Token:
1. 在Telegram中找到 [@BotFather](https://t.me/BotFather)
2. 发送 `/newbot` 创建新机器人
3. 按提示设置机器人名称和用户名
4. 获取Bot Token

#### 获取API ID和API Hash:
1. 访问 [https://my.telegram.org](https://my.telegram.org)
2. 登录你的Telegram账号
3. 创建新应用获取API ID和API Hash

### 4. 配置机器人

编辑 `telegram_bot.py` 文件中的配置项：

```python
# Telegram API 凭证
API_ID = 'your_api_id'
API_HASH = 'your_api_hash'
BOT_TOKEN = 'your_bot_token'

# 代理配置（如果需要）
# 端口号改为自己代理软件上的端口号
proxy = ('http', '127.0.0.1', 7890)  # 或设置为 None
```

### 5. 运行机器人

- Windows: 双击 `start_bot.bat` 文件
- Mac/Linux: 
  - `chmod +x start_bot.sh`
  - `./start_bot.sh` 


### 6. 设置机器人命令菜单（可选）
1. 打开 [@BotFather](https://t.me/BotFather)
2. 发送 `/setcommands`
3. 选择你的机器人
4. 输入命令列表
```text
/start - 启动机器人
/help - 显示帮助信息
/random - 随机发送指定数量的消息
/clear - 删除机器人最近发送的所有消息
```

## 📖 使用说明

### 支持的命令

| 命令        | 描述                 | 示例                                    |
| --------- | ------------------ | ------------------------------------- |
| `/start`  | 启动机器人并显示欢迎信息       | `/start`                              |
| `/help`   | 显示帮助信息和命令列表        | `/help`                               |
| `/random` | 随机发送指定数量的消息(默认10条) | `/random https://t.me/channel/123 20` |
| `/clear`  | 删除机器人最近发送的所有消息     | `/clear`                              |

### 支持的链接格式

- **公开频道/群组**: `https://t.me/channel_name/message_id`
- **私有频道/群组**: `https://t.me/c/channel_id/message_id`

### 使用场景

1. **发送链接**: 直接发送Telegram消息链接
2. **随机消息**: 使用 `/random` 命令获取指定链接中随机消息
3. **清理消息**: 使用 `/clear` 命令删除发送的消息


## ⚠️ 注意事项

1. **隐私保护**: 请妥善保管你的API凭证，不要在公开代码中暴露
2. **使用限制**: 遵守Telegram的使用条款和API限制
3. **网络环境**: 某些地区可能需要代理才能正常使用
4. **消息权限**: 只能转发你有权限访问的消息
5. **删除限制**: 只能删除48小时内发送的消息
6. 公开/私有群组以及私有频道需要将机器人添加为管理员成员才能正常使用

## 🐛 故障排除

### 常见问题

**Q: 机器人无法获取消息**
A: 检查消息链接是否正确，确认你有权限访问该频道

**Q: 代理连接失败**
A: 检查代理设置是否正确，确认代理服务器可用

**Q: API请求失败**
A: 检查API凭证是否正确，网络连接是否稳定

## 🤝 贡献指南

欢迎提交Issue和Pull Request来改进这个项目！

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙏 致谢

感谢以下开源项目：
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- [Telethon](https://github.com/LonamiWebs/Telethon)

---

⭐ 如果这个项目对你有帮助，请给个Star支持一下！