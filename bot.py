import os
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
import yt_dlp

TOKEN = os.environ.get("BOT_TOKEN")

app_flask = Flask(__name__)
app = ApplicationBuilder().token(TOKEN).build()

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    await update.message.reply_text("Downloading...")

    with yt_dlp.YoutubeDL({'outtmpl': 'video.mp4'}) as ydl:
        ydl.download([url])

    await update.message.reply_video(open("video.mp4", "rb"))

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))

@app_flask.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), app.bot)
    app.update_queue.put_nowait(update)
    return "ok"

if __name__ == "__main__":
    app.bot.set_webhook(url=f"{os.environ.get('WEBHOOK_URL')}/{TOKEN}")
    app_flask.run(host="0.0.0.0", port=10000)
