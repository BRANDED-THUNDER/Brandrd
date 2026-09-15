import asyncio
import html
import logging
from typing import Any, Set

from pyrogram import Client


LOGGER = logging.getLogger(__name__)

# ---------------------------------------------------------
# VC USER CACHE
# chat_id -> set(user_id)
# ---------------------------------------------------------

VC_USERS = {}


# ---------------------------------------------------------
# USER ID EXTRACTION
# ---------------------------------------------------------

def _extract_user_id(participant: Any):
    """
    Safely extract Telegram user ID from different
    PyTgCalls / Pyrogram participant object formats.
    """

    try:
        if participant is None:
            return None

        # ---------------------------------------------
        # participant.user.id
        # ---------------------------------------------

        user = getattr(participant, "user", None)

        if user is not None:
            user_id = getattr(user, "id", None)

            if user_id:
                return int(user_id)

        # ---------------------------------------------
        # participant.user_id
        # ---------------------------------------------

        user_id = getattr(
            participant,
            "user_id",
            None,
        )

        if user_id:
            return int(user_id)

        # ---------------------------------------------
        # participant.participant.user_id
        # ---------------------------------------------

        nested = getattr(
            participant,
            "participant",
            None,
        )

        if nested is not None:

            user_id = getattr(
                nested,
                "user_id",
                None,
            )

            if user_id:
                return int(user_id)

        # ---------------------------------------------
        # participant.peer.user_id
        # ---------------------------------------------

        peer = getattr(
            participant,
            "peer",
            None,
        )

        if peer is not None:

            user_id = getattr(
                peer,
                "user_id",
                None,
            )

            if user_id:
                return int(user_id)

    except Exception as e:

        LOGGER.debug(
            "VC USER ID EXTRACTION FAILED | Participant: %r | Error: %s",
            participant,
            e,
        )

    return None


# ---------------------------------------------------------
# EXTRACT ALL PARTICIPANT IDS
# ---------------------------------------------------------

def _extract_user_ids(participants) -> Set[int]:

    current_users = set()

    if not participants:
        return current_users

    try:

        for participant in participants:

            try:

                user_id = _extract_user_id(
                    participant
                )

                if user_id:
                    current_users.add(
                        int(user_id)
                    )

            except Exception as e:

                LOGGER.debug(
                    "VC PARTICIPANT SKIPPED | Error: %s",
                    e,
                )

    except Exception as e:

        LOGGER.error(
            "VC PARTICIPANT LIST EXTRACTION FAILED | %s",
            e,
            exc_info=True,
        )

    return current_users


# ---------------------------------------------------------
# SEND JOIN NOTIFICATION
# ---------------------------------------------------------

async def send_vc_join_notification(
    client: Client,
    chat_id: int,
    user_id: int,
):

    try:

        chat_id = int(chat_id)
        user_id = int(user_id)

        LOGGER.info(
            "VC JOIN NOTIFICATION PREPARING | Chat: %s | User: %s",
            chat_id,
            user_id,
        )

        # ---------------------------------------------
        # GET TELEGRAM USER
        # ---------------------------------------------

        user = await client.get_users(
            user_id
        )

        # ---------------------------------------------
        # USERNAME / NAME
        # ---------------------------------------------

        if user.username:

            username = (
                "@"
                + html.escape(
                    user.username
                )
            )

        else:

            username = html.escape(
                user.first_name
                or user.last_name
                or "Unknown"
            )

        # ---------------------------------------------
        # MESSAGE
        # ---------------------------------------------

        text = (
            "<b>#JoinVc</b>\n\n"
            f"<b>👤 User:</b> {username}\n"
            f"<b>🆔 UserID:</b> "
            f"<code>{user.id}</code>\n"
            "<b>🔐 Auth:</b> Member"
        )

        LOGGER.info(
            "VC JOIN MESSAGE READY | Chat: %s | User: %s | Text: %s",
            chat_id,
            user_id,
            text,
        )

        # ---------------------------------------------
        # SEND MESSAGE
        # ---------------------------------------------

        await client.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode="html",
            disable_web_page_preview=True,
        )

        LOGGER.info(
            "VC JOIN NOTIFICATION SENT | Chat: %s | User: %s",
            chat_id,
            user_id,
        )

        return True

    except Exception as e:

        LOGGER.error(
            "VC JOIN NOTIFICATION FAILED | "
            "Chat: %s | User: %s | Error: %s",
            chat_id,
            user_id,
            e,
            exc_info=True,
        )

        return False


