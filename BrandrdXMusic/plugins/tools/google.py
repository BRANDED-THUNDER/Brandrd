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
# =========================================================

def do_google_search(query):
    try:
        return list(
            search(
                query,
                num_results=8,
                lang="en",
                sleep_interval=1,
            )
        )
    except Exception as e:
        LOGGER.exception("Google search failed: %s", e)
        return []


@app.on_message(filters.command(["google", "gle", "app", "apps"]))
async def google_search_handler(client, message):

    # -----------------------------------------
    # GET SEARCH QUERY
    # -----------------------------------------

    if message.reply_to_message and message.reply_to_message.text:
        user_input = message.reply_to_message.text.strip()

    elif len(message.command) > 1:
        user_input = " ".join(message.command[1:]).strip()

    else:
        await message.reply_text(
            "<b>❌ Pʟᴇᴀsᴇ Gɪᴠᴇ A Sᴇᴀʀᴄʜ Qᴜᴇʀʏ.</b>\n\n"
            "<blockquote>"
            "<b>Eᴜɪᴍᴘʟᴇ:</b>\n"
            "<code>/google India</code>\n"
            "<code>/app Telegram</code>\n"
            "<code>/gle Python</code>"
            "</blockquote>",
        )
        return

    status = await message.reply_text(
        "<b>🔎 Sᴇᴀʀᴄʜɪɴɢ Oɴ Gᴏᴏɢʟᴇ...</b>\n\n"
        "<blockquote>"
        f"<b>Qᴜᴇʀʏ:</b> "
        f"<code>{html.escape(user_input)}</code>"
        "</blockquote>",
    )

    try:

        # Google search is blocking, so run it
        # in a separate thread.
        results = await asyncio.to_thread(
            do_google_search,
            user_input
        )

        # -----------------------------------------
        # NO RESULTS
        # -----------------------------------------

        if not results:
            await status.edit_text(
                "<b>❌ Nᴏ Rᴇsᴜʟᴛs Fᴏᴜɴᴅ.</b>\n\n"
                "<blockquote>"
                f"<b>Qᴜᴇʀʏ:</b> "
                f"<code>{html.escape(user_input)}</code>"
                "</blockquote>",
            )
            return

        # -----------------------------------------
        # RESULTS
        # -----------------------------------------

        text = (
            "<b>🔎 Gᴏᴏɢʟᴇ Sᴇᴀʀᴄʜ Rᴇsᴜʟᴛs</b>\n\n"
            "<blockquote>"
            f"<b>Qᴜᴇʀʏ:</b> "
            f"<code>{html.escape(user_input)}</code>"
            "</blockquote>\n"
        )

        buttons = []

        for number, url in enumerate(results[:8], start=1):

            safe_url = html.escape(str(url), quote=False)

            text += (
                f"\n<b>❍ Rᴇsᴜʟᴛ {number}</b>\n"
                "<blockquote>"
                f"<code>{safe_url[:300]}</code>"
                "</blockquote>"
            )

            buttons.append(
                [
                    InlineKeyboardButton(
                        f"🔗 Rᴇsᴜʟᴛ {number}",
                        url=str(url),
                    )
                ]
            )

        await status.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(buttons),
            disable_web_page_preview=True,
        )

    except Exception as e:

        LOGGER.exception("Google command error: %s", e)

        await status.edit_text(
            "<b>⚠️ Gᴏᴏɢʟᴇ Sᴇᴀʀᴄʜ Eʀʀᴏʀ</b>\n\n"
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
<b>/google [query]</b> - Sᴇᴀʀᴄʜ Gᴏᴏɢʟᴇ
<b>/gle [query]</b> - Sᴇᴀʀᴄʜ Gᴏᴏɢʟᴇ
<b>/app [query]</b> - Sᴇᴀʀᴄʜ Gᴏᴏɢʟᴇ
<b>/apps [query]</b> - Sᴇᴀʀᴄʜ Gᴏᴏɢʟᴇ

<b>Eᴜɪᴍᴘʟᴇ:</b>
<code>/google India</code>
<code>/app Telegram</code>
<code>/gle Python</code>
</blockquote>
"""
