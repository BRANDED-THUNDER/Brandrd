import asyncio
import html
import logging

from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from googlesearch import search

from BrandrdXMusic import app


LOGGER = logging.getLogger(__name__)


# ============================================================
# GOOGLE SEARCH
# ============================================================

@app.on_message(
    filters.command(["google", "gle"])
)
async def google_search_handler(client, message):

    # --------------------------------------------------------
    # GET QUERY
    # --------------------------------------------------------

    if (
        len(message.command) < 2
        and not message.reply_to_message
    ):
        return await message.reply_text(
            "<blockquote>"
            "<b>🔎 Gᴏᴏɢʟᴇ Sᴇᴀʀᴄʜ</b>\n\n"
            "<b>Exᴀᴍᴘʟᴇ:</b>\n"
            "<code>/google lord ram</code>"
            "</blockquote>",
        )

    # --------------------------------------------------------
    # REPLY TEXT OR COMMAND TEXT
    # --------------------------------------------------------

    if (
        message.reply_to_message
        and message.reply_to_message.text
    ):
        user_input = (
            message.reply_to_message.text.strip()
        )
    else:
        user_input = " ".join(
            message.command[1:]
        ).strip()

    if not user_input:
        return await message.reply_text(
            "<blockquote>"
            "<b>❌ Pʟᴇᴀsᴇ Eɴᴛᴇʀ A Sᴇᴀʀᴄʜ Qᴜᴇʀʏ.</b>"
            "</blockquote>",
        )

    status = await message.reply_text(
        "<blockquote>"
        "<b>🔎 Sᴇᴀʀᴄʜɪɴɢ Gᴏᴏɢʟᴇ...</b>\n\n"
        f"<b>Qᴜᴇʀʏ:</b> "
        f"<code>{html.escape(user_input)}</code>"
        "</blockquote>",
    )

    try:

        # ----------------------------------------------------
        # RUN GOOGLE SEARCH IN BACKGROUND THREAD
        # ----------------------------------------------------

        def do_search():

            return list(
                search(
                    user_input,
                    advanced=True,
                    num_results=8,
                    lang="en",
                    sleep_interval=1,
                )
            )

        results = await asyncio.to_thread(
            do_search
        )

        if not results:

            return await status.edit_text(
                "<blockquote>"
                "<b>❌ Nᴏ Rᴇsᴜʟᴛs Fᴏᴜɴᴅ.</b>\n\n"
                f"Qᴜᴇʀʏ: "
                f"<code>{html.escape(user_input)}</code>"
                "</blockquote>",
            )

        # ----------------------------------------------------
        # BUILD RESULTS
        # ----------------------------------------------------

        text = (
            "<blockquote>"
            "<b>🔎 Gᴏᴏɢʟᴇ Sᴇᴀʀᴄʜ Rᴇsᴜʟᴛs</b>\n\n"
            f"<b>Qᴜᴇʀʏ:</b> "
            f"<code>{html.escape(user_input)}</code>"
            "</blockquote>\n\n"
        )

        buttons = []

        for number, result in enumerate(
            results[:8],
            start=1,
        ):

            title = getattr(
                result,
                "title",
                None,
            )

            url = getattr(
                result,
                "url",
                None,
            )

            description = getattr(
                result,
                "description",
                None,
            )

            if not title or not url:
                continue

            title = html.escape(
                str(title)
            )

            description = html.escape(
                str(description or "")
            )

            # Keep Telegram message reasonably short.
            if len(description) > 250:
                description = (
                    description[:247] + "..."
                )

            text += (
                f"<b>{number}. "
                f"{title}</b>\n"
            )

            if description:
                text += (
                    f"<blockquote>"
                    f"{description}"
                    f"</blockquote>\n"
                )

            buttons.append(
                [
                    InlineKeyboardButton(
                        f"🔗 {number}. Oᴘᴇɴ",
                        url=url,
                    )
                ]
            )

        if not buttons:

            return await status.edit_text(
                "<blockquote>"
                "<b>❌ Nᴏ Vᴀʟɪᴅ Rᴇsᴜʟᴛs Fᴏᴜɴᴅ.</b>"
                "</blockquote>",
            )

        await status.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(
                buttons
            ),
            parse_mode="html",
            disable_web_page_preview=True,
        )

    except Exception as e:

        LOGGER.exception(
            "Google search error: %s",
            e,
        )

        try:

            await status.edit_text(
                "<blockquote>"
                "<b>❌ Gᴏᴏɢʟᴇ Sᴇᴀʀᴄʜ Fᴀɪʟᴇᴅ</b>\n\n"
                f"<b>Eʀʀᴏʀ:</b>\n"
                f"<code>{html.escape(str(e)[:1000])}</code>"
                "</blockquote>",
            )

        except Exception:
            pass


# ============================================================
# APP SEARCH
# ============================================================

