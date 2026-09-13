from pyrogram import Client, filters
from pyrogram.types import Message

from BrandrdXMusic import app, userbot
from BrandrdXMusic.core.mongo import mongodb


async def vc_monitor_enabled(chat_id: int) -> bool:
    """Read the VC monitor setting directly from MongoDB."""
    data = await mongodb.vc_monitor.find_one(
        {"chat_id": int(chat_id), "enabled": True}
    )
    return bool(data)


async def set_vc_monitor(chat_id: int, enabled: bool):
    """Persist the VC monitor setting."""
    await mongodb.vc_monitor.update_one(
        {"chat_id": int(chat_id)},
        {"$set": {"enabled": bool(enabled)}},
        upsert=True,
    )


@app.on_message(filters.command("checkvc") & filters.group)
async def check_vc(client: Client, message: Message):
    """
    /checkvc       -> show status
    /checkvc on    -> enable
    /checkvc off   -> disable
    """
    chat_id = int(message.chat.id)
    command = message.command

    if len(command) == 1:
        enabled = await vc_monitor_enabled(chat_id)
        await message.reply_text(
            "🎧 **VC Monitor Status**\n\n"
            f"Status: {'🟢 ON' if enabled else '🔴 OFF'}\n\n"
            "Use `/checkvc on` to enable.\n"
            "Use `/checkvc off` to disable."
        )
        return

    if len(command) != 2 or command[1].lower() not in ("on", "off"):
        await message.reply_text(
            "❌ **Invalid command.**\n\n"
            "Use:\n"
            "`/checkvc on`\n"
            "`/checkvc off`\n"
            "`/checkvc`"
        )
        return

    enabled = command[1].lower() == "on"
    current = await vc_monitor_enabled(chat_id)

    if current == enabled:
        await message.reply_text(
            "ℹ️ **VC monitoring is already "
            + ("ON.**" if enabled else "OFF.**")
        )
        return

    await set_vc_monitor(chat_id, enabled)

    # Synchronize the in-memory state of core.call when available.
    try:
        if enabled:
            userbot.enable_vc_monitoring(chat_id)
        else:
            userbot.disable_vc_monitoring(chat_id)
    except Exception:
        pass

    if enabled:
        await message.reply_text(
            "✅ **VC monitoring enabled.**\n\n"
            "🎧 Join → notification\n"
            "👋 Leave → notification\n"
            "🚫 Removed → notification"
        )
    else:
        await message.reply_text(
            "🛑 **VC monitoring disabled.**\n\n"
            "No VC participant notifications will be sent."
        )
