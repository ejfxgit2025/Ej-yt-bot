import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
import yt_dlp

BOT_TOKEN = os.getenv("BOT_TOKEN")   # 👈 token comes from Koyeb

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text

    if "youtube.com" not in url and "youtu.be" not in url:
        await update.message.reply_text("❌ Send a YouTube link")
        return

    await update.message.reply_text("⬇️ Downloading...")

    with yt_dlp.YoutubeDL({"outtmpl": "video.%(ext)s"}) as ydl:
        ydl.download([url])

    await update.message.reply_video(open("video.mp4", "rb"))

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))
app.run_polling()
