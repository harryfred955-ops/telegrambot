import logging
import os
import httpx
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

MASTER_TOKEN = os.environ["MASTER_BOT_TOKEN"]
TARGET_BOT_TOKEN = os.environ["TARGET_BOT_TOKEN"]
TARGET_API_TOKEN = os.environ["TARGET_API_TOKEN"]

# Authorized Owner Username
OWNER_USERNAME = os.environ.get("OWNER_USERNAME", "marco51375")

def is_authorized(user) -> bool:
    if not user:
        return False
    if user.username and user.username.lower() == OWNER_USERNAME.lower():
        return True
    return False

def admin_only(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        if not user or not is_authorized(user):
            await update.message.reply_text("POTATA: ❌ ACCESS DENIED!", parse_mode="Markdown")
            return
        return await func(update, context)
    return wrapper

# Instant event trigger (Zero loading bar on admin bot for max speed!)
async def trigger_target_event(chat_id, event_text, reply_markup=None):
    api_url = f"https://api.telegram.org/bot{TARGET_API_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": f"POTATA: {event_text}",
        "parse_mode": "Markdown"
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup.to_dict()

    async with httpx.AsyncClient() as client:
        await client.post(api_url, json=payload)

# Mirror GIF/Animation to Target Bot instantly with optional interactive buttons
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

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("⚡ Open Command Grid", callback_data="menu_main")],
        [InlineKeyboardButton("🛡️ System Metrics", callback_data="menu_metrics"),
         InlineKeyboardButton("🚀 Launch Protocol", callback_data="menu_launch")]
    ])
    await update.message.reply_text(
        "POTATA: Advanced Cyber-Core Online 🌌. Choose your interface matrix below, cuh:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

@admin_only
async def admin_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("👑 Power Trips", callback_data="cat_power"),
         InlineKeyboardButton("🌍 Global Events", callback_data="cat_global")],
        [InlineKeyboardButton("🎭 Troll Matrix", callback_data="cat_trolls"),
         InlineKeyboardButton("🛡️ Core Systems", callback_data="cat_systems")],
        [InlineKeyboardButton("🔙 Main Menu", callback_data="menu_main")]
    ])
    await update.message.reply_text(
        "POTATA: ⚡ **ADVANCED CONTROL DECK (50+ COMMANDS)**\n\n"
        "Select a category matrix below or use standard chat commands instantly:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

# Fixed Interactive Callback Query Handler with complete routing
async def button_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "menu_main":
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("👑 Power Trips", callback_data="cat_power"),
             InlineKeyboardButton("🌍 Global Events", callback_data="cat_global")],
            [InlineKeyboardButton("🎭 Troll Matrix", callback_data="cat_trolls"),
             InlineKeyboardButton("🛡️ Core Systems", callback_data="cat_systems")],
            [InlineKeyboardButton("📊 System Metrics", callback_data="menu_metrics"),
             InlineKeyboardButton("🚀 Launch Info", callback_data="menu_launch")]
        ])
        await query.edit_message_text(
            "POTATA: ⚡ **COMMAND GRID MATRIX**\n\nSelect a module category below, cuh:", 
            reply_markup=keyboard, 
            parse_mode="Markdown"
        )
    
    elif data == "menu_metrics":
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Grid", callback_data="menu_main")]])
        await query.edit_message_text(
            "POTATA: 📊 **Telemetry:** Master CPU 0.01% | Node Sync: 100% | Latency: 0.4ms 🟢", 
            reply_markup=keyboard, 
            parse_mode="Markdown"
        )
    
    elif data == "menu_launch":
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Grid", callback_data="menu_main")]])
        await query.edit_message_text(
            "POTATA: 🚀 All 50+ protocols armed and ready for instant deployment, cuh!", 
            reply_markup=keyboard, 
            parse_mode="Markdown"
        )
    
    elif data == "cat_power":
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Grid", callback_data="menu_main")]])
        await query.edit_message_text(
            "POTATA: 👑 **Power Commands:** `/kick` `/ban` `/mute` `/demote` `/glitch` `/nuke` `/warn` `/tax` `/slap` `/roast` `/smite` `/vaporize`", 
            reply_markup=keyboard, 
            parse_mode="Markdown"
        )
    elif data == "cat_global":
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Grid", callback_data="menu_main")]])
        await query.edit_message_text(
            "POTATA: 🌍 **Global Events:** `/earthquake` `/blackout` `/alien` `/zombie` `/weather` `/inflation` `/lockdown` `/purge` `/party` `/reverse` `/tsunami` `/meteor` `/eclipse`", 
            reply_markup=keyboard, 
            parse_mode="Markdown"
        )
    elif data == "cat_trolls":
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Grid", callback_data="menu_main")]])
        await query.edit_message_text(
            "POTATA: 🎭 **Troll Matrix:** `/fakeban` `/hack` `/fakerestart` `/matrix` `/ghost` `/bounty` `/lottery` `/casino` `/jail` `/pardon` `/fakeadmin` `/fakewarn` `/mindwipe`", 
            reply_markup=keyboard, 
            parse_mode="Markdown"
        )
    elif data == "cat_systems":
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Grid", callback_data="menu_main")]])
        await query.edit_message_text(
            "POTATA: 🛡️ **Core Systems:** `/firewall` `/overload` `/sync` `/wipe_logs` `/signal_boost` `/stealth` `/quantum` `/overclock` `/shield_down` `/emergency` `/globalannounce` `/globalwipe` `/serverping` `/sysmetrics`", 
            reply_markup=keyboard, 
            parse_mode="Markdown"
        )
    
    elif data == "btn_replay":
        await query.message.reply_text("POTATA: 🎞️ Media loop packet re-injected into the target node successfully!")
    elif data == "btn_boost":
        await query.message.reply_text("POTATA: ⚡ Node thread supercharged by 1000%! We ball 🚀")

