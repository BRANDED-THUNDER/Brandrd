import html
import logging
import urllib.parse

import aiohttp
from bs4 import BeautifulSoup
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from BrandrdXMusic import app

LOGGER = logging.getLogger(__name__)


# =========================================================
# GOOGLE SEARCH
# =========================================================

async def google_search(query: str, limit: int = 8):
    encoded_query = urllib.parse.quote_plus(query)

    url = f"https://www.google.com/search?q={encoded_query}&num={limit}&hl=en"

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/140.0.0.0 Safari/537.36"
        ),
        "Accept": (
            "text/html,application/xhtml+xml,"
            "application/xml;q=0.9,image/avif,"
            "image/webp,*/*;q=0.8"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Cache-Control": "no-cache",
    }

    timeout = aiohttp.ClientTimeout(total=20)

    try:
        async with aiohttp.ClientSession(
            headers=headers,
            timeout=timeout
        ) as session:

            async with session.get(
                url,
                allow_redirects=True
            ) as response:

                if response.status != 200:
                    LOGGER.error(
                        "Google HTTP status: %s",
                        response.status
                    )
                    return []

                data = await response.text()

        soup = BeautifulSoup(data, "html.parser")

        results = []
        seen = set()

        # Google result blocks
        for result in soup.select("div.MjjYud"):

            link_tag = result.select_one("a[href]")

            if not link_tag:
                continue

            href = link_tag.get("href", "")

            # Only normal Google result URLs
            if not href.startswith("/url?q="):
                continue

            parsed = urllib.parse.urlparse(href)
            params = urllib.parse.parse_qs(parsed.query)

            if "q" not in params:
                continue

            result_url = params["q"][0]

            if not result_url.startswith(("http://", "https://")):
                continue

            if result_url in seen:
                continue

            title_tag = result.select_one("h3")

            if not title_tag:
                continue

            title = title_tag.get_text(
                " ",
                strip=True
            )

            description = ""

            desc = result.select_one(
                ".VwiC3b"
            )

            if desc:
                description = desc.get_text(
                    " ",
                    strip=True
                )

            seen.add(result_url)

            results.append(
                {
                    "title": title,
                    "url": result_url,
                    "description": description,
                }
            )

            if len(results) >= limit:
                break

        return results

    except Exception as e:
        LOGGER.exception(
            "Google search failed: %s",
            e
        )
        return []


# =========================================================
# GOOGLE COMMAND
# =========================================================

@app.on_message(
    filters.command(
        ["google", "gle", "app", "apps"]
    )
)
async def google_search_handler(
    client,
    message
):

    # -----------------------------------------
    # QUERY
    # -----------------------------------------

    if (
        message.reply_to_message
        and message.reply_to_message.text
    ):
        user_input = (
            message.reply_to_message.text.strip()
        )

    elif len(message.command) > 1:
        user_input = " ".join(
            message.command[1:]
        ).strip()

    else:
        await message.reply_text(
            "<b>❌ Pʟᴇᴀsᴇ Gɪᴠᴇ A Sᴇᴀʀᴄʜ Qᴜᴇʀʏ.</b>\n\n"
            "<blockquote>"
            "<b>Eᴜɪᴍᴘʟᴇ:</b>\n"
            "<code>/google branded king</code>\n"
            "<code>/app phone pe</code>\n"
            "<code>/gle Telegram</code>"
            "</blockquote>",
        )
        return

    status = await message.reply_text(
        "<b>🔎 Sᴇᴀʀᴄʜɪɴɢ Oɴ Gᴏᴏɢʟᴇ...</b>\n\n"
        "<blockquote>"
        "<b>Qᴜᴇʀʏ:</b> "
        f"<code>{html.escape(user_input)}</code>"
        "</blockquote>",
    )

    try:

        results = await google_search(
            user_input,
            limit=8
        )

        # -----------------------------------------
        # NO RESULTS
        # -----------------------------------------

        if not results:
            await status.edit_text(
                "<b>❌ Nᴏ Rᴇsᴜʟᴛs Fᴏᴜɴᴅ.</b>\n\n"
                "<blockquote>"
                "<b>Qᴜᴇʀʏ:</b> "
                f"<code>{html.escape(user_input)}</code>"
                "</blockquote>\n\n"
                "<i>Gᴏᴏɢʟᴇ Mᴀʏ Hᴀᴠᴇ Bʟᴏᴄᴋᴇᴅ Tʜᴇ Rᴇǫᴜᴇsᴛ.</i>",
            )
            return

        # -----------------------------------------
        # BUILD RESULT
        # -----------------------------------------

        text = (
            "<b>🔎 Gᴏᴏɢʟᴇ Sᴇᴀʀᴄʜ</b>\n\n"
            "<blockquote>"
            "<b>Qᴜᴇʀʏ:</b> "
            f"<code>{html.escape(user_input)}</code>"
            "</blockquote>\n"
        )

        buttons = []

        for index, result in enumerate(
            results,
            start=1
        ):

            title = html.escape(
                result["title"]
            )

            description = html.escape(
                result["description"]
            )

            result_url = result["url"]

            if len(description) > 250:
                description = (
                    description[:247] + "..."
                )

            text += (
                f"\n<b>❍ {index}. {title}</b>\n"
            )

            if description:
                text += (
                    "<blockquote>"
                    f"{description}"
                    "</blockquote>"
                )

            buttons.append(
                [
                    InlineKeyboardButton(
                        f"🔗 Rᴇsᴜʟᴛ {index}",
                        url=result_url
                    )
                ]
            )

        await status.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(
                buttons
            ),
            disable_web_page_preview=True,
        )

    except Exception as e:

        LOGGER.exception(
            "Google command error: %s",
            e
        )

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
<b>/google [query]</b>
Sᴇᴀʀᴄʜ Gᴏᴏɢʟᴇ

<b>/gle [query]</b>
Sᴀᴍᴇ Aꜱ Gᴏᴏɢʟᴇ

<b>/app [query]</b>
Sᴀᴍᴇ Aꜱ Gᴏᴏɢʟᴇ

<b>Eᴜɪᴍᴘʟᴇ:</b>
<code>/google branded king</code>
<code>/app phone pe</code>
<code>/gle Telegram</code>
</blockquote>
"""
