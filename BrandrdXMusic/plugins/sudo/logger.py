from pyrogram import filters

from BrandrdXMusic import app
from BrandrdXMusic.misc import SUDOERS
from BrandrdXMusic.utils.database import add_off, add_on
from BrandrdXMusic.utils.decorators.language import language


@app.on_message(filters.command(["logger"]) & SUDOERS)
@language
# =========================
# 📝 LOGGER SETTINGS
# =========================

async def logger_settings(client, message, _):
    usage = _["log_1"]

    if len(message.command) != 2:
        return await message.reply_text(
            f"<b><blockquote>{usage}</blockquote></b>",
        )

    state = message.text.split(None, 1)[1].strip().lower()

    if state == "enable":
        await add_on(2)

        await message.reply_text(
            f"<b><blockquote>"
            f"🟢 {_[\"log_2\"]}"
            f"</blockquote></b>",
        )

    elif state == "disable":
        await add_off(2)

        await message.reply_text(
            f"<b><blockquote>"
            f"🔴 {_[\"log_3\"]}"
            f"</blockquote></b>",
        )

    else:
        await message.reply_text(
            f"<b><blockquote>{usage}</blockquote></b>",
        )


# =========================
# 🍪 COOKIES LOGS
# =========================

@app.on_message(filters.command(["cookies"]) & SUDOERS)
@language
async def cookies_logs(client, message, _):

    await message.reply_document(
        "cookies/logs.csv"
    )

    await message.reply_text(
        "<b><blockquote>"
        "🍪 Cᴏᴏᴋɪᴇs Lᴏɢ Fɪʟᴇ Sᴇɴᴛ Sᴜᴄᴄᴇssғᴜʟʟʏ!\n\n"
        "📂 Pʟᴇᴀsᴇ Cʜᴇᴄᴋ Tʜᴇ Gɪᴠᴇɴ Fɪʟᴇ Fᴏʀ "
        "Cᴏᴏᴋɪᴇs Fɪʟᴇ Cʜᴏᴏsɪɴɢ Lᴏɢs..."
        "</blockquote></b>",
    )
