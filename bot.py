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

BOT_TOKEN = os.environ.get("BOT_TOKEN")

YTDLP_BASE_OPTS = {
    "cookiefile": "cookies.txt",
    "quiet": True,
    "no_warnings": True,
}

# ───────────────── START ─────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Send me a YouTube link\n\n"
        "⚡ Fast 360p\n"
        "🎵 MP3 Small\n\n"
        "Created by EJ ❤️"
    )

# ───────────────── LINK HANDLER ─────────────────
async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    if "youtu" not in url:
        await update.message.reply_text("❌ Send a valid YouTube link")
        return

    context.user_data["url"] = url

    keyboard = [
        [InlineKeyboardButton("🎥 360p (Fast)", callback_data="v360")],
        [InlineKeyboardButton("🎵 Audio (MP3)", callback_data="mp3")],
    ]

    await update.message.reply_text(
        "✅ Link saved!\n👇 Choose option",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

# ───────────────── DOWNLOAD ─────────────────
async def download_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    url = context.user_data.get("url")
    if not url:
        await query.edit_message_text("❌ Link expired. Send again.")
        return

    await query.edit_message_text("⏳ Downloading...")

    try:
        if query.data == "v360":
            ydl_opts = {
                **YTDLP_BASE_OPTS,
                "format": "bestvideo[height<=360]+bestaudio/best[height<=360]",
                "outtmpl": "video.mp4",
                "merge_output_format": "mp4",
            }
            filename = "video.mp4"
            send_type = "video"

        else:  # mp3
            ydl_opts = {
                **YTDLP_BASE_OPTS,
                "format": "bestaudio/best",
                "outtmpl": "audio.%(ext)s",
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "96",
                    }
                ],
            }
            filename = "audio.mp3"
            send_type = "audio"

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # File size check (Telegram limit ~50MB)
        if os.path.getsize(filename) > 48 * 1024 * 1024:
            await query.edit_message_text("❌ File too large. Try another video.")
            os.remove(filename)
            return

        if send_type == "video":
            await context.bot.send_video(
                chat_id=query.message.chat_id,
                video=open(filename, "rb"),
                supports_streaming=True,
            )
        else:
            await context.bot.send_audio(
                chat_id=query.message.chat_id,
                audio=open(filename, "rb"),
            )

        os.remove(filename)

    except Exception as e:
        await query.edit_message_text(f"❌ Failed:\n{str(e)[:200]}")

# ───────────────── MAIN ─────────────────
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    app.add_handler(CallbackQueryHandler(download_handler))

    print("✅ Bot started")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
