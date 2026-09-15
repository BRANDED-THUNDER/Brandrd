import asyncio
import html
import logging

from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from googlesearch import search

from BrandrdXMusic import app

LOGGER = logging.getLogger(__name__)


# =========================================================
# GOOGLE SEARCH
# /app
# =========================================================

@app.on_message(filters.command(["google", "gle"]))
async def google_search_app(client, message):

    # Get query from reply or command
    if message.reply_to_message and message.reply_to_message.text:
        query = message.reply_to_message.text.strip()

    elif len(message.command) > 1:
        query = " ".join(message.command[1:]).strip()

    else:
        await message.reply_text(
            "<b>❌ Pʟᴇᴀsᴇ Gɪᴠᴇ A Sᴇᴀʀᴄʜ Qᴜᴇʀʏ.</b>\n\n"
            "<blockquote>"
            "<b>Example:</b>\n"
            "<code>/app India</code>\n"
            "<code>/app Telegram</code>\n"
            "<code>/app Python</code>"
            "</blockquote>",
        )
        return

    status = await message.reply_text(
        "<b>🔎 Sᴇᴀʀᴄʜɪɴɢ Oɴ Gᴏᴏɢʟᴇ...</b>\n\n"
        f"<blockquote>"
        f"<b>Qᴜᴇʀʏ:</b> "
        f"<code>{html.escape(query)}</code>"
        f"</blockquote>",
    )

    try:

        # Google search is synchronous,
        # so run it outside the async event loop.
        def google_search():
            return list(
                search(
                    query,
                    num_results=8,
                    lang="en",
                    sleep_interval=1,
                )
            )

        results = await asyncio.to_thread(google_search)

        if not results:
            await status.edit_text(
                "<b>❌ Nᴏ Rᴇsᴜʟᴛs Fᴏᴜɴᴅ.</b>\n\n"
                "<blockquote>"
                f"<b>Qᴜᴇʀʏ:</b> "
                f"<code>{html.escape(query)}</code>"
                "</blockquote>",
            )
            return

        text = (
            "<b>🔎 Gᴏᴏɢʟᴇ Sᴇᴀʀᴄʜ Rᴇsᴜʟᴛs</b>\n\n"
            "<blockquote>"
            f"<b>Qᴜᴇʀʏ:</b> "
            f"<code>{html.escape(query)}</code>"
            "</blockquote>\n"
        )

        buttons = []

        for i, url in enumerate(results, 1):

            # Basic title fallback
            title = url

            text += (
                f"\n<b>{i}. Rᴇsᴜʟᴛ</b>\n"
                f"<blockquote>"
                f"<code>{html.escape(url[:150])}</code>"
                f"</blockquote>"
            )

            buttons.append(
                [
                    InlineKeyboardButton(
                        f"🔗 Rᴇsᴜʟᴛ {i}",
                        url=url,
                    )
                ]
            )

        await status.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(buttons),
            disable_web_page_preview=True,
        )

    except Exception as e:

        LOGGER.exception("Google search error: %s", e)

        await status.edit_text(
            "<b>⚠️ Gᴏᴏɢʟᴇ Sᴇᴀʀᴄʜ Eʀʀᴏʀ.</b>\n\n"
            "<blockquote>"
            f"<b>Eʀʀᴏʀ:</b> "
            f"<code>{html.escape(str(e))}</code>"
            "</blockquote>",
        )


# =========================================================
# HELP
# =========================================================

__MODULE__ = "Gᴏᴏɢʟᴇ"

__HELP__ = """
<b>🔎 Gᴏᴏɢʟᴇ Sᴇᴀʀᴄʜ</b>

<blockquote>
<b>/google [query]</b> - Sᴇᴀʀᴄʜ Oɴ Gᴏᴏɢʟᴇ
<b>/gle [query]</b> - Sᴀᴍᴇ Aꜱ Aʙᴏᴠᴇ

<b>Eᴜɪᴍᴘʟᴇ:</b>
<code>/google India</code>
<code>/google Telegram</code>
<code>/google Python</code>
</blockquote>
"""
