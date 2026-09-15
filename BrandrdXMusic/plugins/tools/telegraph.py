import os
import asyncio
import aiohttp

from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from BrandrdXMusic import app


FILEIO_URL = "https://file.io"
MAX_FILE_SIZE = 200 * 1024 * 1024  # 200 MB


async def upload_file(file_path: str):
    """
    Upload a file to file.io.

    Returns:
        (True, download_url)
        (False, error_message)
    """

    if not file_path:
        return False, "Fɪʟᴇ ᴘᴀᴛʜ ɪs ᴇᴍᴘᴛʏ."

    if not os.path.exists(file_path):
        return False, "Fɪʟᴇ ᴅᴏᴇs ɴᴏᴛ ᴇxɪsᴛ."

    file_size = os.path.getsize(file_path)

    if file_size == 0:
        return False, "Fɪʟᴇ ɪs ᴇᴍᴘᴛʏ."

    if file_size > MAX_FILE_SIZE:
        return False, (
            f"Fɪʟᴇ ɪs ᴛᴏᴏ ʟᴀʀɢᴇ.\n"
            f"Mᴀxɪᴍᴜᴍ sɪᴢᴇ: <code>200 MB</code>"
        )

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

    try:
        async with aiohttp.ClientSession(
            timeout=timeout,
            headers=headers,
        ) as session:

            with open(file_path, "rb") as file:

                form = aiohttp.FormData()

                form.add_field(
                    "file",
                    file,
                    filename=os.path.basename(file_path),
                    content_type="application/octet-stream",
                )

                async with session.post(
                    FILEIO_URL,
                    data=form,
                ) as response:

                    response_text = await response.text()

                    if response.status != 200:
                        return False, (
                            f"Fɪʟᴇ.ɪᴏ ᴇʀʀᴏʀ: "
                            f"<code>{response.status}</code>\n\n"
                            f"<code>{response_text[:1000]}</code>"
                        )

                    try:
                        data = await response.json(
                            content_type=None
                        )
                    except Exception:
                        return False, (
                            "Fɪʟᴇ.ɪᴏ ʀᴇᴛᴜʀɴᴇᴅ ᴀɴ ɪɴᴠᴀʟɪᴅ ʀᴇsᴘᴏɴsᴇ.\n\n"
                            f"<code>{response_text[:1000]}</code>"
                        )

                    if not isinstance(data, dict):
                        return False, "Iɴᴠᴀʟɪᴅ Fɪʟᴇ.ɪᴏ ʀᴇsᴘᴏɴsᴇ."

                    if data.get("success") is not True:
                        message = data.get(
                            "message",
                            "Fɪʟᴇ.ɪᴏ ᴜᴘʟᴏᴀᴅ ғᴀɪʟᴇᴅ.",
                        )

                        return False, (
                            f"<code>{str(message)[:1000]}</code>"
                        )

                    download_url = data.get("link")

                    if not download_url:
                        return False, (
                            "Fɪʟᴇ.ɪᴏ ᴅɪᴅ ɴᴏᴛ ʀᴇᴛᴜʀɴ ᴀ ᴅᴏᴡɴʟᴏᴀᴅ ʟɪɴᴋ."
                        )

                    return True, download_url

    except asyncio.TimeoutError:
        return False, (
            "Fɪʟᴇ.ɪᴏ ᴜᴘʟᴏᴀᴅ ᴛɪᴍᴇᴅ ᴏᴜᴛ.\n"
            "Pʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ."
        )

    except aiohttp.ClientError as e:
        print(f"File.io connection error: {e}")

        return False, (
            "Fᴀɪʟᴇᴅ ᴛᴏ ᴄᴏɴɴᴇᴄᴛ ᴛᴏ Fɪʟᴇ.ɪᴏ.\n\n"
            f"<code>{str(e)[:500]}</code>"
        )

    except Exception as e:
        print(f"File.io upload error: {e}")

        return False, (
            "Uɴᴋɴᴏᴡɴ Uᴘʟᴏᴀᴅ Eʀʀᴏʀ.\n\n"
            f"<code>{str(e)[:500]}</code>"
        )


