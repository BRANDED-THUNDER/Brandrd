from pyrogram import filters, enums
from pyrogram.types import Message
from pyrogram.errors import UserNotParticipant

from BrandrdXMusic import app
from BrandrdXMusic.core.mongo import mongodb


# ============================================================
# MONGODB COLLECTION
# ============================================================

VC_MONITOR_COLLECTION = mongodb.vc_monitor


# ============================================================
# IN-MEMORY VC MONITOR
# ============================================================

VC_MONITOR_CHATS = set()


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
# ENABLE / DISABLE MEMORY STATE
# ============================================================

def enable_vc_monitor(chat_id: int):
    VC_MONITOR_CHATS.add(int(chat_id))


def disable_vc_monitor(chat_id: int):
    VC_MONITOR_CHATS.discard(int(chat_id))


# ============================================================
# GET USER INFORMATION
# ============================================================

def user_tag(user):
    """
    Create clickable Telegram user tag with:
    Name
    Username
    Telegram ID
    """

    if not user:
        return "👤 <b>Unknown User</b>"

    name = user.first_name or "Unknown"

    if user.last_name:
        name += f" {user.last_name}"

    username = (
        f"@{user.username}"
        if user.username
        else "Nᴏ Uѕᴇʀɴᴀᴍᴇ"
    )

    return (
        f'👤 <a href="tg://user?id={user.id}">'
        f"<b>{name}</b></a>\n"
        f"🔗 <b>Uѕᴇʀɴᴀᴍᴇ:</b> {username}\n"
        f"🆔 <b>Tᴇʟᴇɢʀᴀᴍ ID:</b> <code>{user.id}</code>"
    )


# ============================================================
# SEND VC NOTIFICATION
# ============================================================

async def send_vc_notification(
    client,
    chat_id: int,
    user,
    action: str
):

    if not user:
        return

    if action == "joined":

        text = (
            "<b><blockquote>"
            "🎤 Vᴏɪᴄᴇ Cʜᴀᴛ Jᴏɪɴᴇᴅ\n\n"
            f"{user_tag(user)}\n\n"
            "🟢 <b>Sᴛᴀᴛᴜs:</b> Jᴏɪɴᴇᴅ ᴛʜᴇ Vᴏɪᴄᴇ Cʜᴀᴛ"
            "</blockquote></b>"
        )

    elif action == "left":

        text = (
            "<b><blockquote>"
            "👋 Vᴏɪᴄᴇ Cʜᴀᴛ Lᴇғᴛ\n\n"
            f"{user_tag(user)}\n\n"
            "🔴 <b>Sᴛᴀᴛᴜs:</b> Lᴇғᴛ ᴛʜᴇ Vᴏɪᴄᴇ Cʜᴀᴛ"
            "</blockquote></b>"
        )

    elif action == "removed":

        text = (
            "<b><blockquote>"
            "🚫 Vᴏɪᴄᴇ Cʜᴀᴛ Rᴇᴍᴏᴠᴇᴅ\n\n"
            f"{user_tag(user)}\n\n"
            "⛔ <b>Sᴛᴀᴛᴜs:</b> Rᴇᴍᴏᴠᴇᴅ Fʀᴏᴍ Vᴏɪᴄᴇ Cʜᴀᴛ"
            "</blockquote></b>"
        )

    else:
        return

    try:
        await client.send_message(
            chat_id,
            text,
        )

    except Exception:
        pass


# ============================================================
# VC MEMBER INVITED / JOINED
# ============================================================

@app.on_message(filters.video_chat_members_invited)
async def vc_members_invited(client, message: Message):

    chat_id = int(message.chat.id)

    if not await vc_monitor_enabled(chat_id):
        return

    try:

        members = message.video_chat_members_invited

        if not members:
            return

        for user in members.users:

            await send_vc_notification(
                client,
                chat_id,
                user,
                "joined",
            )

    except Exception:
        pass


