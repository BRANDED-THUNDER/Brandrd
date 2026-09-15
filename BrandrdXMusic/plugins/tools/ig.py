import requests
from pyrogram import filters

from BrandrdXMusic import app

import requests
from pyrogram import filters


@app.on_message(filters.command(["ig", "instagram", "reel"]))
async def download_instagram_video(client, message):
    if len(message.command) < 2:
        await message.reply_text(
            "Pʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴛʜᴇ Iɴsᴛᴀɢʀᴀᴍ ʀᴇᴇʟ URL ᴀғᴛᴇʀ ᴛʜᴇ ᴄᴏᴍᴍᴀɴᴅ"
        )
        return

    url = message.command[1].strip()

    if "instagram.com" not in url:
        await message.reply_text(
            "❌ Pʟᴇᴀsᴇ sᴇɴᴅ ᴀ ᴠᴀʟɪᴅ Iɴsᴛᴀɢʀᴀᴍ URL."
        )
        return

    processing = await message.reply_text("ᴘʀᴏᴄᴇssɪɴɢ...")

    api_url = (
        "https://nodejs-1xn1lcfy3-jobians.vercel.app/"
        "v2/downloader/instagram"
    )

    try:
        # Send URL as a parameter safely
        response = requests.get(
            api_url,
            params={"url": url},
            timeout=30,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 Chrome/120.0 Safari/537.36"
                )
            },
        )

        # Check HTTP status first
        if response.status_code != 200:
            await processing.edit_text(
                f"❌ Iɴsᴛᴀɢʀᴀᴍ API Eʀʀᴏʀ\n"
                f"Sᴛᴀᴛᴜs: `{response.status_code}`"
            )
            return

        # Prevent JSONDecodeError
        if not response.text.strip():
            await processing.edit_text(
                "❌ Iɴsᴛᴀɢʀᴀᴍ API returned an empty response."
            )
            return

        try:
            data = response.json()
        except ValueError:
            print("Instagram API response:")
            print(response.text[:2000])

            await processing.edit_text(
                "❌ Iɴsᴛᴀɢʀᴀᴍ API returned an invalid response."
            )
            return

        # Check API response
        if not isinstance(data, dict):
            await processing.edit_text(
                "❌ Iɴᴠᴀʟɪᴅ API response."
            )
            return

        if not data.get("status"):
            message_text = data.get(
                "message",
                "Fᴀɪʟᴇᴅ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ Rᴇᴇʟ"
            )

            await processing.edit_text(
                f"❌ {message_text}"
            )
            return

        # Get data safely
        result = data.get("data")

        if not result:
            await processing.edit_text(
                "❌ Nᴏ ᴠɪᴅᴇᴏ ғᴏᴜɴᴅ ɪɴ API response."
            )
            return

        # API may return list or dictionary
        video_url = None

        if isinstance(result, list):
            for item in result:
                if isinstance(item, dict):
                    video_url = (
                        item.get("url")
                        or item.get("download")
                        or item.get("video")
                    )

                    if video_url:
                        break

        elif isinstance(result, dict):
            video_url = (
                result.get("url")
                or result.get("download")
                or result.get("video")
            )

        if not video_url:
            await processing.edit_text(
                "❌ Vɪᴅᴇᴏ URL API response ᴍᴇɪɴ ɴᴀʜɪ ᴍɪʟᴀ."
            )
            return

        await processing.edit_text("ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ...")

        # Telegram can download directly from a URL
        await client.send_video(
            chat_id=message.chat.id,
            video=video_url,
            caption="🎬 Dᴏᴡɴʟᴏᴀᴅᴇᴅ Bʏ Bᴏᴛ",
        )

        await processing.delete()

    except requests.exceptions.Timeout:
        await processing.edit_text(
            "❌ Iɴsᴛᴀɢʀᴀᴍ API ᴛɪᴍᴇᴅ ᴏᴜᴛ. Pʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ."
        )

    except requests.exceptions.RequestException as e:
        print(f"Instagram Request Error: {e}")

        await processing.edit_text(
            "❌ Fᴀɪʟᴇᴅ ᴛᴏ ᴄᴏɴɴᴇᴄᴛ ᴛᴏ Iɴsᴛᴀɢʀᴀᴍ API."
        )

    except Exception as e:
        print(f"Instagram Downloader Error: {e}")

        await processing.edit_text(
            "❌ Sᴏᴍᴇᴛʜɪɴɢ Wᴇɴᴛ Wʀᴏɴɢ Wʜɪʟᴇ Dᴏᴡɴʟᴏᴀᴅɪɴɢ."
        )


__MODULE__ = "Iɴsᴛᴀɢʀᴀᴍ"

__HELP__ = """
/reel [ɪɴsᴛᴀɢʀᴀᴍ ʀᴇᴇʟ ᴜʀʟ] - Tᴏ Dᴏᴡɴʟᴏᴀᴅ Tʜᴇ Rᴇᴇʟ Bʏ Bᴏᴛ

/ig [ɪɴsᴛᴀɢʀᴀᴍ ʀᴇᴇʟ ᴜʀʟ] - Tᴏ Dᴏᴡɴʟᴏᴀᴅ Tʜᴇ Rᴇᴇʟ Bʏ Bᴏᴛ

/instagram [ɪɴsᴛᴀɢʀᴀᴍ ʀᴇᴇʟ ᴜʀʟ] - Tᴏ Dᴏᴡɴʟᴏᴀᴅ Tʜᴇ Rᴇᴇʟ Bʏ Bᴏᴛ
"""
