import os, glob, asyncio
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
    [InlineKeyboardButton("🎥 360p (Fast)", callback_data="360")],
    [InlineKeyboardButton("🎵 Audio (Small)", callback_data="audio")],
])

def clean():
    for f in glob.glob("*.*"):
        if f.endswith(("mp4", "webm", "m4a")):
            os.remove(f)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔥 *EJ YT Downloader*\n\n"
        "📥 Send YouTube link\n"
        "⚠️ Max 50MB (Telegram limit)\n\n"
        "🤖 Created by EJ",
        parse_mode="Markdown",
        reply_markup=keyboard,
    )

async def save_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if "youtube.com" not in url and "youtu.be" not in url:
        await update.message.reply_text("❌ Send a valid YouTube link")
        return

    context.user_data["url"] = url
    await update.message.reply_text("✅ Link saved\n👇 Choose option", reply_markup=keyboard)

async def run_ydl(opts, url):
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    url = context.user_data.get("url")
    if not url:
        await query.message.reply_text("❌ Send link first")
        return

    clean()
    await query.message.reply_text("⏳ Downloading...")

    if query.data == "audio":
        opts = {
            "format": "bestaudio[filesize_approx<45M]",
            "outtmpl": "audio.%(ext)s",
        }
        await asyncio.to_thread(run_ydl, opts, url)
        file = glob.glob("audio.*")
        if not file:
            await query.message.reply_text("❌ File too large")
            return
        await query.message.reply_audio(open(file[0], "rb"))
        clean()
        return

    opts = {
        "format": "best[height<=360][filesize_approx<45M]",
        "outtmpl": "video.%(ext)s",
    }
    await asyncio.to_thread(run_ydl, opts, url)

    file = glob.glob("video.*")
    if not file:
        await query.message.reply_text("❌ Video too large")
        return

    await query.message.reply_video(open(file[0], "rb"))
    clean()

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, save_url))
    app.add_handler(CallbackQueryHandler(button))
    app.run_polling()

if __name__ == "__main__":
    main()
