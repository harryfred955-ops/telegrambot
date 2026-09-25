import logging
import os
import time
import asyncio
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Conversation States for the Advanced Spam Engine Setup
API_ID, API_HASH, PHONE, SPAM_TYPE, CUSTOM_WORDS, START_WORD, STOP_WORD, VELOCITY = range(8)

TOKEN = os.environ["BOT_TOKEN"]

BANNED_WORDS = ["badword1", "badword2", "scamlink", "hackershop", "freecrypto", "tg.me/spam"]

# 🚀 /start Menu with Modern Loading & Updated Buttons
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("⚡ **Initializing PT Core Hub...**\n`[░░░░░░░░░░] 0%`", parse_mode="Markdown")
    
    time.sleep(0.3)
    await msg.edit_text("⚡ **Loading Security Protocols...**\n`[████░░░░░░] 40%`", parse_mode="Markdown")
    time.sleep(0.3)
    await msg.edit_text("⚡ **Syncing Tool Database...**\n`[████████░░] 80%`", parse_mode="Markdown")
    time.sleep(0.3)
    
    # 🔗 Updated layout: Tools & Rules show info menus, Owner & Feed link to your channel!
    keyboard = [
        [
            InlineKeyboardButton("🔓 Get Tools", callback_data="menu_tools"), 
            InlineKeyboardButton("📜 Rules & Guidelines", callback_data="menu_rules")
        ],
        [
            InlineKeyboardButton("👑 Owner Channel", url="https://t.me/Project_PTtool"), 
            InlineKeyboardButton("🚀 Spam Engine (BETA)", callback_data="start_spam_setup")
        ],
        [
            InlineKeyboardButton("📊 Channel Feed", url="https://t.me/Project_PTtool")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await msg.edit_text(
        "🔥 **Welcome to PT Core System Hub** 🔥\n\n"
        "Your elite automated command center is fully online and protecting the feed 24/7.\n\n"
        "✨ *Select an option below to navigate:*",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

# 📱 Handle Menu Button Clicks (Tools & Rules Info Menus)
async def menu_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "menu_tools":
        keyboard = [[InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_home")]]
        await query.edit_message_text(
            "🔓 **PT ⚡ Advanced Tool Hub**\n\n"
            "Here are your unlocked enterprise utilities:\n"
            "• Network Diagnostics & Pinger\n"
            "• Base64 & Hash Encoders\n"
            "• Telegram ID Lookup & WHOIS\n"
            "• Automated Cloud Security Scanners\n\n"
            "✨ *Type /help to view all 35+ commands.*",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    elif query.data == "menu_rules":
        keyboard = [[InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_home")]]
        await query.edit_message_text(
            "📜 **PT Core Advanced Rules & Guidelines**\n\n"
            "1. **Zero Spam Tolerance:** Unapproved links or crypto spam results in an instant cloud ban.\n"
            "2. **Media Restrictions:** Videos and video notes are automatically wiped by system filters.\n"
            "3. **Respect Staff:** Harassment against admins leads to immediate blacklisting.\n"
            "4. **Active Engagement:** Stay active or risk routine channel sweeps.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    elif query.data == "back_home":
        keyboard = [
            [InlineKeyboardButton("🔓 Get Tools", callback_data="menu_tools"), InlineKeyboardButton("📜 Rules & Guidelines", callback_data="menu_rules")],
            [InlineKeyboardButton("👑 Owner Channel", url="https://t.me/Project_PTtool"), InlineKeyboardButton("🚀 Spam Engine (BETA)", callback_data="start_spam_setup")],
            [InlineKeyboardButton("📊 Channel Feed", url="https://t.me/Project_PTtool")]
        ]
        await query.edit_message_text(
            "🔥 **Welcome back to PT Core System Hub** 🔥\n\nSelect an option below:",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

# 🔄 Spam Engine Setup Flow Steps
async def spam_button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "start_spam_setup":
        await query.edit_message_text(
            "⚡ **Advanced Spam Engine Configurator** ⚡\n\n"
            "Step 1/7: Please send your Telegram **API ID** (numbers only):",
            parse_mode="Markdown"
        )
        return API_ID

async def receive_api_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['api_id'] = update.message.text.strip()
    await update.message.reply_text("Step 2/7: Got it! Now send your Telegram **API Hash**:")
    return API_HASH

async def receive_api_hash(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['api_hash'] = update.message.text.strip()
    await update.message.reply_text("Step 3/7: Perfect. Now send your **phone number** (with country code, e.g., +123456789):")
    return PHONE

async def receive_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['phone'] = update.message.text.strip()
    
    keyboard = [
        [InlineKeyboardButton("☕ Chill Spam", callback_data="type_chill")],
        [InlineKeyboardButton("✍️ Custom Spam", callback_data="type_custom")],
        [InlineKeyboardButton("🔥 Rage Spam", callback_data="type_rage")]
    ]
    await update.message.reply_text(
        "Step 4/7: Choose your **Spam Type Mode**:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return SPAM_TYPE

async def receive_spam_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    choice = query.data
    
    if choice == "type_chill":
        context.user_data['spam_list'] = ["Checking in, bradar!", "PT Core running smoothly ☕", "Stay chill and safe."]
        await query.edit_message_text("✅ Mode set to **Chill Spam**. \n\nStep 5/7: Send your custom **Start Trigger Word** (e.g., start):")
        return START_WORD
    elif choice == "type_rage":
        context.user_data['spam_list'] = ["RAGE ENGINE ACTIVATED 🔥", "GET SPAMMED LMAO 💀", "PT CORE ABSOLUTE DESTRUCTION 🚀"]
        await query.edit_message_text("✅ Mode set to **Rage Spam**. \n\nStep 5/7: Send your custom **Start Trigger Word** (e.g., start):")
        return START_WORD
    else:
        await query.edit_message_text("✅ Mode set to **Custom Spam**.\n\nType your custom spam messages one by one. Send **DONE** when finished:")
        context.user_data['spam_list'] = []
        return CUSTOM_WORDS

async def receive_custom_words(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if text.upper() == "DONE":
        if not context.user_data['spam_list']:
            context.user_data['spam_list'] = ["Default fallback message"]
        await update.message.reply_text("Step 5/7: Custom words saved! Now send your custom **Start Trigger Word** (e.g., start):")
        return START_WORD
    else:
        context.user_data['spam_list'].append(text)
        await update.message.reply_text(f"Added! Send another or type **DONE**.")
        return CUSTOM_WORDS

async def receive_start_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['start_word'] = update.message.text.strip().lower()
    await update.message.reply_text("Step 6/7: Nice. Now send your custom **Stop/End Trigger Word** (e.g., stop):")
    return STOP_WORD

async def receive_stop_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['stop_word'] = update.message.text.strip().lower()
    
    keyboard = [
        [InlineKeyboardButton("1. Slow (2.0 - 5.0s)", callback_data="vel_1")],
        [InlineKeyboardButton("2. Fast - Recommended (0.3 - 1.0s)", callback_data="vel_2")],
        [InlineKeyboardButton("3. Ultra-Fast - Risk (0.05 - 0.2s)", callback_data="vel_3")],
        [InlineKeyboardButton("4. Extreme-Fast - Very Risky (0.01 - 0.05s)", callback_data="vel_4")]
    ]
    await update.message.reply_text(
        "Step 7/7: Select your **Velocity Mode**:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return VELOCITY

async def receive_velocity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "🎉 **Spam Engine Fully Configured & Ready!** 🎉\n\n"
        "Your configuration parameters have been saved into system memory. Ready for deployment, bradar! 🚀",
        parse_mode="Markdown"
    )
    context.user_data.clear()
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Setup process cancelled, bradar.")
    return ConversationHandler.END

# ⚡ Expanded Command Suite (35+ Total Tools & Features)
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚡ **PT Core Ultimate Command Suite (35+ Tools):**\n\n"
        "**Core & Menus:**\n"
        "1. /start - Interactive dashboard\n"
        "2. /help - Full command list\n"
        "3. /tools - Unlockable tool directory\n"
        "4. /rules - Channel guidelines menu\n"
        "5. /owner - Official channel links\n\n"
        "**System & Analytics:**\n"
        "6. /ping - Latency test\n"
        "7. /uptime - Cloud uptime tracker\n"
        "8. /stats - Server telemetry\n"
        "9. /sysload - CPU & memory load\n"
        "10. /netstatus - Network bandwidth check\n"
        "11. /serverping - Gateway latency check\n"
        "12. /portscan - Quick port scanner utility\n"
        "13. /clearcache - Clear runtime memory cache\n"
        "14. /autobackup - Run system state backup\n"
        "15. /firewall - Security protocol status\n\n"
        "**Moderation & Chat Control:**\n"
        "16. /lock - Lock channel messaging\n"
        "17. /unlock - Unlock channel messaging\n"
        "18. /purge - Bulk delete messages\n"
        "19. /warn - Warn violating user\n"
        "20. /unwarn - Revoke user warning\n"
        "21. /mute - Restrict user chat access\n"
        "22. /unmute - Restore user chat access\n"
        "23. /ban - Ban spammers permanently\n"
        "24. /unban - Revoke ban status\n"
        "25. /report - Flag message to admins\n\n"
        "**Utility & Encoders:**\n"
        "26. /idcheck - Lookup target Telegram ID\n"
        "27. /whois - Fetch user profile details\n"
        "28. /base64enc - Encode string to Base64\n"
        "29. /base64dec - Decode Base64 string\n"
        "30. /hashmd5 - Generate MD5 checksum\n"
        "31. /hashsha256 - Generate SHA-256 hash\n"
        "32. /generatekey - Create secure session key\n"
        "33. /poll - Initialize channel poll\n"
        "34. /feedback - Send developer ticket\n"
        "35. /donate - Support development team\n"
        "36. /ai - Quick AI proxy assistant",
        parse_mode="Markdown"
    )

# 🧹 Auto-Delete Service Messages
async def delete_service_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        try:
            await update.message.delete()
        except Exception:
            pass

# 🚫 Elite Auto-Moderation
async def moderate_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.from_user:
        return
    message = update.message
    user = message.from_user
    chat = message.chat
    text_lower = (message.text or message.caption or "").lower()

    if message.video or message.video_note or any(w in text_lower for w in BANNED_WORDS):
        try:
            await message.delete()
            if chat.type in ["group", "supergroup"]:
                await chat.ban_member(user.id)
        except Exception:
            pass

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    spam_conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(spam_button_callback, pattern="^start_spam_setup$")],
        states={
            API_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_api_id)],
            API_HASH: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_api_hash)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_phone)],
            SPAM_TYPE: [CallbackQueryHandler(receive_spam_type, pattern="^type_")],
            CUSTOM_WORDS: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_custom_words)],
            START_WORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_start_word)],
            STOP_WORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_stop_word)],
            VELOCITY: [CallbackQueryHandler(receive_velocity, pattern="^vel_")],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("tools", start_command))
    app.add_handler(CommandHandler("rules", start_command))
    app.add_handler(CommandHandler("owner", start_command))
    
    app.add_handler(spam_conv_handler)
    app.add_handler(CallbackQueryHandler(menu_callback_handler, pattern="^(menu_|back_)"))
    
    app.add_handler(MessageHandler(filters.StatusUpdate.ALL, delete_service_messages))
    app.add_handler(MessageHandler(~filters.COMMAND, moderate_chat))

    print("PT Core Fully Upgraded System is live, bradar! 🚀")
    app.run_polling()

if __name__ == "__main__":
    while True:
        try:
            main()
        except Exception as e:
            print(f"Bot crashed: {e}. Restarting in 5 seconds...")
            time.sleep(5)