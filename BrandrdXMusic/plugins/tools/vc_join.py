# BrandrdXMusic/plugins/tools/vc_join.py

import html
import logging
import asyncio

from pyrogram import Client

from BrandrdXMusic import app

LOGGER = logging.getLogger(__name__)


# ============================================================
# VC JOIN NOTIFICATION
# ============================================================

async def send_vc_join_notification(
    client: Client,
    chat_id: int,
    user_id: int,
):
    """
    Send VC join notification in the same group
    where the user joined the Voice Chat.
    """

    try:
        user = await client.get_users(user_id)

        if user.username:
            username = f"@{html.escape(user.username)}"
        else:
            username = html.escape(
                user.first_name or "Unknown"
            )

        text = (
            "<b>#JoinVc</b>\n\n"
            f"<b>👤 User:</b> {username}\n"
            f"<b>🆔 UserID:</b> <code>{user.id}</code>\n"
            "<b>🔐 Auth:</b> Member"
        )

        await client.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode="html",
            disable_web_page_preview=True,
        )

        LOGGER.info(
            "VC JOIN | Chat: %s | User: %s",
            chat_id,
            user_id,
        )

    except Exception as e:
        LOGGER.exception(
            "VC JOIN notification failed: %s",
            e,
        )


# ============================================================
# PARTICIPANT CACHE
# ============================================================

# {
#     chat_id: {
#         user_id,
#         user_id,
#         user_id
#     }
# }
#
# This keeps track of users already detected in VC.

VC_USERS = {}


# ============================================================
# PROCESS VC PARTICIPANTS
# ============================================================

async def process_vc_participants(
    client: Client,
    chat_id: int,
    participants,
):
    """
    Compare the previous VC participant list with
    the current list.

    New users are treated as VC joins.
    """

    try:

        current_users = set()

        # -----------------------------------------
        # Extract current participant IDs
        # -----------------------------------------

        for participant in participants:

            try:
                user = getattr(participant, "user", None)

                if user:
                    user_id = user.id
                else:
                    user_id = getattr(
                        participant,
                        "user_id",
                        None,
                    )

                if user_id:
                    current_users.add(int(user_id))

            except Exception:
                continue

        # -----------------------------------------
        # Previous users
        # -----------------------------------------

        previous_users = VC_USERS.get(
            chat_id,
            set(),
        )

        # -----------------------------------------
        # Detect newly joined users
        # -----------------------------------------

        joined_users = (
            current_users - previous_users
        )

        # -----------------------------------------
        # Send notification
        # -----------------------------------------

        for user_id in joined_users:

            await send_vc_join_notification(
                client=client,
                chat_id=chat_id,
                user_id=user_id,
            )

            # Small delay prevents Telegram flood
            await asyncio.sleep(0.3)

        # -----------------------------------------
        # Update cache
        # -----------------------------------------

        VC_USERS[chat_id] = current_users

    except Exception as e:

        LOGGER.exception(
            "VC participant processing failed: %s",
            e,
        )


# ============================================================
# INITIALIZE VC
# ============================================================

async def initialize_vc(
    client: Client,
    chat_id: int,
    participants,
):
    """
    Use this when the VC monitor starts.

    IMPORTANT:
    Existing participants are stored without sending
    #JoinVc notifications.

    This prevents the bot from announcing everyone already
    inside the VC as a new join.
    """

    try:

        current_users = set()

        for participant in participants:

            try:

                user = getattr(
                    participant,
                    "user",
                    None,
                )

                if user:
                    user_id = user.id
                else:
                    user_id = getattr(
                        participant,
                        "user_id",
                        None,
                    )

                if user_id:
                    current_users.add(
                        int(user_id)
                    )

            except Exception:
                continue

        VC_USERS[chat_id] = current_users

    except Exception as e:

        LOGGER.exception(
            "VC initialization failed: %s",
            e,
        )


# ============================================================
# REMOVE VC CACHE
# ============================================================

def remove_vc_cache(chat_id: int):
    """
    Remove cached participant data when VC ends.
    """

    VC_USERS.pop(
        chat_id,
        None,
    )


# ============================================================
# MODULE INFORMATION
# ============================================================

__MODULE__ = "VC Join"

__HELP__ = """
<b>🎙️ VC Jᴏɪɴ Lᴏɢ</b>

<blockquote>
<b>#JoinVc</b>

👤 User: @username
🆔 UserID: 123456789
🔐 Auth: Member

Notifications are sent directly
to the same group where the user
joins the Voice Chat.
</blockquote>
"""
