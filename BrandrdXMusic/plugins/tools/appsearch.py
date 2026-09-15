import asyncio
import html
import logging
import re

import aiohttp
from bs4 import BeautifulSoup
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from BrandrdXMusic import app

LOGGER = logging.getLogger(__name__)


# =========================================================
# PLAY STORE SEARCH
# =========================================================

async def search_playstore(query: str):
    url = "https://play.google.com/store/search"

    params = {
        "q": query,
        "c": "apps",
        "hl": "en",
        "gl": "IN",
    }

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/140.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
    }

    timeout = aiohttp.ClientTimeout(total=20)

    try:
        async with aiohttp.ClientSession(
            timeout=timeout,
            headers=headers
        ) as session:

            async with session.get(url, params=params) as response:

                if response.status != 200:
                    LOGGER.error(
                        "Play Store returned HTTP %s",
                        response.status
                    )
                    return []

                text = await response.text()

        soup = BeautifulSoup(text, "html.parser")

        results = []
        seen = set()

        # Play Store app links
        for a in soup.find_all("a", href=True):

            href = a.get("href", "")

            if "/store/apps/details?id=" not in href:
                continue

            match = re.search(
                r"/store/apps/details\?id=([^&]+)",
                href
            )

            if not match:
                continue

            package_id = match.group(1)

            if package_id in seen:
                continue

            seen.add(package_id)

            title = a.get_text(" ", strip=True)

            if not title:
                title = package_id

            if href.startswith("/"):
                link = "https://play.google.com" + href
            else:
                link = href

            results.append(
                {
                    "title": title,
                    "id": package_id,
                    "link": link,
                }
            )

            if len(results) >= 10:
                break

        return results

    except Exception as e:
        LOGGER.exception("Play Store search error: %s", e)
        return []


# =========================================================
# /APP
# =========================================================

@app.on_message(filters.command(["app", "apps"]))
async def playstore_search_handler(client, message):

    # -----------------------------------------
    # GET QUERY
    # -----------------------------------------

    if message.reply_to_message and message.reply_to_message.text:
        query = message.reply_to_message.text.strip()

    elif len(message.command) > 1:
        query = " ".join(message.command[1:]).strip()

    else:
        await message.reply_text(
            "<b>❌ Pʟᴇᴀsᴇ Gɪᴠᴇ A Sᴇᴀʀᴄʜ Qᴜᴇʀʏ.</b>\n\n"
            "<blockquote>"
            "<b>Eᴜɪᴍᴘʟᴇ:</b>\n"
            "<code>/app WhatsApp</code>\n"
            "<code>/app Instagram</code>\n"
            "<code>/app Free Fire</code>"
            "</blockquote>",
        )
        return

    status = await message.reply_text(
        "<b>🔎 Sᴇᴀʀᴄʜɪɴɢ Pʟᴀʏ Sᴛᴏʀᴇ...</b>\n\n"
        f"<blockquote><b>Qᴜᴇʀʏ:</b> "
        f"<code>{html.escape(query)}</code></blockquote>",
    )

    try:

        results = await search_playstore(query)

        # -----------------------------------------
        # NO RESULTS
        # -----------------------------------------

        if not results:
            await status.edit_text(
                "<b>❌ Nᴏ Rᴇsᴜʟᴛs Fᴏᴜɴᴅ.</b>\n\n"
                f"<blockquote>"
                f"<b>Qᴜᴇʀʏ:</b> "
                f"<code>{html.escape(query)}</code>"
                f"</blockquote>",
            )
            return

        # -----------------------------------------
        # SHOW RESULTS
        # -----------------------------------------

        text = (
            "<b>📱 Pʟᴀʏ Sᴛᴏʀᴇ Rᴇsᴜʟᴛs</b>\n\n"
            f"<blockquote>"
            f"<b>Qᴜᴇʀʏ:</b> "
            f"<code>{html.escape(query)}</code>"
            f"</blockquote>\n"
        )

        buttons = []

        for index, item in enumerate(results[:8], start=1):

            title = html.escape(item["title"])
            package_id = html.escape(item["id"])
            link = item["link"]

            text += (
                f"\n<b>{index}. {title}</b>\n"
                f"<blockquote>"
                f"<b>ID:</b> <code>{package_id}</code>"
                f"</blockquote>"
            )

            buttons.append(
                [
                    InlineKeyboardButton(
                        f"📱 {item['title'][:25]}",
                        url=link,
                    )
                ]
            )

        await status.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(buttons),
            disable_web_page_preview=True,
        )

    except Exception as e:

        LOGGER.exception("APP command failed: %s", e)

        await status.edit_text(
            "<b>⚠️ Eʀʀᴏʀ Wʜɪʟᴇ Sᴇᴀʀᴄʜɪɴɢ.</b>\n\n"
            "<blockquote>"
            f"<b>Eʀʀᴏʀ:</b> <code>{html.escape(str(e))}</code>"
            "</blockquote>",
        )


# =========================================================
# MODULE HELP
# =========================================================

__MODULE__ = "Aᴘᴘ Sᴇᴀʀᴄʜ" 

__HELP__ = """
<b>📱 Aᴘᴘ Sᴇᴀʀᴄʜ</b>

<blockquote>
<b>/app [query]</b> - Sᴇᴀʀᴄʜ Pʟᴀʏ Sᴛᴏʀᴇ
<b>/apps [query]</b> - Sᴀᴍᴇ Aꜱ Aʙᴏᴠᴇ

<b>Eᴜɪᴍᴘʟᴇ:</b>
<code>/app WhatsApp</code>
<code>/app Instagram</code>
<code>/app Free Fire</code>
</blockquote>
"""