@app.on_message(
    filters.command(["app", "apps"])
)
async def playstore_search_handler(
    client,
    message,
):

    # --------------------------------------------------------
    # GET QUERY
    # --------------------------------------------------------

    if (
        len(message.command) < 2
        and not message.reply_to_message
    ):
        return await message.reply_text(
            "<blockquote>"
            "<b>📱 Pʟᴀʏ Sᴛᴏʀᴇ Sᴇᴀʀᴄʜ</b>\n\n"
            "<b>Exᴀᴍᴘʟᴇ:</b>\n"
            "<code>/app Free Fire</code>"
            "</blockquote>",
        )

    if (
        message.reply_to_message
        and message.reply_to_message.text
    ):
        user_input = (
            message.reply_to_message.text.strip()
        )
    else:
        user_input = " ".join(
            message.command[1:]
        ).strip()

    if not user_input:

        return await message.reply_text(
            "<blockquote>"
            "<b>❌ Pʟᴇᴀsᴇ Eɴᴛᴇʀ Aɴ Aᴘᴘ Nᴀᴍᴇ.</b>"
            "</blockquote>",
        )

    status = await message.reply_text(
        "<blockquote>"
        "<b>📱 Sᴇᴀʀᴄʜɪɴɢ Pʟᴀʏ Sᴛᴏʀᴇ...</b>\n\n"
        f"<b>Qᴜᴇʀʏ:</b> "
        f"<code>{html.escape(user_input)}</code>"
        "</blockquote>",
    )

    try:

        # ----------------------------------------------------
        # USE GOOGLE SEARCH TO FIND PLAY STORE APP
        # ----------------------------------------------------

        def search_playstore():

            query = (
                f"site:play.google.com/store/apps "
                f"{user_input}"
            )

            return list(
                search(
                    query,
                    advanced=True,
                    num_results=5,
                    lang="en",
                    sleep_interval=1,
                )
            )

        results = await asyncio.to_thread(
            search_playstore
        )

        if not results:

            return await status.edit_text(
                "<blockquote>"
                "<b>❌ Aᴘᴘ Nᴏᴛ Fᴏᴜɴᴅ.</b>\n\n"
                "Tʀʏ Aɴᴏᴛʜᴇʀ Aᴘᴘ Nᴀᴍᴇ."
                "</blockquote>",
            )

        # ----------------------------------------------------
        # FIND FIRST PLAY STORE RESULT
        # ----------------------------------------------------

        selected = None

        for result in results:

            url = getattr(
                result,
                "url",
                "",
            )

            if (
                "play.google.com/store/apps"
                in url
            ):
                selected = result
                break

        if not selected:

            return await status.edit_text(
                "<blockquote>"
                "<b>❌ Pʟᴀʏ Sᴛᴏʀᴇ Aᴘᴘ Nᴏᴛ Fᴏᴜɴᴅ.</b>"
                "</blockquote>",
            )

        title = getattr(
            selected,
            "title",
            "Unknown App",
        )

        url = getattr(
            selected,
            "url",
            "",
        )

        description = getattr(
            selected,
            "description",
            "",
        )

        title = html.escape(
            str(title)
        )

        description = html.escape(
            str(description or "")
        )

        if len(description) > 700:
            description = (
                description[:697] + "..."
            )

        # ----------------------------------------------------
        # EXTRACT PACKAGE ID
        # ----------------------------------------------------

        package_id = "Unknown"

        if "?id=" in url:

            package_id = (
                url.split("?id=", 1)[1]
                .split("&", 1)[0]
            )

        # ----------------------------------------------------
        # RESULT
        # ----------------------------------------------------

        text = (
            "<blockquote>"
            "<b>📱 Pʟᴀʏ Sᴛᴏʀᴇ Aᴘᴘ</b>\n\n"
            f"<b>Tɪᴛʟᴇ:</b> "
            f"{title}\n\n"
            f"<b>ID:</b> "
            f"<code>{html.escape(package_id)}</code>\n\n"
            f"<b>Dᴇsᴄʀɪᴘᴛɪᴏɴ:</b>\n"
            f"{description}"
            "</blockquote>"
        )

        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "📱 Oᴘᴇɴ Pʟᴀʏ Sᴛᴏʀᴇ",
                        url=url,
                    )
                ]
            ]
        )

        await status.edit_text(
            text,
            reply_markup=keyboard,
            disable_web_page_preview=False,
        )

    except Exception as e:

        LOGGER.exception(
            "Play Store search error: %s",
            e,
        )

        try:

            await status.edit_text(
                "<blockquote>"
                "<b>❌ Aᴘᴘ Sᴇᴀʀᴄʜ Fᴀɪʟᴇᴅ</b>\n\n"
                f"<b>Eʀʀᴏʀ:</b>\n"
                f"<code>{html.escape(str(e)[:1000])}</code>"
                "</blockquote>",
            )

        except Exception:
            pass


# ============================================================
# HELP
# ============================================================

__MODULE__ = "Sᴇᴀʀᴄʜ"

__HELP__ = """
<b>🔎 Sᴇᴀʀᴄʜ Cᴏᴍᴍᴀɴᴅs</b>

<blockquote>
<b>Gᴏᴏɢʟᴇ:</b>

<code>/google query</code>
<code>/gle query</code>

<b>Example:</b>
<code>/google lord ram</code>

<b>Pʟᴀʏ Sᴛᴏʀᴇ:</b>

<code>/app app name</code>
<code>/apps app name</code>

<b>Example:</b>
<code>/app Free Fire</code>

Yᴏᴜ Cᴀɴ Aʟsᴏ Rᴇᴘʟʏ Tᴏ A Tᴇxᴛ Mᴇssᴀɢᴇ Wɪᴛʜ
<code>/google</code> Oʀ <code>/app</code>.
</blockquote>
"""
