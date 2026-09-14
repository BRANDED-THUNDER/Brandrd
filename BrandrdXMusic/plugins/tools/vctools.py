from pyrogram import Client, filters
from pyrogram.types import Message
from BrandrdXMusic import app
from pyrogram import *
from pyrogram.types import *
from config import OWNER_ID
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.raw.functions.phone import CreateGroupCall, DiscardGroupCall
from pyrogram.raw.types import InputGroupCall
from BrandrdXMusic.utils.database import get_assistant
from telethon.tl.functions.phone import (
    CreateGroupCallRequest,
    DiscardGroupCallRequest,
    GetGroupCallRequest,
    InviteToGroupCallRequest,
)


# vc on
@app.on_message(filters.video_chat_started)
async def brah(_, msg):
    group_name = msg.chat.title or "Private Chat"
    chat_id = msg.chat.id

    await msg.reply(
        f"<b><blockquote>"
        f" ᴠɪᴅᴇᴏ ᴄʜᴀᴛ sᴛᴀʀᴛᴇᴅ \n\n"
        f"──────────\n"
        f"๏ sᴛᴀʀᴛᴇᴅ ʙʏ : {group_name}\n"
        f"๏ ᴄʜᴀᴛ ɪᴅ : <code>{chat_id}</code>\n"
        f"──────────\n"
        f"ᴊᴏɪɴ ᴛʜᴇ ᴠɪᴅᴇᴏ ᴄʜᴀᴛ ɴᴏᴡ!"
        f"</blockquote></b>"
    )


# vc off
@app.on_message(filters.video_chat_ended)
async def brah2(_, msg):
    group_name = msg.chat.title or "Private Chat"
    chat_id = msg.chat.id

    await msg.reply(
        f"<b><blockquote>"
        f" ᴠɪᴅᴇᴏ ᴄʜᴀᴛ ᴇɴᴅᴇᴅ \n\n"
        f"──────────\n"
        f"๏ ɢʀᴏᴜᴘ : {group_name}\n"
        f"๏ ᴄʜᴀᴛ ɪᴅ : <code>{chat_id}</code>\n"
        f"๏ ᴅᴜʀᴀᴛɪᴏɴ : {duration_text}\n"
        f"──────────\n"
        f"</blockquote></b>"
    )
# ================================
# Invite Members on VC
# ================================

@app.on_message(filters.video_chat_members_invited)
async def brah3(client, message: Message):
    try:
        text = (
            f"➻ {message.from_user.mention}\n\n"
            f"**๏ ɪɴᴠɪᴛɪɴɢ:**\n\n"
        )

        for user in message.video_chat_members_invited.users:
            try:
                text += f"➻ [{user.first_name}](tg://user?id={user.id})\n"
            except Exception:
                pass

        add_link = f"https://t.me/{client.me.username}?startgroup=true"

        reply_text = f"{text}\n🤭🤭"

        await message.reply(
            reply_text,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "๏ ᴊᴏɪɴ ᴠᴄ ๏",
                            url=add_link
                        )
                    ]
                ]
            ),
        )

    except Exception as e:
        print(f"VC Invite Error: {e}")


# ================================
# Math Command
# ================================

@app.on_message(filters.command("math", prefixes="/"))
async def calculate_math(client, message: Message):
    try:
        if len(message.command) < 2:
            return await message.reply(
                "❌ Usage: `/math 10 + 20`"
            )

        expression = message.text.split("/math ", 1)[1]

        # Basic protection
        allowed = "0123456789+-*/().% "

        if not all(char in allowed for char in expression):
            return await message.reply(
                "❌ Invalid expression!"
            )

        result = eval(expression, {"__builtins__": None}, {})

        await message.reply(
            f"ᴛʜᴇ ʀᴇsᴜʟᴛ ɪs : `{result}`"
        )

    except Exception:
        await message.reply(
            "ɪɴᴠᴀʟɪᴅ ᴇxᴘʀᴇssɪᴏɴ"
        )


# ================================
# Google Search Command
# ================================

@app.on_message(filters.command(["spg"], prefixes=["/", "!", "."]))
async def search(client, message: Message):
    try:
        if len(message.command) < 2:
            return await message.reply(
                "❌ Usage: `/spg search query`"
            )

        query = " ".join(message.command[1:])

        msg = await message.reply("🔎 Searching...")

        async with aiohttp.ClientSession() as session:

            start = 1

            url = (
                "https://content-customsearch.googleapis.com/"
                "customsearch/v1"
            )

            params = {
                "cx": "YOUR_SEARCH_ENGINE_ID",
                "q": query,
                "key": "YOUR_GOOGLE_API_KEY",
                "start": start,
            }

            headers = {
                "x-referer": "https://explorer.apis.google.com"
            }

            async with session.get(
                url,
                params=params,
                headers=headers
            ) as r:

                response = await r.json()

            if not response.get("items"):
                return await msg.edit(
                    "❌ No results found!"
                )

            result = ""
            seen = set()

            for item in response["items"]:

                title = item.get("title", "No title")
                link = item.get("link", "")

                if not link or link in seen:
                    continue

                seen.add(link)

                # Clean URL
                if "/s" in link:
                    link = link.replace("/s", "", 1)

                elif re.search(r"/\d", link):
                    link = re.sub(r"/\d", "", link)

                if "?" in link:
                    link = link.split("?")[0]

                result += (
                    f"**{title}**\n"
                    f"`{link}`\n\n"
                )

            if not result:
                return await msg.edit(
                    "❌ No valid results found!"
                )

            buttons = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "▶️ Next ▶️",
                            callback_data=f"spg_next:{start + 10}:{query}"
                        )
                    ]
                ]
            )

            await msg.edit(
                result,
                disable_web_page_preview=True,
                reply_markup=buttons
            )

    except Exception as e:
        print(f"Search Error: {e}")

        try:
            await msg.edit(
                "❌ Search failed. Please try again."
            )
        except Exception:
            pass

