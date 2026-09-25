"""
main.py — Render entry point.

Launches both Telegram bots in background threads and exposes a minimal
Flask HTTP server on the PORT Render injects.  Render's health-check hits
the HTTP endpoint, keeping the free-tier Web Service alive.
"""

import os
import time
import threading
import logging

from flask import Flask

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
log = logging.getLogger(__name__)

# ── Flask keep-alive server ──────────────────────────────────────────────────

app = Flask(__name__)


@app.route("/")
def index():
    return "PT Core System Hub is live 🚀", 200


@app.route("/health")
def health():
    return "OK", 200


def run_flask():
    port = int(os.environ.get("PORT", 8080))
    log.info("Keep-alive server starting on port %s", port)
    app.run(host="0.0.0.0", port=port, use_reloader=False)


# ── Bot runners ──────────────────────────────────────────────────────────────

def run_bot():
    """Run bot.py's main loop with auto-restart on crash."""
    import bot
    while True:
        try:
            log.info("Starting main bot (bot.py)...")
            bot.main()
        except Exception as exc:
            log.error("main bot crashed: %s - restarting in 5 s", exc)
            time.sleep(5)


def run_admin_bot():
    """Run admin_bot.py's main loop with auto-restart on crash."""
    import admin_bot
    while True:
        try:
            log.info("Starting admin bot (admin_bot.py)...")
            admin_bot.main()
        except Exception as exc:
            log.error("admin bot crashed: %s - restarting in 5 s", exc)
            time.sleep(5)


# ── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Start both bots as daemon threads so they die with the main process
    threading.Thread(target=run_bot, daemon=True, name="bot").start()
    threading.Thread(target=run_admin_bot, daemon=True, name="admin_bot").start()

    # Flask runs in the main thread (Render's health-check requires it)
    run_flask()
