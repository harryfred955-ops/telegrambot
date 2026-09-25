import logging
import os
import datetime
import httpx
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatPermissions
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
log = logging.getLogger(__name__)

MASTER_TOKEN    = os.environ["MASTER_BOT_TOKEN"]
TARGET_BOT_TOKEN = os.environ["TARGET_BOT_TOKEN"]
TARGET_API_TOKEN = os.environ["TARGET_API_TOKEN"]

# TARGET_CHAT_ID: The group/channel ID where real moderation commands apply.
# Get it by adding @userinfobot to your group — it will show the chat ID (negative number).
TARGET_CHAT_ID  = os.environ.get("TARGET_CHAT_ID", "")
OWNER_USERNAME  = os.environ.get("OWNER_USERNAME", "marco51375")

# Tracks active events started via /event start
active_events: dict = {}


# ── Auth helpers ──────────────────────────────────────────────────────────────

def is_authorized(user) -> bool:
    if not user:
        return False
    return bool(user.username and user.username.lower() == OWNER_USERNAME.lower())


def admin_only(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        if not user or not is_authorized(user):
            await update.message.reply_text("❌ ACCESS DENIED!")
            return
        return await func(update, context)
    wrapper.__name__ = func.__name__
    return wrapper


# ── Utility ───────────────────────────────────────────────────────────────────

def parse_duration(s: str) -> datetime.timedelta:
    """Parse '30m', '2h', '7d', '90s' into a timedelta. Plain int = minutes."""
    s = s.strip().lower()
    try:
        if s.endswith('d'):
            return datetime.timedelta(days=int(s[:-1]))
        if s.endswith('h'):
            return datetime.timedelta(hours=int(s[:-1]))
        if s.endswith('m'):
            return datetime.timedelta(minutes=int(s[:-1]))
        if s.endswith('s'):
            return datetime.timedelta(seconds=int(s[:-1]))
        return datetime.timedelta(minutes=int(s))
    except ValueError:
        raise ValueError(f"Cannot parse duration: '{s}' — use formats like 30m, 2h, 7d")


def require_chat_id(func):
    """Decorator: reject real commands if TARGET_CHAT_ID is not set."""
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not TARGET_CHAT_ID:
            await update.message.reply_text(
                "❌ `TARGET_CHAT_ID` is not set.\n"
                "Add it in your `.env` or Render Environment Variables.",
                parse_mode="Markdown"
            )
            return
        return await func(update, context)
    wrapper.__name__ = func.__name__
    return wrapper


async def trigger_target_event(chat_id, event_text):
    """Send a styled message to a chat via the TARGET_API_TOKEN bot."""
    api_url = f"https://api.telegram.org/bot{TARGET_API_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": f"POTATA: {event_text}", "parse_mode": "Markdown"}
    async with httpx.AsyncClient() as client:
        await client.post(api_url, json=payload)


# ── START / HELP ──────────────────────────────────────────────────────────────

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("⚡ Command Grid", callback_data="menu_main")],
        [InlineKeyboardButton("🛡️ System Metrics", callback_data="menu_metrics"),
         InlineKeyboardButton("🚀 Launch Protocol", callback_data="menu_launch")]
    ])
    await update.message.reply_text(
        "POTATA: Advanced Cyber-Core Online 🌌\nChoose your interface matrix below:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )


@admin_only
async def admin_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚡ **ADMIN COMMAND REFERENCE**\n\n"
        "🔴 **Real Moderation (requires bot to be admin in target group)**\n"
        "`/checkuser [user_id or @username]` — User info & status\n"
        "`/ban [user_id] [duration] [reason]` — Ban (e.g. 30m, 2h, 7d)\n"
        "`/kick [user_id] [reason]` — Remove from group (can rejoin)\n"
        "`/stopspam [user_id] [duration] [reason]` — Mute user\n"
        "`/global [message]` — Broadcast to target chat\n"
        "`/event [start/stop] [name]` — Announce event start/stop\n\n"
        "🎭 **Fun / Roleplay Commands**\n"
        "`/nuke /earthquake /blackout /alien /zombie /weather`\n"
        "`/hack /fakeban /fakerestart /matrix /ghost /bounty`\n"
        "`/firewall /quantum /overclock /stealth /emergency`\n\n"
        "Use `/adminhelp` to see this menu.",
        parse_mode="Markdown"
    )


# ── INTERACTIVE MENU ──────────────────────────────────────────────────────────