# ============================================================
# /CHECKVC
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

            status = (
                "🟢 Eɴᴀʙʟᴇᴅ"
                if enabled
                else
                "🔴 Dɪsᴀʙʟᴇᴅ"
            )

            await message.reply_text(
                "<b><blockquote>"
                "🎧 Vᴏɪᴄᴇ Cʜᴀᴛ Mᴏɴɪᴛᴏʀ\n\n"
                f"📊 <b>Sᴛᴀᴛᴜs:</b> {status}\n\n"
                "⚙️ <b>Cᴏᴍᴍᴀɴᴅs:</b>\n"
                "• <code>/checkvc on</code> — Eɴᴀʙʟᴇ\n"
                "• <code>/checkvc off</code> — Dɪsᴀʙʟᴇ\n"
                "• <code>/checkvc</code> — Cʜᴇᴄᴋ Sᴛᴀᴛᴜs\n\n"
                "👤 Uѕᴇʀs ᴡɪʟʟ ʙᴇ ᴛᴀɢɢᴇᴅ ᴡɪᴛʜ "
                "Uѕᴇʀɴᴀᴍᴇ + Tᴇʟᴇɢʀᴀᴍ ID."
                "</blockquote></b>",
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
                "<b><blockquote>"
                "❌ Iɴᴠᴀʟɪᴅ Cᴏᴍᴍᴀɴᴅ\n\n"
                "📝 Uѕᴇ:\n"
                "<code>/checkvc on</code>\n"
                "<code>/checkvc off</code>\n"
                "<code>/checkvc</code>"
                "</blockquote></b>",
            )

            return

        # ====================================================
        # ON / OFF
        # ====================================================

        action = command[1].lower()
        enabled = action == "on"

        current = await vc_monitor_enabled(chat_id)

        # ====================================================
        # ALREADY ENABLED / DISABLED
        # ====================================================

        if current == enabled:

            if enabled:

                await message.reply_text(
                    "<b><blockquote>"
                    "ℹ️ Vᴄ Mᴏɴɪᴛᴏʀ ɪs Aʟʀᴇᴀᴅʏ Eɴᴀʙʟᴇᴅ.\n\n"
                    "🎤 Jᴏɪɴᴇᴅ — Nᴏᴛɪғɪᴄᴀᴛɪᴏɴ\n"
                    "👋 Lᴇғᴛ — Nᴏᴛɪғɪᴄᴀᴛɪᴏɴ\n"
                    "🚫 Rᴇᴍᴏᴠᴇᴅ — Nᴏᴛɪғɪᴄᴀᴛɪᴏɴ\n\n"
                    "👤 Uѕᴇʀɴᴀᴍᴇ + 🆔 ID Wɪʟʟ Bᴇ Tᴀɢɢᴇᴅ."
                    "</blockquote></b>",
                )

            else:

                await message.reply_text(
                    "<b><blockquote>"
                    "ℹ️ Vᴄ Mᴏɴɪᴛᴏʀ ɪs Aʟʀᴇᴀᴅʏ Dɪsᴀʙʟᴇᴅ."
                    "</blockquote></b>",
                )

            return

        # ====================================================
        # SAVE MONGODB
        # ====================================================

        try:

            await set_vc_monitor(
                chat_id,
                enabled
            )

        except Exception as e:

            await message.reply_text(
                "<b><blockquote>"
                "❌ MᴏɴɢᴏDB Eʀʀᴏʀ\n\n"
                f"<code>{type(e).__name__}: {str(e)}</code>"
                "</blockquote></b>",
            )

            return

        # ====================================================
        # SYNC MEMORY
        # ====================================================

        if enabled:
            enable_vc_monitor(chat_id)
        else:
            disable_vc_monitor(chat_id)

        # ====================================================
        # SYNC WITH CALL OBJECT
        # ====================================================

        try:

            from BrandrdXMusic.core.call import Hotty

            if enabled:
                Hotty.enable_vc_monitoring(chat_id)
            else:
                Hotty.disable_vc_monitoring(chat_id)

        except Exception:
            pass

        # ====================================================
        # ENABLED RESPONSE
        # ====================================================

        if enabled:

            await message.reply_text(
                "<b><blockquote>"
                "✅ Vᴄ Mᴏɴɪᴛᴏʀ Eɴᴀʙʟᴇᴅ\n\n"
                "🎤 Jᴏɪɴᴇᴅ — Tʀᴀᴄᴋᴇᴅ\n"
                "👋 Lᴇғᴛ — Tʀᴀᴄᴋᴇᴅ\n"
                "🚫 Rᴇᴍᴏᴠᴇᴅ — Tʀᴀᴄᴋᴇᴅ\n\n"
                "👤 Uѕᴇʀɴᴀᴍᴇ + 🆔 Tᴇʟᴇɢʀᴀᴍ ID\n"
                "ᴡɪʟʟ ʙᴇ Tᴀɢɢᴇᴅ.\n\n"
                "💾 Sᴛᴀᴛᴜs Sᴀᴠᴇᴅ Tᴏ MᴏɴɢᴏDB."
                "</blockquote></b>",
            )

        # ====================================================
        # DISABLED RESPONSE
        # ====================================================

        else:

            await message.reply_text(
                "<b><blockquote>"
                "🛑 Vᴄ Mᴏɴɪᴛᴏʀ Dɪsᴀʙʟᴇᴅ\n\n"
                "🔕 Nᴏ Vᴄ Pᴀʀᴛɪᴄɪᴘᴀɴᴛ Nᴏᴛɪғɪᴄᴀᴛɪᴏɴs Wɪʟʟ Bᴇ Sᴇɴᴛ.\n\n"
                "💾 Sᴛᴀᴛᴜs Sᴀᴠᴇᴅ Tᴏ MᴏɴɢᴏDB."
                "</blockquote></b>",
            )

    except Exception as e:

        try:

            await message.reply_text(
                "<b><blockquote>"
                "❌ Vᴄ Mᴏɴɪᴛᴏʀ Eʀʀᴏʀ\n\n"
                f"<code>{type(e).__name__}: {str(e)}</code>"
                "</blockquote></b>",
            )

        except Exception:
            pass
