# Deploy on a Linux VPS

This project runs two Telegram polling processes: `bot.py` and `admin_bot.py`.
The instructions below assume Ubuntu/Debian and a server account with `sudo`.

## 1. Rotate the exposed tokens

The tokens previously in the Python files have been exposed. Open `@BotFather` in Telegram, use `/revoke` for each affected bot, and copy the newly generated tokens. Do not reuse the old values.

## 2. Copy the project to the server

From PowerShell, copy the project to your server (replace the host):

```powershell
scp -r .\* user@SERVER_IP:/tmp/telegrambot/
```

On the server:

```bash
sudo useradd --system --create-home --home-dir /opt/telegrambot telegrambot
sudo mkdir -p /opt/telegrambot
sudo cp -r /tmp/telegrambot/. /opt/telegrambot/
sudo chown -R telegrambot:telegrambot /opt/telegrambot
cd /opt/telegrambot
sudo -u telegrambot python3 -m venv .venv
sudo -u telegrambot .venv/bin/pip install --upgrade pip
sudo -u telegrambot .venv/bin/pip install -r requirements.txt
sudo cp .env.example .env
sudo nano .env
sudo chmod 600 .env
sudo chown telegrambot:telegrambot .env
```

Set real values in `.env` for all four token variables. `BOT_TOKEN` and `TARGET_BOT_TOKEN` normally refer to the same target bot, while `MASTER_BOT_TOKEN` is the admin bot token. `TARGET_API_TOKEN` must be the token of the bot that should send target events.

## 3. Install and start both services

```bash
sudo cp telegram-bot.service telegram-admin.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now telegram-bot.service telegram-admin.service
sudo systemctl status telegram-bot.service telegram-admin.service
```

View logs with:

```bash
sudo journalctl -u telegram-bot.service -f
sudo journalctl -u telegram-admin.service -f
```

After changing code or dependencies:

```bash
sudo systemctl restart telegram-bot.service telegram-admin.service
```