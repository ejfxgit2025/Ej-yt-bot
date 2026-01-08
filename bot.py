import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
import yt_dlp

BOT_TOKEN = os.getenv("BOT_TOKEN")

BASE_DIR = os.getcwd()
COOKIE_FILE = os.path.join(BASE_DIR, "cookies.txt")

ydl_base_opts = {
    "quiet": True,
    "no_warnings": True,
    "cookies": COOKIE_FILE,
    "user_agent": "Mozilla/5.0",
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Send me a YouTube link\n\n"
        "🎥 360p Fast\n"
        "🎵 MP3 Small\n"
        "⚠️ Files >50MB may fail"
    )

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    context.user_data["url"] = url

    keyboard = [
        [InlineKeyboardButton("🎥 360p (Fast)", callback_data="360")],
        [InlineKeyboardButton("🎵 Audio (MP3)", callback_data="mp3")],
    ]

    await update.message.reply_text(
        "✅ Link saved!\n👇 Choose option",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

def yt_download(url, mode):
    if mode == "360":
        filename = "video.mp4"
        ydl_opts = {
            **ydl_base_opts,
            "format": "bv*[height<=360]+ba/b[height<=360]",
            "merge_output_format": "mp4",
            "outtmpl": filename,
        }
    else:
        filename = "audio.mp3"
        ydl_opts = {
            **ydl_base_opts,
            "format": "bestaudio",
            "outtmpl": "audio.%(ext)s",
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "128",
                }
            ],
        }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return filename

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    url = context.user_data.get("url")
    if not url:
        await query.edit_message_text("❌ No URL found")
        return

    await query.edit_message_text("⏳ Downloading...")

    try:
        filename = await asyncio.to_thread(
            yt_download, url, query.data
        )

        if query.data == "360":
            await query.message.reply_video(
                video=open(filename, "rb"),
                supports_streaming=True,
            )
        else:
            await query.message.reply_audio(
                audio=open(filename, "rb"),
            )

        os.remove(filename)

    except Exception as e:
        await query.message.reply_text(
            f"❌ Failed:\n{str(e)[:400]}"
        )

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    app.add_handler(CallbackQueryHandler(download))

    print("Bot started...")
    app.run_polling()

if __name__ == "__main__":
    main()
