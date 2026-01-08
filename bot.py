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

# ---------- START ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎥 360p", callback_data="360")],
        [InlineKeyboardButton("🎥 720p", callback_data="720")],
        [InlineKeyboardButton("🎥 1080p", callback_data="1080")],
        [InlineKeyboardButton("🎵 MP3", callback_data="mp3")],
    ]

    await update.message.reply_text(
        "🔥 *Fast YouTube Downloader*\n\n"
        "📥 Send YouTube link\n"
        "👇 Choose quality\n\n"
        "🤖 Created by EJ",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
    )

# ---------- SAVE URL ----------
async def save_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if "youtube.com" not in url and "youtu.be" not in url:
        await update.message.reply_text("❌ Send a valid YouTube link")
        return

    context.user_data["url"] = url
    await update.message.reply_text("✅ Link saved!\nNow choose quality 👇")

# ---------- BUTTON HANDLER ----------
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    url = context.user_data.get("url")
    if not url:
        await query.edit_message_text("❌ Send YouTube link first")
        return

    choice = query.data
    await query.edit_message_text("⏳ Downloading... Please wait")

    if choice == "mp3":
        ydl_opts = {
            "format": "bestaudio",
            "outtmpl": "audio.%(ext)s",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
            }],
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        await query.message.reply_audio(open("audio.mp3", "rb"))
        return

    ydl_opts = {
        "format": f"bestvideo[height<={choice}]+bestaudio/best",
        "outtmpl": "video.%(ext)s",
        "merge_output_format": "mp4",
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
