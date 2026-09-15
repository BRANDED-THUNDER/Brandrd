import asyncio
import html
import logging

from pyrogram import Client

LOGGER = logging.getLogger(__name__)

VC_USERS = {}


async def send_vc_join_notification(
    client: Client,
    chat_id: int,
    user_id: int,
):
    try:
        user = await client.get_users(int(user_id))

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
            chat_id=int(chat_id),
            text=text,
            parse_mode="html",
            disable_web_page_preview=True,
        )

        LOGGER.info(
            "VC JOIN NOTIFICATION SENT | Chat: %s | User: %s",
            chat_id,
            user_id,
        )

    except Exception as e:
        LOGGER.error(
            "VC JOIN NOTIFICATION FAILED | Chat: %s | User: %s | %s",
            chat_id,
            user_id,
            e,
            exc_info=True,
        )


def _extract_user_ids(participants):
    current_users = set()

    if not participants:
        return current_users

    for participant in participants:
        try:
            user_id = None

            user = getattr(
                participant,
                "user",
                None,
            )

            if user is not None:
                user_id = getattr(
                    user,
                    "id",
                    None,
                )

            if not user_id:
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

    return current_users


async def process_vc_participants(
    client: Client,
    chat_id: int,
    participants,
):
    try:
        chat_id = int(chat_id)

        current_users = _extract_user_ids(
            participants
        )

        previous_users = VC_USERS.get(
            chat_id,
            set(),
        )

        joined_users = (
            current_users - previous_users
        )

        LOGGER.info(
            "VC CHECK | Chat: %s | Previous: %s | Current: %s | Joined: %s",
            chat_id,
            len(previous_users),
            len(current_users),
            list(joined_users),
        )

        for user_id in joined_users:

            await send_vc_join_notification(
                client=client,
                chat_id=chat_id,
                user_id=user_id,
            )

            await asyncio.sleep(
                0.3
            )

        VC_USERS[chat_id] = current_users

    except Exception as e:

        LOGGER.error(
            "VC PARTICIPANT PROCESSING FAILED | Chat: %s | %s",
            chat_id,
            e,
            exc_info=True,
        )


async def initialize_vc(
    client: Client,
    chat_id: int,
    participants,
):
    try:
        chat_id = int(chat_id)

        current_users = _extract_user_ids(
            participants
        )

        VC_USERS[chat_id] = current_users

        LOGGER.info(
            "VC INITIALIZED | Chat: %s | Existing Users: %s",
            chat_id,
            list(current_users),
        )

    except Exception as e:

        LOGGER.error(
            "VC INITIALIZATION FAILED | Chat: %s | %s",
            chat_id,
            e,
            exc_info=True,
        )


def remove_vc_cache(
    chat_id: int,
):
    chat_id = int(chat_id)

    VC_USERS.pop(
        chat_id,
        None,
    )

    LOGGER.info(
        "VC CACHE REMOVED | Chat: %s",
        chat_id,
    )


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