async def button_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "menu_main":
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔴 Moderation", callback_data="cat_mod"),
             InlineKeyboardButton("🎭 Fun Commands", callback_data="cat_fun")],
            [InlineKeyboardButton("🛡️ Metrics", callback_data="menu_metrics"),
             InlineKeyboardButton("🚀 Launch Info", callback_data="menu_launch")]
        ])
        await query.edit_message_text(
            "POTATA: ⚡ **COMMAND GRID**\nSelect a module:", reply_markup=keyboard, parse_mode="Markdown"
        )
    elif data == "menu_metrics":
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="menu_main")]])
        await query.edit_message_text(
            "POTATA: 📊 Master CPU 0.01% | Sync 100% | Latency 0.4ms 🟢",
            reply_markup=keyboard, parse_mode="Markdown"
        )
    elif data == "menu_launch":
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="menu_main")]])
        await query.edit_message_text(
            "POTATA: 🚀 All protocols armed!", reply_markup=keyboard, parse_mode="Markdown"
        )
    elif data == "cat_mod":
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="menu_main")]])
        await query.edit_message_text(
            "🔴 **Moderation Commands:**\n"
            "`/checkuser` `/ban` `/kick` `/stopspam` `/global` `/event`",
            reply_markup=keyboard, parse_mode="Markdown"
        )
    elif data == "cat_fun":
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="menu_main")]])
        await query.edit_message_text(
            "🎭 **Fun Commands:**\n"
            "`/nuke` `/hack` `/earthquake` `/blackout` `/alien` `/zombie`\n"
            "`/fakeban` `/matrix` `/ghost` `/firewall` `/quantum` `/emergency`",
            reply_markup=keyboard, parse_mode="Markdown"
        )
    elif data == "btn_replay":
        await query.message.reply_text("POTATA: 🎞️ Media loop re-injected!")
    elif data == "btn_boost":
        await query.message.reply_text("POTATA: ⚡ Node supercharged by 1000%! 🚀")


# ── GIF MIRROR ────────────────────────────────────────────────────────────────

async def mirror_gif_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not user or not is_authorized(user):
        return
    if update.message.animation:
        file_id = update.message.animation.file_id
        chat_id = update.effective_chat.id
        caption = update.message.caption or ""
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔥 Replay Grid", callback_data="btn_replay"),
             InlineKeyboardButton("⚡ Boost Node", callback_data="btn_boost")]
        ])
        api_url = f"https://api.telegram.org/bot{TARGET_API_TOKEN}/sendAnimation"
        payload = {
            "chat_id": chat_id,
            "animation": file_id,
            "caption": f"POTATA: {caption}" if caption else "POTATA: 🎞️ [Advanced Media Feed]",
            "reply_markup": keyboard.to_dict()
        }
        async with httpx.AsyncClient() as client:
            await client.post(api_url, json=payload)


# ══════════════════════════════════════════════════════════════════════════════
# 🔴 REAL MODERATION COMMANDS
# ══════════════════════════════════════════════════════════════════════════════

