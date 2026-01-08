import os
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
    [InlineKeyboardButton("🎵 Audio (MP3)", callback_data="audio")],
])

# ---------- START ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔥 *EJ YT Downloader*\n\n"
        "📥 Send YouTube link\n"
        "👇 Choose format\n\n"
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

    choice = query.data
    await query.message.reply_text("⏳ Downloading...")

    # ---- AUDIO (M4A, WORKS WITHOUT FFMPEG) ----
    if choice == "audio":
        ydl_opts = {
            "format": "bestaudio[ext=m4a]/bestaudio",
            "outtmpl": "audio.%(ext)s",
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        await query.message.reply_audio(open("audio.m4a", "rb"))
        return

    # ---- VIDEO ----
    ydl_opts = {
        "format": f"best[height<={choice}][ext=mp4]",
        "outtmpl": "video.mp4",
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    await query.message.reply_video(open("video.mp4", "rb"))

# ---------- MAIN ----------
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, save_url))
    app.add_handler(CallbackQueryHandler(button))
    app.run_polling()

if __name__ == "__main__":
    main()