# ---------------------------------------------------------
# PROCESS VC PARTICIPANTS
# ---------------------------------------------------------

async def process_vc_participants(
    client: Client,
    chat_id: int,
    participants,
):

    try:

        chat_id = int(chat_id)

        # ---------------------------------------------
        # CURRENT PARTICIPANTS
        # ---------------------------------------------

        current_users = _extract_user_ids(
            participants
        )

        # ---------------------------------------------
        # PREVIOUS PARTICIPANTS
        # ---------------------------------------------

        previous_users = VC_USERS.get(
            chat_id,
            set(),
        )

        # Always make a copy so external mutation
        # cannot affect our cache.
        previous_users = set(
            previous_users
        )

        # ---------------------------------------------
        # FIND NEW USERS
        # ---------------------------------------------

        joined_users = (
            current_users
            - previous_users
        )

        # ---------------------------------------------
        # FIND LEFT USERS
        # ---------------------------------------------

        left_users = (
            previous_users
            - current_users
        )

        LOGGER.info(
            "VC CHECK | "
            "Chat: %s | "
            "Previous: %s | "
            "Current: %s | "
            "Joined: %s | "
            "Left: %s",
            chat_id,
            len(previous_users),
            len(current_users),
            list(joined_users),
            list(left_users),
        )

        # ---------------------------------------------
        # IMPORTANT:
        # UPDATE CACHE FIRST
        #
        # This prevents duplicate notifications if
        # two VC update callbacks arrive together.
        # ---------------------------------------------

        VC_USERS[chat_id] = set(
            current_users
        )

        # ---------------------------------------------
        # NO NEW USER
        # ---------------------------------------------

        if not joined_users:

            LOGGER.debug(
                "VC NO NEW PARTICIPANT | Chat: %s",
                chat_id,
            )

            return

        # ---------------------------------------------
        # SEND JOIN NOTIFICATION
        # ---------------------------------------------

        for user_id in sorted(
            joined_users
        ):

            LOGGER.info(
                "VC NEW PARTICIPANT DETECTED | "
                "Chat: %s | User: %s",
                chat_id,
                user_id,
            )

            await send_vc_join_notification(
                client=client,
                chat_id=chat_id,
                user_id=user_id,
            )

            # Small delay prevents Telegram flood
            # when multiple users join together.
            await asyncio.sleep(
                0.3
            )

    except Exception as e:

        LOGGER.error(
            "VC PARTICIPANT PROCESSING FAILED | "
            "Chat: %s | Error: %s",
            chat_id,
            e,
            exc_info=True,
        )


# ---------------------------------------------------------
# INITIALIZE VC CACHE
# ---------------------------------------------------------

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

        # ---------------------------------------------
        # IMPORTANT:
        # Initialization NEVER sends notifications.
        #
        # These users are already inside VC when
        # monitoring starts.
        # ---------------------------------------------

        VC_USERS[chat_id] = set(
            current_users
        )

        LOGGER.info(
            "VC INITIALIZED | "
            "Chat: %s | "
            "Existing Users: %s",
            chat_id,
            sorted(current_users),
        )

    except Exception as e:

        LOGGER.error(
            "VC INITIALIZATION FAILED | "
            "Chat: %s | Error: %s",
            chat_id,
            e,
            exc_info=True,
        )


# ---------------------------------------------------------
# REMOVE VC CACHE
# ---------------------------------------------------------

def remove_vc_cache(
    chat_id: int,
):

    try:

        chat_id = int(chat_id)

        old_users = VC_USERS.pop(
            chat_id,
            None,
        )

        LOGGER.info(
            "VC CACHE REMOVED | "
            "Chat: %s | Previous Users: %s",
            chat_id,
            sorted(old_users or set()),
        )

    except Exception as e:

        LOGGER.error(
            "VC CACHE REMOVE FAILED | "
            "Chat: %s | Error: %s",
            chat_id,
            e,
            exc_info=True,
        )


# ---------------------------------------------------------
# MODULE INFO
# ---------------------------------------------------------

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
