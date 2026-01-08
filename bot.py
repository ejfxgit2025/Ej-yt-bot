import os
import yt_dlp
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")

KEYBOARD = InlineKeyboardMarkup([
    [InlineKeyboardButton("🎥 360p Video", callback_data="360")],
    [InlineKeyboardButton("🎥 720p Video", callback_data="720")],
    [InlineKeyboardButton("🎵 Audio", callback_data="audio")],
])

YDL_OPTS_BASE = {
    "quiet": True,
    "no_warnings": True,
    "skip_download": True,
    "force_ipv4": True,
    "cookiefile": "cookies.txt",
    "http_headers": {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    },
}

# ---------- START ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔥 *EJ YT Videos Downloader*\n\n"
        "📥 Send YouTube link\n"
        "👇 Choose option\n\n"
        "⚡ Link Mode (Fast)\n"
        "🤖 Created by EJ",
        parse_mode="Markdown",
        reply_markup=KEYBOARD,
    )

# ---------- SAVE LINK ----------
async def save_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    if "youtube.com" not in url and "youtu.be" not in url:
        await update.message.reply_text("❌ Send a valid YouTube link")
        return

    context.user_data["url"] = url
    await update.message.reply_text(
        "✅ Link saved\n👇 Choose option",
        reply_markup=KEYBOARD,
    )

# ---------- BUTTON ----------
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    url = context.user_data.get("url")
    if not url:
        await query.message.reply_text("❌ Send link first")
        return

    await query.message.reply_text("🔎 Fetching download link...")

    try:
        with yt_dlp.YoutubeDL(YDL_OPTS_BASE) as ydl:
            info = ydl.extract_info(url, download=False)
    except Exception:
        await query.message.reply_text(
            "❌ YouTube blocked this video\n"
            "🔁 Try another video"
        )
        return

    choice = query.data

    # ---------- AUDIO ----------
    if choice == "audio":
        for f in info.get("formats", []):
            if f.get("vcodec") == "none" and f.get("acodec") != "none":
                await query.message.reply_text(
                    f"🎵 *Audio Download*\n\n🔗 {f['url']}",
                    parse_mode="Markdown",
                )
                return

    # ---------- VIDEO ----------
    for f in info.get("formats", []):
        if (
            f.get("height") == int(choice)
            and f.get("vcodec") != "none"
            and f.get("acodec") != "none"
        ):
            await query.message.reply_text(
                f"🎥 *{choice}p Video Download*\n\n🔗 {f['url']}",
                parse_mode="Markdown",
            )
            return

    await query.message.reply_text("❌ Format not available")

# ---------- MAIN ----------
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, save_link))
    app.add_handler(CallbackQueryHandler(button))
    app.run_polling()

if __name__ == "__main__":
    main()

