import os
import asyncio
import aiohttp

from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from BrandrdXMusic import app


CATBOX_URL = "https://catbox.moe/user/api.php"
MAX_FILE_SIZE = 200 * 1024 * 1024  # 200 MB


async def upload_file(file_path: str):
    """
    Upload file to Catbox and return:
    (True, url) on success
    (False, error_message) on failure
    """

    if not file_path or not os.path.exists(file_path):
        return False, "Fɪʟᴇ ɴᴏᴛ ғᴏᴜɴᴅ."

    file_size = os.path.getsize(file_path)

    if file_size > MAX_FILE_SIZE:
        return False, "Fɪʟᴇ ɪs ʟᴀʀɢᴇʀ ᴛʜᴀɴ 200 MB."

    try:
        timeout = aiohttp.ClientTimeout(
            total=900,
            connect=30,
            sock_read=900,
        )

        headers = {
            "User-Agent": (
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/120.0 Safari/537.36"
            )
        }

        form = aiohttp.FormData()

        form.add_field(
            "reqtype",
            "fileupload",
        )

        # Catbox expects the actual file field.
        with open(file_path, "rb") as file:
            form.add_field(
                "fileToUpload",
                file,
                filename=os.path.basename(file_path),
                content_type="application/octet-stream",
            )

            async with aiohttp.ClientSession(
                timeout=timeout,
                headers=headers,
            ) as session:

                async with session.post(
                    CATBOX_URL,
                    data=form,
                ) as response:

                    result = await response.text()

                    if response.status == 200:
                        result = result.strip()

                        # Catbox normally returns the uploaded URL
                        # as plain text.
                        if result.startswith("http://") or result.startswith(
                            "https://"
                        ):
                            return True, result

                        return False, (
                            "Cᴀᴛʙᴏx ʀᴇᴛᴜʀɴᴇᴅ ᴀɴ ᴜɴᴇxᴘᴇᴄᴛᴇᴅ ʀᴇsᴘᴏɴsᴇ:\n"
                            f"<code>{result[:1000]}</code>"
                        )

                    return False, (
                        f"Cᴀᴛʙᴏx ᴇʀʀᴏʀ: "
                        f"<code>{response.status}</code>\n\n"
                        f"<code>{result[:1000]}</code>"
                    )

    except asyncio.TimeoutError:
        return False, (
            "Cᴀᴛʙᴏx ᴜᴘʟᴏᴀᴅ ᴛɪᴍᴇᴅ ᴏᴜᴛ.\n"
            "Pʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ."
        )

    except aiohttp.ClientError as e:
        print(f"Catbox Client Error: {e}")
        return False, (
            "Fᴀɪʟᴇᴅ ᴛᴏ ᴄᴏɴɴᴇᴄᴛ ᴛᴏ Cᴀᴛʙᴏx.\n"
            f"<code>{str(e)[:500]}</code>"
        )

    except Exception as e:
        print(f"Catbox Upload Error: {e}")
        return False, (
            "Uɴᴋɴᴏᴡɴ Cᴀᴛʙᴏx ᴇʀʀᴏʀ.\n"
            f"<code>{str(e)[:500]}</code>"
        )