# ==========================================
# 🚀 FULL 50+ COMMAND IMPLEMENTATIONS
# ==========================================

@admin_only
async def cmd_kick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    r = " ".join(context.args) if context.args else "Power trip active"
    await trigger_target_event(update.effective_chat.id, f"Air kicked target node: {r} 💀")
    await update.message.reply_text(f"POTATA: Air kick executed -> {r}")

@admin_only
async def cmd_ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    r = " ".join(context.args) if context.args else "Shadow realm bound"
    await trigger_target_event(update.effective_chat.id, f"Dimension ban enforced: {r} 😭🙏")
    await update.message.reply_text(f"POTATA: Dimension ban deployed -> {r}")

@admin_only
async def cmd_mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    r = " ".join(context.args) if context.args else "Absolute silence"
    await trigger_target_event(update.effective_chat.id, f"Chat lockdown active: {r} 🤫")
    await update.message.reply_text(f"POTATA: Silence enforced -> {r}")

@admin_only
async def cmd_demote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    r = " ".join(context.args) if context.args else "Stripped of rank"
    await trigger_target_event(update.effective_chat.id, f"DEMOTION WARNING: {r}")
    await update.message.reply_text(f"POTATA: Demotion sequence sent -> {r}")

@admin_only
async def cmd_glitch(update: Update, context: ContextTypes.DEFAULT_TYPE):
    r = " ".join(context.args) if context.args else "Matrix lines corrupting"
    await trigger_target_event(update.effective_chat.id, f"⚠️ SYSTEM GLITCH: {r} 🌀")
    await update.message.reply_text(f"POTATA: Glitch deployed -> {r}")

@admin_only
async def cmd_nuke(update: Update, context: ContextTypes.DEFAULT_TYPE):
    r = " ".join(context.args) if context.args else "History vaporized"
    await trigger_target_event(update.effective_chat.id, f"☢️ TACTICAL NUKE: {r} 💥")
    await update.message.reply_text(f"POTATA: Cluster nuke dropped -> {r}")

@admin_only
async def cmd_warn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    r = " ".join(context.args) if context.args else "Final warning issued"
    await trigger_target_event(update.effective_chat.id, f"🚨 WARNING STRIKE: {r} ⚠️")
    await update.message.reply_text(f"POTATA: Strike warning sent -> {r}")

@admin_only
async def cmd_tax(update: Update, context: ContextTypes.DEFAULT_TYPE):
    r = " ".join(context.args) if context.args else "Hand over the bags cuh!"
    await trigger_target_event(update.effective_chat.id, f"💸 MANDATORY TAX: {r} 💰")
    await update.message.reply_text(f"POTATA: Tax collection dispatched -> {r}")

@admin_only
async def cmd_slap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    r = " ".join(context.args) if context.args else "Virtual reality slap"
    await trigger_target_event(update.effective_chat.id, f"👋 SLAPPED across the server grid: {r} 💥")
    await update.message.reply_text(f"POTATA: Slap delivered -> {r}")

@admin_only
async def cmd_roast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    r = " ".join(context.args) if context.args else "Absolute violation"
    await trigger_target_event(update.effective_chat.id, f"🔥 ROASTED by owner: {r} 💀")
    await update.message.reply_text(f"POTATA: Roast deployed -> {r}")

