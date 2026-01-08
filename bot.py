async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    url = context.user_data.get("url")
    if not url:
        await query.message.reply_text("❌ Send link first")
        return

    await query.message.reply_text("🔗 Generating download link...")

    ydl_opts = {
        "quiet": True,
        "skip_download": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    if query.data == "audio":
        for f in info["formats"]:
            if f.get("acodec") != "none":
                await query.message.reply_text(
                    f"🎵 *Audio Download*\n\n{f['url']}",
                    parse_mode="Markdown",
                )
                return

    for f in info["formats"]:
        if f.get("height") == 360:
            await query.message.reply_text(
                f"🎥 *360p Download*\n\n{f['url']}",
                parse_mode="Markdown",
            )
            return

    await query.message.reply_text("❌ No suitable format found")
