from pyrogram import filters
from pyrogram.types import Message

from BrandrdXMusic import app
from BrandrdXMusic.core.mongo import mongodb


# ============================================================
# MongoDB
# ============================================================

async def vc_monitor_enabled(chat_id: int) -> bool:
    try:
        data = await mongodb.vc_monitor.find_one(
            {"chat_id": int(chat_id)}
        )
        return bool(data and data.get("enabled", False))
    except Exception:
        return False


async def set_vc_monitor(chat_id: int, enabled: bool):
    await mongodb.vc_monitor.update_one(
        {"chat_id": int(chat_id)},
        {
            "$set": {
                "chat_id": int(chat_id),
                "enabled": bool(enabled),
            }
        },
        upsert=True,
    )


# ============================================================
# /checkvc
# ============================================================

@app.on_message(filters.command("checkvc") & filters.group)
async def check_vc(_, message: Message):

    chat_id = int(message.chat.id)
    command = message.command

    # --------------------------------------------------------
    # /checkvc
    # --------------------------------------------------------

    if len(command) == 1:

        enabled = await vc_monitor_enabled(chat_id)

        status = "🟢 ENABLED" if enabled else "🔴 DISABLED"

        await message.reply_text(
            "**🎧 VC Monitor**\n\n"
            f"**Status:** {status}\n\n"
            "**Commands:**\n"
            "• `/checkvc on` — Enable\n"
            "• `/checkvc off` — Disable\n"
            "• `/checkvc` — Check status"
        )

        return

    # --------------------------------------------------------
    # Invalid command
    # --------------------------------------------------------

    if (
        len(command) != 2
        or command[1].lower() not in ("on", "off")
    ):
        await message.reply_text(
            "**❌ Invalid command**\n\n"
            "Use:\n"
            "`/checkvc on`\n"
            "`/checkvc off`\n"
            "`/checkvc`"
        )
        return

    # --------------------------------------------------------
    # ON / OFF
    # --------------------------------------------------------

    enabled = command[1].lower() == "on"

    current = await vc_monitor_enabled(chat_id)

    if current == enabled:

        if enabled:
            await message.reply_text(
                "ℹ️ **VC Monitor is already enabled.**"
            )
        else:
            await message.reply_text(
                "ℹ️ **VC Monitor is already disabled.**"
            )

        return

    # Save to MongoDB
    try:
        await set_vc_monitor(chat_id, enabled)
    except Exception as e:
        await message.reply_text(
            "❌ **MongoDB Error**\n\n"
            f"`{type(e).__name__}: {e}`"
        )
        return

    # --------------------------------------------------------
    # Response
    # --------------------------------------------------------

    if enabled:

        await message.reply_text(
            "✅ **VC Monitor Enabled**\n\n"
            "🎤 A user joins the voice chat → notification\n"
            "👋 A user leaves the voice chat → notification\n"
            "🚫 A user is removed → notification"
        )

    else:

        await message.reply_text(
            "🛑 **VC Monitor Disabled**\n\n"
            "No VC participant notifications will be sent."
        )