@app.on_message(filters.command(["tgm", "tgt", "telegraph", "tl"]))
async def get_link_group(client, message):

    if not message.reply_to_message:
        return await message.reply_text(
            "<blockquote>"
            "<b>❌ Pʟᴇᴀsᴇ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇᴅɪᴀ ғɪʟᴇ.</b>\n\n"
            "Rᴇᴘʟʏ ᴛᴏ ᴀ ᴘʜᴏᴛᴏ, ᴠɪᴅᴇᴏ, ᴅᴏᴄᴜᴍᴇɴᴛ, "
            "ᴀᴜᴅɪᴏ ᴏʀ ᴀɴɪᴍᴀᴛɪᴏɴ ᴡɪᴛʜ <code>/tgm</code>."
            "</blockquote>",
        )

    media = message.reply_to_message

    # Find media file size
    file_size = 0

    if media.photo:
        file_size = media.photo.file_size or 0

    elif media.video:
        file_size = media.video.file_size or 0

    elif media.document:
        file_size = media.document.file_size or 0

    elif media.animation:
        file_size = media.animation.file_size or 0

    elif media.audio:
        file_size = media.audio.file_size or 0

    elif media.voice:
        file_size = media.voice.file_size or 0

    else:
        return await message.reply_text(
            "<blockquote>"
            "<b>❌ Uɴsᴜᴘᴘᴏʀᴛᴇᴅ Mᴇᴅɪᴀ</b>\n\n"
            "Pʟᴇᴀsᴇ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴘʜᴏᴛᴏ, ᴠɪᴅᴇᴏ, "
            "ᴅᴏᴄᴜᴍᴇɴᴛ, ᴀᴜᴅɪᴏ ᴏʀ ᴀɴɪᴍᴀᴛɪᴏɴ."
            "</blockquote>",
        )

    # 200 MB limit
    if file_size > MAX_FILE_SIZE:
        size_mb = file_size / (1024 * 1024)

        return await message.reply_text(
            "<blockquote>"
            "<b>❌ Fɪʟᴇ Tᴏᴏ Lᴀʀɢᴇ</b>\n\n"
            f"Fɪʟᴇ Sɪᴢᴇ: <code>{size_mb:.2f} MB</code>\n"
            "Mᴀxɪᴍᴜᴍ Sɪᴢᴇ: <code>200 MB</code>"
            "</blockquote>",
        )

    text = await message.reply_text(
        "<blockquote>"
        "<b>📥 Dᴏᴡɴʟᴏᴀᴅɪɴɢ Fɪʟᴇ...</b>\n\n"
        "Pʟᴇᴀsᴇ Wᴀɪᴛ."
        "</blockquote>",
    )

    local_path = None

    try:

        # -------------------------
        # DOWNLOAD FROM TELEGRAM
        # -------------------------

        last_update = 0

        async def progress(current, total):
            nonlocal last_update

            if not total:
                return

            percent = current * 100 / total

            # Avoid editing Telegram message too frequently.
            now = asyncio.get_running_loop().time()

            if now - last_update < 2:
                return

            last_update = now

            try:
                await text.edit_text(
                    "<blockquote>"
                    "<b>📥 Dᴏᴡɴʟᴏᴀᴅɪɴɢ Fɪʟᴇ...</b>\n\n"
                    f"<b>Pʀᴏɢʀᴇss:</b> "
                    f"<code>{percent:.1f}%</code>"
                    "</blockquote>",
                )
            except Exception:
                pass

        local_path = await message.reply_to_message.download(
            progress=progress
        )

        if not local_path or not os.path.exists(local_path):
            raise Exception("Telegram download failed.")

        # -------------------------
        # CATBOX UPLOAD
        # -------------------------

        await text.edit_text(
            "<blockquote>"
            "<b>📤 Uᴘʟᴏᴀᴅɪɴɢ Tᴏ Cᴀᴛʙᴏx...</b>\n\n"
            "Tʜɪs ᴍᴀʏ ᴛᴀᴋᴇ sᴏᴍᴇ ᴛɪᴍᴇ ғᴏʀ ʟᴀʀɢᴇ ғɪʟᴇs."
            "</blockquote>",
        )

        success, result = await upload_file(local_path)

        # -------------------------
        # SUCCESS
        # -------------------------

        if success:

            upload_url = result.strip()

            buttons = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "🔗 Oᴘᴇɴ Fɪʟᴇ",
                            url=upload_url,
                        )
                    ]
                ]
            )

            await text.edit_text(
                "<blockquote>"
                "<b>✅ Uᴘʟᴏᴀᴅ Sᴜᴄᴄᴇssғᴜʟ</b>\n\n"
                f"<b>🔗 Lɪɴᴋ:</b>\n"
                f"<code>{upload_url}</code>"
                "</blockquote>",
                reply_markup=buttons,
                disable_web_page_preview=True,
            )

        # -------------------------
        # ERROR
        # -------------------------

        else:

            await text.edit_text(
                "<blockquote>"
                "<b>❌ Uᴘʟᴏᴀᴅ Fᴀɪʟᴇᴅ</b>\n\n"
                f"<b>Rᴇᴀsᴏɴ:</b>\n"
                f"{result}"
                "</blockquote>",
            )

    except Exception as e:

        print(f"Telegram/Catbox Error: {e}")

        try:
            await text.edit_text(
                "<blockquote>"
                "<b>❌ Fɪʟᴇ Uᴘʟᴏᴀᴅ Fᴀɪʟᴇᴅ</b>\n\n"
                f"<b>Rᴇᴀsᴏɴ:</b>\n"
                f"<code>{str(e)[:1000]}</code>"
                "</blockquote>",
            )
        except Exception:
            pass

    finally:

        # -------------------------
        # CLEAN TEMP FILE
        # -------------------------

        if local_path and os.path.exists(local_path):
            try:
                os.remove(local_path)
            except Exception as e:
                print(f"File cleanup error: {e}")


__MODULE__ = "Tᴇʟᴇɢʀᴀᴘʜ"

__HELP__ = """
<b>📤 Tᴇʟᴇɢʀᴀᴘʜ / Cᴀᴛʙᴏx Uᴘʟᴏᴀᴅᴇʀ</b>

<blockquote>
<b>Cᴏᴍᴍᴀɴᴅs:</b>

• <code>/tgm</code> - Uᴘʟᴏᴀᴅ Mᴇᴅɪᴀ
• <code>/tgt</code> - Uᴘʟᴏᴀᴅ Mᴇᴅɪᴀ
• <code>/telegraph</code> - Uᴘʟᴏᴀᴅ Mᴇᴅɪᴀ
• <code>/tl</code> - Uᴘʟᴏᴀᴅ Mᴇᴅɪᴀ

<b>Hᴏᴡ Tᴏ Uѕᴇ:</b>

Rᴇᴘʟʏ ᴛᴏ ᴀ:
• Pʜᴏᴛᴏ
• Vɪᴅᴇᴏ
• Dᴏᴄᴜᴍᴇɴᴛ
• Aᴜᴅɪᴏ
• Aɴɪᴍᴀᴛɪᴏɴ
• Vᴏɪᴄᴇ

Tʜᴇɴ sᴇɴᴅ <code>/tgm</code>.

<b>Mᴀxɪᴍᴜᴍ Fɪʟᴇ Sɪᴢᴇ:</b> <code>200 MB</code>
</blockquote>
"""