@app.on_message(
    filters.command(
        ["tgm", "tgt", "telegraph", "tl"]
    )
)
async def get_link_group(client, message):

    media = message.reply_to_message

    # -------------------------
    # CHECK REPLY
    # -------------------------

    if not media:
        return await message.reply_text(
            "<blockquote>"
            "<b>❌ Rᴇᴘʟʏ Tᴏ A Mᴇᴅɪᴀ Fɪʟᴇ</b>\n\n"
            "Rᴇᴘʟʏ ᴛᴏ ᴀ ᴘʜᴏᴛᴏ, ᴠɪᴅᴇᴏ, ᴅᴏᴄᴜᴍᴇɴᴛ, "
            "ᴀᴜᴅɪᴏ ᴏʀ ᴀɴɪᴍᴀᴛɪᴏɴ ᴡɪᴛʜ <code>/tgm</code>."
            "</blockquote>",
        )

    # -------------------------
    # DETECT MEDIA
    # -------------------------

    file_size = 0

    if media.photo:
        file_size = media.photo.file_size or 0

    elif media.video:
        file_size = media.video.file_size or 0

    elif media.document:
        file_size = media.document.file_size or 0

    elif media.audio:
        file_size = media.audio.file_size or 0

    elif media.animation:
        file_size = media.animation.file_size or 0

    elif media.voice:
        file_size = media.voice.file_size or 0

    elif media.video_note:
        file_size = media.video_note.file_size or 0

    else:
        return await message.reply_text(
            "<blockquote>"
            "<b>❌ Uɴsᴜᴘᴘᴏʀᴛᴇᴅ Fɪʟᴇ</b>\n\n"
            "Pʟᴇᴀsᴇ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴘʜᴏᴛᴏ, ᴠɪᴅᴇᴏ, "
            "ᴅᴏᴄᴜᴍᴇɴᴛ, ᴀᴜᴅɪᴏ ᴏʀ ᴀɴɪᴍᴀᴛɪᴏɴ."
            "</blockquote>",
        )

    # -------------------------
    # SIZE CHECK
    # -------------------------

    if file_size > MAX_FILE_SIZE:

        size_mb = file_size / (1024 * 1024)

        return await message.reply_text(
            "<blockquote>"
            "<b>❌ Fɪʟᴇ Tᴏᴏ Lᴀʀɢᴇ</b>\n\n"
            f"<b>Fɪʟᴇ Sɪᴢᴇ:</b> "
            f"<code>{size_mb:.2f} MB</code>\n"
            f"<b>Mᴀxɪᴍᴜᴍ:</b> "
            f"<code>200 MB</code>"
            "</blockquote>",
        )

    # -------------------------
    # STATUS MESSAGE
    # -------------------------

    status = await message.reply_text(
        "<blockquote>"
        "<b>📥 Dᴏᴡɴʟᴏᴀᴅɪɴɢ Fɪʟᴇ...</b>\n\n"
        "Pʟᴇᴀsᴇ Wᴀɪᴛ..."
        "</blockquote>",
    )

    local_path = None

    try:

        # -------------------------
        # TELEGRAM DOWNLOAD
        # -------------------------

        last_update = 0

        async def progress(current, total):

            nonlocal last_update

            if not total:
                return

            now = asyncio.get_running_loop().time()

            # Update message every 2 seconds
            if now - last_update < 2:
                return

            last_update = now

            percent = (current / total) * 100

            try:
                await status.edit_text(
                    "<blockquote>"
                    "<b>📥 Dᴏᴡɴʟᴏᴀᴅɪɴɢ Fɪʟᴇ...</b>\n\n"
                    f"<b>Pʀᴏɢʀᴇss:</b> "
                    f"<code>{percent:.1f}%</code>"
                    "</blockquote>",
                )
            except Exception:
                pass

        local_path = await media.download(
            progress=progress
        )

        if not local_path:
            raise Exception(
                "Telegram did not return a file path."
            )

        if not os.path.exists(local_path):
            raise Exception(
                "Downloaded file does not exist."
            )

        # -------------------------
        # UPLOAD TO FILE.IO
        # -------------------------

        await status.edit_text(
            "<blockquote>"
            "<b>📤 Uᴘʟᴏᴀᴅɪɴɢ Tᴏ Fɪʟᴇ.ɪᴏ...</b>\n\n"
            "Tʜɪs ᴄᴀɴ ᴛᴀᴋᴇ sᴏᴍᴇ ᴛɪᴍᴇ ғᴏʀ ʟᴀʀɢᴇ ғɪʟᴇs."
            "</blockquote>",
        )

        success, result = await upload_file(
            local_path
        )

        # -------------------------
        # SUCCESS
        # -------------------------

        if success:

            upload_url = result

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

            await status.edit_text(
                "<blockquote>"
                "<b>✅ Uᴘʟᴏᴀᴅ Sᴜᴄᴄᴇssғᴜʟ</b>\n\n"
                f"<b>🔗 Dᴏᴡɴʟᴏᴀᴅ Lɪɴᴋ:</b>\n"
                f"<code>{upload_url}</code>\n\n"
                "<i>⚠️ Fɪʟᴇ.ɪᴏ ʟɪɴᴋs ᴍᴀʏ ᴇxᴘɪʀᴇ.</i>"
                "</blockquote>",
                reply_markup=buttons,
                disable_web_page_preview=True,
            )

        # -------------------------
        # UPLOAD FAILED
        # -------------------------

        else:

            await status.edit_text(
                "<blockquote>"
                "<b>❌ Uᴘʟᴏᴀᴅ Fᴀɪʟᴇᴅ</b>\n\n"
                f"<b>Rᴇᴀsᴏɴ:</b>\n"
                f"{result}"
                "</blockquote>",
            )

    except Exception as e:

        print(
            f"TGM Plugin Error: {type(e).__name__}: {e}"
        )

        try:
            await status.edit_text(
                "<blockquote>"
                "<b>❌ Pʀᴏᴄᴇssɪɴɢ Fᴀɪʟᴇᴅ</b>\n\n"
                f"<b>Eʀʀᴏʀ:</b>\n"
                f"<code>{str(e)[:1000]}</code>"
                "</blockquote>",
            )
        except Exception:
            pass

    finally:

        # -------------------------
        # DELETE TEMP FILE
        # -------------------------

        if local_path:

            try:

                if os.path.exists(local_path):
                    os.remove(local_path)

            except Exception as e:
                print(
                    f"Temporary file cleanup error: {e}"
                )


__MODULE__ = "Tᴇʟᴇɢʀᴀᴘʜ"

__HELP__ = """
<b>📤 Tᴇʟᴇɢʀᴀᴘʜ / Fɪʟᴇ Uᴘʟᴏᴀᴅᴇʀ</b>

<blockquote>
<b>Cᴏᴍᴍᴀɴᴅs:</b>

• <code>/tgm</code>
• <code>/tgt</code>
• <code>/telegraph</code>
• <code>/tl</code>

<b>Hᴏᴡ Tᴏ Uѕᴇ:</b>

Rᴇᴘʟʏ ᴛᴏ ᴀ ᴘʜᴏᴛᴏ, ᴠɪᴅᴇᴏ,
ᴅᴏᴄᴜᴍᴇɴᴛ, ᴀᴜᴅɪᴏ,
ᴀɴɪᴍᴀᴛɪᴏɴ ᴏʀ ᴠᴏɪᴄᴇ

Tʜᴇɴ sᴇɴᴅ:

<code>/tgm</code>

<b>Mᴀxɪᴍᴜᴍ:</b> <code>200 MB</code>

<b>Hᴏsᴛ:</b> Fɪʟᴇ.ɪᴏ
</blockquote>
"""