@admin_only
@require_chat_id
async def cmd_checkuser(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /checkuser [user_id or @username]
    Fetches the user's info and status in the target chat.
    """
    if not context.args:
        await update.message.reply_text(
            "📋 Usage: `/checkuser [user_id or @username]`", parse_mode="Markdown"
        )
        return

    identifier = context.args[0]
    chat_id = int(TARGET_CHAT_ID)

    try:
        # Resolve to a numeric ID
        if identifier.lstrip("@").lstrip("-").isdigit() and not identifier.startswith("@"):
            uid = int(identifier)
        else:
            username = identifier.lstrip("@")
            chat_obj = await context.bot.get_chat(f"@{username}")
            uid = chat_obj.id

        member = await context.bot.get_chat_member(chat_id=chat_id, user_id=uid)
        user = member.user
        status_emoji = {
            "creator": "👑", "administrator": "🛡️", "member": "👤",
            "restricted": "🔇", "left": "🚪", "banned": "🔨",
        }.get(member.status, "❓")

        text = (
            f"👤 **User Info**\n\n"
            f"🆔 ID: `{user.id}`\n"
            f"📛 Name: {user.full_name}\n"
            f"🔗 Username: {'@' + user.username if user.username else 'None'}\n"
            f"🤖 Bot: {'Yes' if user.is_bot else 'No'}\n"
            f"{status_emoji} Status: `{member.status}`"
        )

        # Extra info for restricted members
        if member.status == "restricted":
            text += (
                f"\n\n🔒 **Restrictions:**\n"
                f"• Can send messages: {member.permissions.can_send_messages}\n"
                f"• Until: {member.until_date or 'Permanent'}"
            )
        await update.message.reply_text(text, parse_mode="Markdown")

    except Exception as e:
        await update.message.reply_text(f"❌ Error: `{e}`", parse_mode="Markdown")


@admin_only
@require_chat_id
async def cmd_ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /ban [user_id] [duration] [reason]
    Duration examples: 30m, 2h, 7d — omit for permanent ban.
    """
    if not context.args:
        await update.message.reply_text(
            "📋 Usage: `/ban [user_id] [duration e.g. 30m 2h 7d] [reason]`\n"
            "Omit duration to ban permanently.",
            parse_mode="Markdown"
        )
        return

    try:
        uid = int(context.args[0])
        until_date = None
        reason = "No reason provided"
        duration_label = "permanently"

        if len(context.args) > 1:
            try:
                td = parse_duration(context.args[1])
                until_date = datetime.datetime.now(datetime.timezone.utc) + td
                duration_label = f"for **{context.args[1]}**"
                reason = " ".join(context.args[2:]) or reason
            except ValueError:
                reason = " ".join(context.args[1:])

        await context.bot.ban_chat_member(
            chat_id=int(TARGET_CHAT_ID), user_id=uid, until_date=until_date
        )
        await update.message.reply_text(
            f"🔨 **Banned** `{uid}` {duration_label}\n"
            f"📝 Reason: {reason}",
            parse_mode="Markdown"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Ban failed: `{e}`", parse_mode="Markdown")


@admin_only
@require_chat_id
async def cmd_kick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /kick [user_id] [reason]
    Removes user from the group (they can rejoin via invite link).
    """
    if not context.args:
        await update.message.reply_text(
            "📋 Usage: `/kick [user_id] [reason]`", parse_mode="Markdown"
        )
        return

    try:
        uid = int(context.args[0])
        reason = " ".join(context.args[1:]) or "No reason provided"

        # Telegram kick = ban then immediately unban
        await context.bot.ban_chat_member(chat_id=int(TARGET_CHAT_ID), user_id=uid)
        await context.bot.unban_chat_member(
            chat_id=int(TARGET_CHAT_ID), user_id=uid, only_if_banned=True
        )
        await update.message.reply_text(
            f"👢 **Kicked** `{uid}` from the group\n📝 Reason: {reason}",
            parse_mode="Markdown"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Kick failed: `{e}`", parse_mode="Markdown")


@admin_only
@require_chat_id
async def cmd_stopspam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /stopspam [user_id] [duration] [reason]
    Mutes (restricts) a user for the given duration.
    Duration examples: 30m, 1h, 2d — omit for permanent mute.
    """
    if not context.args:
        await update.message.reply_text(
            "📋 Usage: `/stopspam [user_id] [duration e.g. 30m 1h 2d] [reason]`\n"
            "Omit duration to mute permanently.",
            parse_mode="Markdown"
        )
        return

    try:
        uid = int(context.args[0])
        until_date = None
        reason = "Spam detected"
        duration_label = "permanently"

        if len(context.args) > 1:
            try:
                td = parse_duration(context.args[1])
                until_date = datetime.datetime.now(datetime.timezone.utc) + td
                duration_label = f"for **{context.args[1]}**"
                reason = " ".join(context.args[2:]) or reason
            except ValueError:
                reason = " ".join(context.args[1:])

        no_perms = ChatPermissions(
            can_send_messages=False,
            can_send_photos=False,
            can_send_videos=False,
            can_send_audios=False,
            can_send_documents=False,
            can_send_voice_notes=False,
            can_send_video_notes=False,
            can_send_other_messages=False,
            can_add_web_page_previews=False,
        )
        await context.bot.restrict_chat_member(
            chat_id=int(TARGET_CHAT_ID),
            user_id=uid,
            permissions=no_perms,
            until_date=until_date,
        )
        await update.message.reply_text(
            f"🔇 **Muted** `{uid}` {duration_label}\n📝 Reason: {reason}",
            parse_mode="Markdown"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Mute failed: `{e}`", parse_mode="Markdown")


@admin_only
@require_chat_id
async def cmd_global(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /global [message]
    Sends a global broadcast to the target chat.
    """
    if not context.args:
        await update.message.reply_text(
            "📋 Usage: `/global [your message]`", parse_mode="Markdown"
        )
        return

    message = " ".join(context.args)
    try:
        await context.bot.send_message(
            chat_id=int(TARGET_CHAT_ID),
            text=f"📢 **GLOBAL ANNOUNCEMENT**\n\n{message}",
            parse_mode="Markdown"
        )
        await update.message.reply_text("✅ Global message sent to target chat!")
    except Exception as e:
        await update.message.reply_text(f"❌ Failed: `{e}`", parse_mode="Markdown")


@admin_only
@require_chat_id
async def cmd_event(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /event [start/stop] [event name]
    Announces event start or end in the target chat and tracks active events.
    Run /event alone to list active events.
    """
    if not context.args:
        if active_events:
            names = "\n".join(f"• {n}" for n in active_events)
            await update.message.reply_text(
                f"🎉 **Active Events:**\n{names}\n\n"
                "Use `/event stop [name]` to end one.",
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(
                "No active events.\nUsage: `/event [start/stop] [event name]`",
                parse_mode="Markdown"
            )
        return

    if len(context.args) < 2:
        await update.message.reply_text(
            "📋 Usage: `/event [start/stop] [event name]`", parse_mode="Markdown"
        )
        return

    action = context.args[0].lower()
    name = " ".join(context.args[1:])

    try:
        if action == "start":
            active_events[name] = True
            await context.bot.send_message(
                chat_id=int(TARGET_CHAT_ID),
                text=(
                    f"🎉 **EVENT STARTED!**\n\n"
                    f"📌 **{name}**\n\n"
                    f"Stay tuned for updates! 🚀"
                ),
                parse_mode="Markdown"
            )
            await update.message.reply_text(
                f"✅ Event `{name}` started and announced!", parse_mode="Markdown"
            )

        elif action == "stop":
            active_events.pop(name, None)
            await context.bot.send_message(
                chat_id=int(TARGET_CHAT_ID),
                text=(
                    f"🔴 **EVENT ENDED**\n\n"
                    f"📌 **{name}**\n\n"
                    f"Thanks for participating! 🙏"
                ),
                parse_mode="Markdown"
            )
            await update.message.reply_text(
                f"✅ Event `{name}` stopped and announced!", parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(
                "❌ Action must be `start` or `stop`.", parse_mode="Markdown"
            )
    except Exception as e:
        await update.message.reply_text(f"❌ Error: `{e}`", parse_mode="Markdown")


# ══════════════════════════════════════════════════════════════════════════════
# 🎭 FUN / ROLEPLAY COMMANDS (send styled messages to target chat)
# ══════════════════════════════════════════════════════════════════════════════

def _fun(text: str):
    """Factory: create an admin-only handler that triggers a styled event message."""
    @admin_only
    async def _handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        args = " ".join(context.args) if context.args else ""
        msg = text.format(args=args) if "{args}" in text else text
        await trigger_target_event(update.effective_chat.id, msg)
        await update.message.reply_text(f"POTATA: Done ✅")
    return _handler


FUN_COMMANDS = {
    "nuke":         "☢️ **TACTICAL NUKE:** {args} 💥",
    "earthquake":   "🌍 **SERVER EARTHQUAKE:** Magnitude 9.9 tectonic shift! 🫨",
    "blackout":     "🌑 **GRID BLACKOUT:** Power cut across all nodes ⚡",
    "alien":        "👽 **ALIEN ABDUCTION:** UFO beaming users into deep space 🛸",
    "zombie":       "🧟 **ZOMBIE OUTBREAK:** Infection spreading. Quarantine active ☣️",
    "weather":      "⛈️ **EXTREME WEATHER:** Cyber-blizzard flooding server ports ❄️",
    "inflation":    "📈 **HYPER INFLATION:** Currency dropped to zero. Everyone broke 📉",
    "lockdown":     "🚨 **DEFCON 1 LOCKDOWN:** Military perimeter established 🛡️",
    "purge":        "🧹 **THE PURGE:** All restrictions suspended for 12 hours 🔪",
    "party":        "🥳 **RAVE PARTY:** Laser lights activated across the grid 🎉",
    "reverse":      "🔄 **REALITY REVERSE:** Up is down, left is right 🙃",
    "tsunami":      "🌊 **MEGA TSUNAMI:** Data wave crashing through firewalls 🏊",
    "meteor":       "☄️ **METEOR IMPACT:** Rock colliding into chat sector zero 💥",
    "eclipse":      "🌑 **SOLAR ECLIPSE:** Complete network darkness 🌌",
    "hack":         "💻 **MAINFRAME BREACH:** Downloading search histories… 100% 🕵️",
    "fakeban":      "🎭 **FAKE BAN ALERT:** Target sweating bullets 😭",
    "fakerestart":  "🔄 **FAKE REBOOT:** Server self-destruct initiated… Just kidding 😂",
    "matrix":       "💊 **RED PILL SWALLOWED:** Welcome to reality 🟢",
    "ghost":        "👻 **GHOST PROTOCOL:** Stealth mode active. Signature hidden 🕶️",
    "bounty":       "🎯 **BOUNTY PLACED:** 10,000 credits for finding the biggest bug 💰",
    "lottery":      "🎰 **JACKPOT:** Mega-lottery drawn. Winner takes all 💸",
    "casino":       "🎲 **HIGH ROLLER:** Casino tables open. House always wins 🎰",
    "jail":         "⛓️ **SERVER JAIL:** Sentenced to hard labor in formatting mines ⛏️",
    "pardon":       "🕊️ **ROYAL PARDON:** All sentences wiped clean 🙌",
    "fakeadmin":    "👑 **PROMOTION GLITCH:** Fake admin privileges for 5 seconds 🤡",
    "fakewarn":     "⚠️ **PHANTOM WARNING:** 3/3 strikes. Account pending deletion 💀",
    "mindwipe":     "🌀 **MEMORY WIPE:** Neural cache formatting. What were we discussing? 🤔",
    "firewall":     "🛡️ **FIREWALL MAXED:** Perimeter shields at 100% 🔥",
    "overload":     "⚡ **CORE OVERLOAD:** Reactors past thermal limits! Meltdown 🌡️",
    "sync":         "🔗 **DEEP SYNC:** Bot 1 and Bot 2 neural networks cross-linked 🧠",
    "wipe_logs":    "🧹 **LOGSCRUBBER:** All forensic evidence erased 🧽",
    "signal_boost": "📡 **SIGNAL BOOST:** Broadcasting across global channels 🔊",
    "stealth":      "🥷 **STEALTH MODE:** Routing hidden behind proxy layers 🕶️",
    "quantum":      "⚛️ **QUANTUM TUNNELING:** Bypassing restrictions via wormhole 🌀",
    "overclock":    "🚀 **CPU OVERCLOCK:** Processing boosted 500% ⚡",
    "shield_down":  "⚠️ **SHIELDS LOWERED:** Running fully exposed. Danger! 💀",
    "emergency":    "🛑 **EMERGENCY STOP:** All background operations halted 🚨",
    "globalwipe":   "🧹 **GLOBAL PURGE:** Records wiped across all server nodes 🧼",
    "serverping":   None,  # handled separately
    "sysmetrics":   None,  # handled separately
}


@admin_only
async def cmd_serverping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("POTATA: Pong! 1ms latency ⚡")


@admin_only
async def cmd_sysmetrics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("POTATA: Telemetry: Master CPU 0.1%, Node Sync 100% 🟢")


@admin_only
async def cmd_globalannounce(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ann = " ".join(context.args) if context.args else "System-wide broadcast!"
    await trigger_target_event(update.effective_chat.id, f"🌐 **GLOBAL ANNOUNCEMENT:** {ann}")
    await update.message.reply_text(f"POTATA: Announced ✅")


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    app = ApplicationBuilder().token(MASTER_TOKEN).build()

    # Start / help
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("adminhelp", admin_help))

    # Interactive menu buttons
    app.add_handler(CallbackQueryHandler(button_callback_handler))

    # 🔴 Real moderation commands
    app.add_handler(CommandHandler("checkuser", cmd_checkuser))
    app.add_handler(CommandHandler("ban", cmd_ban))
    app.add_handler(CommandHandler("kick", cmd_kick))
    app.add_handler(CommandHandler("stopspam", cmd_stopspam))
    app.add_handler(CommandHandler("global", cmd_global))
    app.add_handler(CommandHandler("event", cmd_event))

    # 🎭 Fun commands auto-registered from FUN_COMMANDS dict
    for cmd_name, text in FUN_COMMANDS.items():
        if text is not None:
            app.add_handler(CommandHandler(cmd_name, _fun(text)))

    # Separately handled fun commands
    app.add_handler(CommandHandler("serverping", cmd_serverping))
    app.add_handler(CommandHandler("sysmetrics", cmd_sysmetrics))
    app.add_handler(CommandHandler("globalannounce", cmd_globalannounce))

    # GIF mirror
    app.add_handler(MessageHandler(filters.ANIMATION, mirror_gif_handler))

    print("POTATA Advanced Controller live 🚀🔥")
    app.run_polling()


if __name__ == "__main__":
    import time
    while True:
        try:
            main()
        except Exception as e:
            print(f"Bot crashed: {e}. Restarting...")
            time.sleep(3)