@admin_only
async def cmd_smite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = " ".join(context.args) if context.args else "random target"
    await trigger_target_event(update.effective_chat.id, f"⚡ **DIVINE SMITE:** Lightning bolt struck {target} straight from the heavens! 🌩️")
    await update.message.reply_text(f"POTATA: Smite executed on {target}")

@admin_only
async def cmd_vaporize(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = " ".join(context.args) if context.args else "target node"
    await trigger_target_event(update.effective_chat.id, f"⚛️ **VAPORIZED:** {target} turned into pure subatomic digital dust. Gone! 💨")
    await update.message.reply_text(f"POTATA: Vaporization complete for {target}")

# Global Events
@admin_only
async def cmd_earthquake(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await trigger_target_event(update.effective_chat.id, "🌍 **SERVER EARTHQUAKE:** Magnitude 9.9 tectonic shift shaking all chat rooms! 🫨")
    await update.message.reply_text("POTATA: Earthquake event triggered!")

@admin_only
async def cmd_blackout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await trigger_target_event(update.effective_chat.id, "🌑 **GRID BLACKOUT:** Power cut across all local nodes. Generators online ⚡")
    await update.message.reply_text("POTATA: Blackout event initiated!")

@admin_only
async def cmd_alien(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await trigger_target_event(update.effective_chat.id, "👽 **ALIEN ABDUCTION:** UFO tractor-beaming random users into deep space 🛸")
    await update.message.reply_text("POTATA: Alien invasion deployed!")

@admin_only
async def cmd_zombie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await trigger_target_event(update.effective_chat.id, "🧟 **ZOMBIE OUTBREAK:** Infection spreading rapidly through logs. Quarantine active ☣️")
    await update.message.reply_text("POTATA: Zombie outbreak live!")

@admin_only
async def cmd_weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await trigger_target_event(update.effective_chat.id, "⛈️ **EXTREME WEATHER:** Cyber-blizzard and digital lightning storms flooding server ports ❄️")
    await update.message.reply_text("POTATA: Weather anomaly simulated!")

@admin_only
async def cmd_inflation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await trigger_target_event(update.effective_chat.id, "📈 **HYPER INFLATION:** Currency value dropped to zero. Everyone broke overnight 📉")
    await update.message.reply_text("POTATA: Economic collapse live!")

@admin_only
async def cmd_lockdown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await trigger_target_event(update.effective_chat.id, f"🚨 **DEFCON 1 LOCKDOWN:** Military perimeter established by owner `{OWNER_USERNAME}`. No passage! 🛡️")
    await update.message.reply_text("POTATA: DEFCON 1 engaged!")

@admin_only
async def cmd_purge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await trigger_target_event(update.effective_chat.id, "🧹 **THE PURGE:** All laws and restrictions suspended for 12 hours 🔪")
    await update.message.reply_text("POTATA: Purge event started!")

@admin_only
async def cmd_party(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await trigger_target_event(update.effective_chat.id, "🥳 **RAVE PARTY:** Laser lights and VIP energy activated across the grid 🎉")
    await update.message.reply_text("POTATA: Rave party activated!")

@admin_only
async def cmd_reverse(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await trigger_target_event(update.effective_chat.id, "🔄 **REALITY REVERSE:** Up is down, left is right, admins are peasants 🙃")
    await update.message.reply_text("POTATA: Reality flip executed!")

@admin_only
async def cmd_tsunami(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await trigger_target_event(update.effective_chat.id, "🌊 **MEGA TSUNAMI:** Massive digital data wave crashing through firewalls! Swim upstream 🏊‍♂️")
    await update.message.reply_text("POTATA: Tsunami unleashed!")

@admin_only
async def cmd_meteor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await trigger_target_event(update.effective_chat.id, "☄️ **METEOR IMPACT:** Space rock colliding straight into chat sector zero 💥")
    await update.message.reply_text("POTATA: Meteor strike deployed!")

@admin_only
async def cmd_eclipse(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await trigger_target_event(update.effective_chat.id, "🌑 **SOLAR ECLIPSE:** Complete network darkness. Communication channels pitch black 🌌")
    await update.message.reply_text("POTATA: Eclipse protocol active!")

# Trolls & Psychological
@admin_only
async def cmd_fakeban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await trigger_target_event(update.effective_chat.id, "🎭 **PSYCHOLOGICAL WARFARE:** Fake permanent ban alert triggered. Target sweating bullets 😭")
    await update.message.reply_text("POTATA: Fake ban triggered!")

@admin_only
async def cmd_hack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await trigger_target_event(update.effective_chat.id, "💻 **MAINFRAME BREACH:** Downloading user search histories and exposing secrets... 100% 🕵️‍♂️")
    await update.message.reply_text("POTATA: Fake hack executed!")

@admin_only
async def cmd_fakerestart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await trigger_target_event(update.effective_chat.id, "🔄 **FAKE REBOOT:** Server self-destruct initiated... Just kidding, we ball 😂")
    await update.message.reply_text("POTATA: Fake reboot sent!")

@admin_only
async def cmd_matrix(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await trigger_target_event(update.effective_chat.id, "💊 **RED PILL SWALLOWED:** You have exited the simulation. Welcome to reality 🟢")
    await update.message.reply_text("POTATA: Matrix pill dropped!")

@admin_only
async def cmd_ghost(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await trigger_target_event(update.effective_chat.id, "👻 **GHOST PROTOCOL:** Stealth mode active. Owner signature hidden from radar 🕶️")
    await update.message.reply_text("POTATA: Ghost protocol online!")

@admin_only
async def cmd_bounty(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await trigger_target_event(update.effective_chat.id, "🎯 **BOUNTY PLACED:** 10,000 credits rewarded for finding the biggest bug 💰")
    await update.message.reply_text("POTATA: Bounty board updated!")

@admin_only
async def cmd_lottery(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await trigger_target_event(update.effective_chat.id, "🎰 **JACKPOT:** Mega-lottery ticket drawn. Winner takes all bags 💸")
    await update.message.reply_text("POTATA: Lottery simulated!")

@admin_only
async def cmd_casino(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await trigger_target_event(update.effective_chat.id, "🎲 **HIGH ROLLER:** Casino tables open. House always wins, cuh! 🎰")
    await update.message.reply_text("POTATA: Casino mode online!")

@admin_only
async def cmd_jail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await trigger_target_event(update.effective_chat.id, "⛓️ **SERVER JAIL:** Sentenced to hard labor in formatting mines. No bail! ⛏️")
    await update.message.reply_text("POTATA: Jail enforced!")

@admin_only
async def cmd_pardon(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await trigger_target_event(update.effective_chat.id, "🕊️ **ROYAL PARDON:** All prisoner sentences wiped clean by grace. Free at last 🙌")
    await update.message.reply_text("POTATA: Pardon granted!")

@admin_only
async def cmd_fakeadmin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await trigger_target_event(update.effective_chat.id, "👑 **PROMOTION GLITCH:** System error granted fake owner privileges for 5 seconds 🤡")
    await update.message.reply_text("POTATA: Fake admin glitch sent!")

@admin_only
async def cmd_fakewarn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await trigger_target_event(update.effective_chat.id, "⚠️ **PHANTOM WARNING:** 3/3 moderation strikes recorded. Account pending deletion... 💀")
    await update.message.reply_text("POTATA: Phantom warning triggered!")

@admin_only
async def cmd_mindwipe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await trigger_target_event(update.effective_chat.id, "🌀 **MEMORY WIPE:** Neural cache formatting in progress. What were we talking about? 🤔")
    await update.message.reply_text("POTATA: Mind wipe simulated!")

# System & Network
@admin_only
async def cmd_firewall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await trigger_target_event(update.effective_chat.id, "🛡️ **FIREWALL MAXED:** Perimeter defense shields raised to 100% capacity 🔥")
    await update.message.reply_text("POTATA: Firewall maxed out!")

@admin_only
async def cmd_overload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await trigger_target_event(update.effective_chat.id, "⚡ **CORE OVERLOAD:** Reactor cores pushing past safe thermal limits! Meltdown 🌡️")
    await update.message.reply_text("POTATA: Core overload warning dispatched!")

@admin_only
async def cmd_sync(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await trigger_target_event(update.effective_chat.id, "🔗 **DEEP SYNCHRONIZATION:** Bot 1 and Bot 2 neural networks cross-linked 🧠")
    await update.message.reply_text("POTATA: Neural sync completed!")

@admin_only
async def cmd_wipe_logs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await trigger_target_event(update.effective_chat.id, "🧹 **LOGSCRUBBER:** All forensic evidence and chat histories permanently erased 🧽")
    await update.message.reply_text("POTATA: Logs wiped clean!")

@admin_only
async def cmd_signal_boost(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await trigger_target_event(update.effective_chat.id, "📡 **SIGNAL BOOST:** Broadcasting frequency amplified across global channels 🔊")
    await update.message.reply_text("POTATA: Signal boosted!")

@admin_only
async def cmd_stealth(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await trigger_target_event(update.effective_chat.id, "🥷 **STEALTH MODE:** Active routing hidden behind proxy layers. Untraceable 🕶️")
    await update.message.reply_text("POTATA: Stealth mode enabled!")

@admin_only
async def cmd_quantum(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await trigger_target_event(update.effective_chat.id, "⚛️ **QUANTUM TUNNELING:** Bypassing standard network restrictions via wormhole bridge 🌀")
    await update.message.reply_text("POTATA: Quantum tunnel opened!")

@admin_only
async def cmd_overclock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await trigger_target_event(update.effective_chat.id, "🚀 **CPU OVERCLOCK:** Processing speeds boosted by 500%. Lightning speed active ⚡")
    await update.message.reply_text("POTATA: CPU overclocked!")

@admin_only
async def cmd_shield_down(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await trigger_target_event(update.effective_chat.id, "⚠️ **SHIELDS LOWERED:** Running completely exposed to external traffic lines. Danger! 💀")
    await update.message.reply_text("POTATA: Shields dropped!")

@admin_only
async def cmd_emergency(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await trigger_target_event(update.effective_chat.id, "🛑 **EMERGENCY STOP:** All background operations halted instantly by system governor 🚨")
    await update.message.reply_text("POTATA: Emergency brake pulled!")

@admin_only
async def cmd_global_announce(update: Update, context: ContextTypes.DEFAULT_TYPE):
    announcement = " ".join(context.args) if context.args else "System-wide broadcast alert!"
    await trigger_target_event(update.effective_chat.id, f"🌐 **GLOBAL ANNOUNCEMENT:** {announcement}")
    await update.message.reply_text(f"POTATA: {announcement}")

@admin_only
async def cmd_global_wipe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await trigger_target_event(update.effective_chat.id, "🧹 **GLOBAL PURGE:** Wiped records clean across all connected server nodes simultaneously! 🧼")
    await update.message.reply_text("POTATA: Global cluster wipe executed!")

@admin_only
async def cmd_serverping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("POTATA: Pong! 1ms latency ⚡")

@admin_only
async def cmd_sysmetrics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("POTATA: Telemetry: Master CPU 0.1%, Node Sync 100% optimal 🟢")

def main():
    app = ApplicationBuilder().token(MASTER_TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("adminhelp", admin_help))
    
    # Callback query handler for interactive buttons
    app.add_handler(CallbackQueryHandler(button_callback_handler))

    # Mapping all 50+ commands
    commands_map = {
        "kick": cmd_kick, "ban": cmd_ban, "mute": cmd_mute, "demote": cmd_demote,
        "glitch": cmd_glitch, "nuke": cmd_nuke, "warn": cmd_warn, "tax": cmd_tax,
        "slap": cmd_slap, "roast": cmd_roast, "smite": cmd_smite, "vaporize": cmd_vaporize,
        "earthquake": cmd_earthquake, "blackout": cmd_blackout, "alien": cmd_alien, 
        "zombie": cmd_zombie, "weather": cmd_weather, "inflation": cmd_inflation, 
        "lockdown": cmd_lockdown, "purge": cmd_purge, "party": cmd_party, 
        "reverse": cmd_reverse, "tsunami": cmd_tsunami, "meteor": cmd_meteor, "eclipse": cmd_eclipse,
        "fakeban": cmd_fakeban, "hack": cmd_hack, "fakerestart": cmd_fakerestart,
        "matrix": cmd_matrix, "ghost": cmd_ghost, "bounty": cmd_bounty,
        "lottery": cmd_lottery, "casino": cmd_casino, "jail": cmd_jail,
        "pardon": cmd_pardon, "fakeadmin": cmd_fakeadmin, "fakewarn": cmd_fakewarn, "mindwipe": cmd_mindwipe,
        "firewall": cmd_firewall, "overload": cmd_overload,
        "sync": cmd_sync, "wipe_logs": cmd_wipe_logs, "signal_boost": cmd_signal_boost,
        "stealth": cmd_stealth, "quantum": cmd_quantum, "overclock": cmd_overclock,
        "shield_down": cmd_shield_down, "emergency": cmd_emergency,
        "globalannounce": cmd_global_announce, "globalwipe": cmd_global_wipe,
        "serverping": cmd_serverping, "sysmetrics": cmd_sysmetrics
    }

    for cmd_name, func in commands_map.items():
        app.add_handler(CommandHandler(cmd_name, func))
    
    # GIF Mirror Handler with buttons attached
    app.add_handler(MessageHandler(filters.ANIMATION, mirror_gif_handler))

    print("POTATA Advanced Interactive Controller live, cuh! 🚀🔥")
    app.run_polling()

if __name__ == "__main__":
    while True:
        try:
            main()
        except Exception as e:
            print(f"Bot crashed: {e}. Restarting...")
            import time
            time.sleep(3)