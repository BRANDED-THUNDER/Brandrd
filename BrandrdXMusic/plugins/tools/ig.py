import os
import asyncio
import tempfile

from pyrogram import filters
from BrandrdXMusic import app


@app.on_message(filters.command(["ig", "instagram", "reel"]))
async def download_instagram_video(client, message):
    if len(message.command) < 2:
        await message.reply_text(
            "Pʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴛʜᴇ Iɴsᴛᴀɢʀᴀᴍ Rᴇᴇʟ URL ᴀғᴛᴇʀ ᴛʜᴇ ᴄᴏᴍᴍᴀɴᴅ"
        )
        return

    url = message.command[1].strip()

    # Basic Instagram URL validation
    if not (
        "instagram.com/" in url
        or "www.instagram.com/" in url
        or "instagr.am/" in url
    ):
        await message.reply_text(
            "❌ Pʟᴇᴀsᴇ sᴇɴᴅ ᴀ ᴠᴀʟɪᴅ Iɴsᴛᴀɢʀᴀᴍ URL."
        )
        return

    processing = await message.reply_text(
        "⏳ <b>Pʀᴏᴄᴇssɪɴɢ Iɴsᴛᴀɢʀᴀᴍ...</b>"
    )

    temp_dir = tempfile.mkdtemp(prefix="instagram_")
    output_template = os.path.join(temp_dir, "%(id)s.%(ext)s")

    try:
        await processing.edit_text(
            "⬇️ <b>Dᴏᴡɴʟᴏᴀᴅɪɴɢ Iɴsᴛᴀɢʀᴀᴍ Vɪᴅᴇᴏ...</b>"
        )

        # Run yt-dlp in a separate thread so the Pyrogram event loop
        # does not get blocked.
        process = await asyncio.create_subprocess_exec(
            "yt-dlp",
            "--no-playlist",
            "--no-warnings",
            "--restrict-filenames",
            "-f",
            "best[ext=mp4]/best",
            "-o",
            output_template,
            url,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await process.communicate()

        error_output = stderr.decode("utf-8", errors="ignore")

        if process.returncode != 0:
            print("Instagram yt-dlp error:")
            print(error_output[:4000])

            if "login required" in error_output.lower():
                await processing.edit_text(
                    "❌ <b>Login Required</b>\n\n"
                    "This Instagram post/reel requires an Instagram login."
                )
            elif "private" in error_output.lower():
                await processing.edit_text(
                    "❌ <b>Private Content</b>\n\n"
                    "Private Instagram content cannot be downloaded."
                )
            elif "not found" in error_output.lower():
                await processing.edit_text(
                    "❌ Instagram video/reel not found."
                )
            else:
                await processing.edit_text(
                    "❌ <b>Fᴀɪʟᴇᴅ Tᴏ Dᴏᴡɴʟᴏᴀᴅ</b>\n\n"
                    "The Instagram video could not be downloaded."
                )

            return

        # Find downloaded file
        downloaded_file = None

        for filename in os.listdir(temp_dir):
            filepath = os.path.join(temp_dir, filename)

            if os.path.isfile(filepath):
                downloaded_file = filepath
                break

        if not downloaded_file:
            await processing.edit_text(
                "❌ Vɪᴅᴇᴏ Fɪʟᴇ Wᴀs Nᴏᴛ Fᴏᴜɴᴅ."
            )
            return

        # Check file size
        file_size = os.path.getsize(downloaded_file)

        if file_size == 0:
            await processing.edit_text(
                "❌ Dᴏᴡɴʟᴏᴀᴅᴇᴅ Fɪʟᴇ Is Eᴍᴘᴛʏ."
            )
            return

        await processing.edit_text(
            "📤 <b>Uᴘʟᴏᴀᴅɪɴɢ Tᴏ Tᴇʟᴇɢʀᴀᴍ...</b>"
        )

        await client.send_video(
            chat_id=message.chat.id,
            video=downloaded_file,
            caption="🎬 <b>Dᴏᴡɴʟᴏᴀᴅᴇᴅ Bʏ Bᴏᴛ</b>",
            supports_streaming=True,
        )

        await processing.delete()

    except FileNotFoundError:
        print("yt-dlp is not installed or not available in PATH.")

        await processing.edit_text(
            "❌ <b>yt-dlp Nᴏᴛ Fᴏᴜɴᴅ</b>\n\n"
            "Please install yt-dlp in your requirements."
        )

    except Exception as e:
        print(f"Instagram Downloader Error: {e}")

        try:
            await processing.edit_text(
                "❌ <b>Sᴏᴍᴇᴛʜɪɴɢ Wᴇɴᴛ Wʀᴏɴɢ</b>\n\n"
                "Unable to download this Instagram video."
            )
        except Exception:
            pass

    finally:
        # Remove temporary downloaded files
        try:
            if os.path.exists(temp_dir):
                for filename in os.listdir(temp_dir):
                    filepath = os.path.join(temp_dir, filename)

                    try:
                        if os.path.isfile(filepath):
                            os.remove(filepath)
                    except Exception:
                        pass

                try:
                    os.rmdir(temp_dir)
                except Exception:
                    pass

        except Exception as e:
            print(f"Cleanup Error: {e}")


__MODULE__ = "Iɴsᴛᴀɢʀᴀᴍ"

__HELP__ = """
/reel [ɪɴsᴛᴀɢʀᴀᴍ ʀᴇᴇʟ ᴜʀʟ] - Tᴏ Dᴏᴡɴʟᴏᴀᴅ Tʜᴇ Rᴇᴇʟ Bʏ Bᴏᴛ

/ig [ɪɴsᴛᴀɢʀᴀᴍ ʀᴇᴇʟ ᴜʀʟ] - Tᴏ Dᴏᴡɴʟᴏᴀᴅ Tʜᴇ Rᴇᴇʟ Bʏ Bᴏᴛ

/instagram [ɪɴsᴛᴀɢʀᴀᴍ ʀᴇᴇʟ ᴜʀʟ] - Tᴏ Dᴏᴡɴʟᴏᴀᴅ Tʜᴇ Rᴇᴇʟ Bʏ Bᴏᴛ
"""
