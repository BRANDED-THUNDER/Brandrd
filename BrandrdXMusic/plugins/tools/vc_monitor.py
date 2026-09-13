from pyrogram import filters
from pyrogram.types import Message

from BrandrdXMusic import app
from BrandrdXMusic.core.mongo import mongodb


# ============================================================
# MongoDB COLLECTION
# ============================================================

VC_MONITOR_COLLECTION = mongodb.vc_monitor


# ============================================================
# CHECK VC MONITOR STATUS
# ============================================================

async def vc_monitor_enabled(chat_id: int) -> bool:
    """
    Return True if VC monitor is enabled for this chat.
    """

    try:
        chat_id = int(chat_id)

        data = await VC_MONITOR_COLLECTION.find_one(
            {"chat_id": chat_id}
        )

        if not data:
            return False

        return bool(data.get("enabled", False))

    except Exception:
        return False


# ============================================================
# SET VC MONITOR STATUS
# ============================================================

async def set_vc_monitor(chat_id: int, enabled: bool) -> bool:
    """
    Enable or disable VC monitor for a chat.
    """

    chat_id = int(chat_id)
    enabled = bool(enabled)

    await VC_MONITOR_COLLECTION.update_one(
        {"chat_id": chat_id},
        {
            "$set": {
                "chat_id": chat_id,
                "enabled": enabled,
            }
        },
        upsert=True,
    )

    return True


# ============================================================
# /checkvc
# ============================================================

@app.on_message(
    filters.command("checkvc") & filters.group
)
async def check_vc(client, message: Message):

    chat_id = int(message.chat.id)

    try:
        command = message.command or []

        # ====================================================
        # /checkvc
        # ====================================================

        if len(command) == 1:

            enabled = await vc_monitor_enabled(chat_id)

            if enabled:
                status = "🟢 ENABLED"
            else:
                status = "🔴 DISABLED"

            await message.reply_text(
                "**🎧 VC Monitor**\n\n"
                f"**Status:** {status}\n\n"
                "**Commands:**\n"
                "• `/checkvc on` — Enable\n"
                "• `/checkvc off` — Disable\n"
                "• `/checkvc` — Check status"
            )

            return

        # ====================================================
        # INVALID COMMAND
        # ====================================================

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

        # ====================================================
        # ON / OFF
        # ====================================================

        action = command[1].lower()
        enabled = action == "on"

        # Check current status
        current = await vc_monitor_enabled(chat_id)

        # ====================================================
        # ALREADY ENABLED / DISABLED
        # ====================================================

        if current == enabled:

            if enabled:
                await message.reply_text(
                    "ℹ️ **VC Monitor is already enabled.**\n\n"
                    "Users joining, leaving or being removed "
                    "from the Voice Chat will be monitored."
                )
            else:
                await message.reply_text(
                    "ℹ️ **VC Monitor is already disabled.**"
                )

            return

        # ====================================================
        # SAVE TO MONGODB
        # ====================================================

        try:

            await set_vc_monitor(
                chat_id,
                enabled
            )

        except Exception as e:

            await message.reply_text(
                "❌ **MongoDB Error**\n\n"
                f"`{type(e).__name__}: {str(e)}`"
            )

            return

        # ====================================================
        # SYNC WITH CALL OBJECT
        #
        # This keeps the in-memory monitor state synchronized
        # immediately after /checkvc on/off.
        # ====================================================

        try:

            from BrandrdXMusic.core.call import Hotty

            if enabled:
                Hotty.enable_vc_monitoring(chat_id)
            else:
                Hotty.disable_vc_monitoring(chat_id)

        except Exception:
            # MongoDB is still the permanent source of truth.
            pass

        # ====================================================
        # ENABLED RESPONSE
        # ====================================================

        if enabled:

            await message.reply_text(
                "✅ **VC Monitor Enabled**\n\n"
                "🎤 **Joined:** notification will be sent\n"
                "👋 **Left:** notification will be sent\n"
                "🚫 **Removed:** notification will be sent\n\n"
                "💾 **Status saved to MongoDB.**"
            )

        # ====================================================
        # DISABLED RESPONSE
        # ====================================================

        else:

            await message.reply_text(
                "🛑 **VC Monitor Disabled**\n\n"
                "No VC participant notifications will be sent.\n\n"
                "💾 **Status saved to MongoDB.**"
            )

    except Exception as e:

        try:
            await message.reply_text(
                "❌ **VC Monitor Error**\n\n"
                f"`{type(e).__name__}: {str(e)}`"
            )
        except Exception:
            pass
