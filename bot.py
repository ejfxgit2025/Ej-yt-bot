import os
import glob
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")

keyboard = InlineKeyboardMarkup([
    [InlineKeyboardButton("🎥 360p", callback_data="360")],
    [InlineKeyboardButton("🎥 720p", callback_data="720")],
    [InlineKeyboardButton("🎵 Audio", callback_data="audio")],
])

def clean_files():
    for f in glob.glob("*.*"):
        if f.endswith(("mp4", "webm", "m4a", "mkv")):
            os.remove(f)

# ---------- START ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔥 *EJ YT Downloader*\n\n"
        "📥 Send YouTube link\n"
        "👇 Choose option\n\n"
        "🤖 Created by EJ",
        parse_mode="Markdown",
        reply_markup=keyboard,
    )

# ---------- SAVE URL ----------
async def save_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if "youtube.com" not in url and "youtu.be" not in url:
        await update.message.reply_text("❌ Send a valid YouTube link")
        return

    context.user_data["url"] = url
    await update.message.reply_text(
        "✅ Link saved!\n👇 Choose option",
        reply_markup=keyboard,
    )

# ---------- BUTTON ----------
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    url = context.user_data.get("url")
    if not url:
        await query.message.reply_text("❌ Send link first")
        return

    clean_files()
    await query.message.reply_text("⏳ Downloading...")

    choice = query.data

    # AUDIO (NO FFMPEG, WORKS)
    if choice == "audio":
        ydl_opts = {
            "format": "bestaudio",
            "outtmpl": "audio.%(ext)s",
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        file = glob.glob("audio.*")[0]
        await query.message.reply_audio(open(file, "rb"))
        clean_files()
        return

    # VIDEO
    ydl_opts = {
        "format": f"best[height<={choice}]",
        "outtmpl": "video.%(ext)s",
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    file = glob.glob("video.*")[0]
    await query.message.reply_video(open(file, "rb"))
    clean_files()

# ---------- MAIN ----------
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, save_url))
    app.add_handler(CallbackQueryHandler(button))
    app.run_polling()

if __name__ == "__main__":
    main()
