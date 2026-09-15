import asyncio
import os
from datetime import datetime, timedelta
from typing import Union

from pyrogram import Client
from pyrogram.types import InlineKeyboardMarkup

from ntgcalls import TelegramServerError
from pytgcalls import PyTgCalls

from pytgcalls.exceptions import (
    AlreadyJoinedError,
    NoActiveGroupCall,
)

from pytgcalls.types import (
    MediaStream,
    AudioQuality,
    VideoQuality,
    Update,
)
from pytgcalls.types.stream import StreamAudioEnded

import config
from BrandrdXMusic import LOGGER, YouTube, app
from BrandrdXMusic.misc import db

from BrandrdXMusic.utils.database import (
    add_active_chat,
    add_active_video_chat,
    get_lang,
    get_loop,
    group_assistant,
    is_autoend,
    music_on,
    remove_active_chat,
    remove_active_video_chat,
    set_loop,
)

from BrandrdXMusic.utils.exceptions import AssistantErr

from BrandrdXMusic.utils.formatters import (
    check_duration,
    seconds_to_min,
    speed_converter,
)

from BrandrdXMusic.utils.inline.play import (
    stream_markup,
    stream_markup2,
)

from BrandrdXMusic.utils.stream.autoclear import auto_clean
from BrandrdXMusic.utils.thumbnails import get_thumb
from strings import get_string


# ============================================================
# VC JOIN MONITOR
# ============================================================

try:

    from BrandrdXMusic.plugins.tools.vc_join import (
        process_vc_participants,
        initialize_vc,
        remove_vc_cache,
    )

    VC_JOIN_AVAILABLE = True

    LOGGER(__name__).info(
        "VC JOIN MODULE LOADED SUCCESSFULLY"
    )

except Exception as e:

    process_vc_participants = None
    initialize_vc = None
    remove_vc_cache = None

    VC_JOIN_AVAILABLE = False

    LOGGER(__name__).error(
        "VC JOIN MODULE IMPORT FAILED | %s",
        e,
        exc_info=True,
    )


# ============================================================
# GLOBALS
# ============================================================

autoend = {}
counter = {}

loop = asyncio.get_event_loop_policy().get_event_loop()


# ============================================================
# CLEAR CHAT
# ============================================================

async def _clear_(chat_id):

    db[chat_id] = []

    await remove_active_video_chat(
        chat_id
    )

    await remove_active_chat(
        chat_id
    )


# ============================================================
# CALL CLASS
# ============================================================

class Call(PyTgCalls):

    def __init__(self):

        # ----------------------------------------------------
        # VC MONITOR STATE
        # ----------------------------------------------------

        self._vc_monitor_tasks = {}
        self._vc_monitor_running = set()

        # ----------------------------------------------------
        # USERBOT 1
        # ----------------------------------------------------

        self.userbot1 = Client(
            name="BrandrdXMusic1",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING1),
        )

        self.one = PyTgCalls(
            self.userbot1,
            cache_duration=100,
        )

        # ----------------------------------------------------
        # USERBOT 2
        # ----------------------------------------------------

        self.userbot2 = Client(
            name="BrandrdXMusic2",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING2),
        )

        self.two = PyTgCalls(
            self.userbot2,
            cache_duration=100,
        )

        # ----------------------------------------------------
        # USERBOT 3
        # ----------------------------------------------------

        self.userbot3 = Client(
            name="BrandrdXMusic3",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING3),
        )

        self.three = PyTgCalls(
            self.userbot3,
            cache_duration=100,
        )

        # ----------------------------------------------------
        # USERBOT 4
        # ----------------------------------------------------

        self.userbot4 = Client(
            name="BrandrdXMusic4",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING4),
        )

        self.four = PyTgCalls(
            self.userbot4,
            cache_duration=100,
        )

        # ----------------------------------------------------
        # USERBOT 5
        # ----------------------------------------------------

        self.userbot5 = Client(
            name="BrandrdXMusic5",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING5),
        )

        self.five = PyTgCalls(
            self.userbot5,
            cache_duration=100,
        )

        LOGGER(__name__).info(
            "CALL CLIENTS INITIALIZED"
        )

    # ========================================================
    # VC MONITOR LOOP
    # ========================================================

    async def _vc_monitor_loop(
        self,
        chat_id: int,
        assistant,
    ):

        chat_id = int(chat_id)

        initialized = False

        try:

            LOGGER(__name__).info(
                "=================================================="
            )

            LOGGER(__name__).info(
                "VC MONITOR LOOP STARTED | Chat: %s",
                chat_id,
            )

            LOGGER(__name__).info(
                "VC MONITOR ASSISTANT | %s",
                type(assistant).__name__,
            )

            while chat_id in self._vc_monitor_running:

                try:

                    # ------------------------------------------------
                    # GET CURRENT VC PARTICIPANTS
                    # ------------------------------------------------

                    participants = (
                        await assistant.get_group_call_participants(
                            chat_id
                        )
                    )

                    if participants is None:
                        participants = []

                    LOGGER(__name__).info(
                        "VC PARTICIPANTS FETCHED | "
                        "Chat: %s | Count: %s",
                        chat_id,
                        len(participants),
                    )

                    # ------------------------------------------------
                    # INITIAL SNAPSHOT
                    # ------------------------------------------------

                    if not initialized:

                        if initialize_vc is not None:

                            await initialize_vc(
                                client=app,
                                chat_id=chat_id,
                                participants=participants,
                            )

                            LOGGER(__name__).info(
                                "VC INITIALIZE_VC EXECUTED | "
                                "Chat: %s",
                                chat_id,
                            )

                        initialized = True

                        LOGGER(__name__).info(
                            "VC INITIAL SNAPSHOT DONE | "
                            "Chat: %s | Existing Users: %s",
                            chat_id,
                            len(participants),
                        )

                    # ------------------------------------------------
                    # CHECK NEW USERS
                    # ------------------------------------------------

                    else:

                        if process_vc_participants is not None:

                            await process_vc_participants(
                                client=app,
                                chat_id=chat_id,
                                participants=participants,
                            )

                            LOGGER(__name__).info(
                                "VC PARTICIPANT PROCESS COMPLETE | "
                                "Chat: %s | Users: %s",
                                chat_id,
                                len(participants),
                            )

                        else:

                            LOGGER(__name__).warning(
                                "VC PROCESS FUNCTION IS NONE | "
                                "Chat: %s",
                                chat_id,
                            )

                except asyncio.CancelledError:

                    raise

                except AttributeError as e:

                    LOGGER(__name__).error(
                        "VC API METHOD ERROR | "
                        "Chat: %s | %s",
                        chat_id,
                        e,
                        exc_info=True,
                    )

                except Exception as e:

                    LOGGER(__name__).error(
                        "VC PARTICIPANT FETCH ERROR | "
                        "Chat: %s | %s",
                        chat_id,
                        e,
                        exc_info=True,
                    )

                # ------------------------------------------------
                # CHECK EVERY 2 SECONDS
                # ------------------------------------------------

                await asyncio.sleep(
                    2
                )

        except asyncio.CancelledError:

            LOGGER(__name__).info(
                "VC MONITOR CANCELLED | Chat: %s",
                chat_id,
            )

            raise

        except Exception as e:

            LOGGER(__name__).error(
                "VC MONITOR CRASHED | "
                "Chat: %s | %s",
                chat_id,
                e,
                exc_info=True,
            )

        finally:

            # ------------------------------------------------
            # REMOVE RUNNING STATE
            # ------------------------------------------------

            self._vc_monitor_running.discard(
                chat_id
            )

            # ------------------------------------------------
            # REMOVE TASK
            # ------------------------------------------------

            self._vc_monitor_tasks.pop(
                chat_id,
                None,
            )

            # ------------------------------------------------
            # REMOVE CACHE
            # ------------------------------------------------

            if remove_vc_cache is not None:

                try:

                    remove_vc_cache(
                        chat_id
                    )

                    LOGGER(__name__).info(
                        "VC CACHE REMOVED | Chat: %s",
                        chat_id,
                    )

                except Exception as e:

                    LOGGER(__name__).warning(
                        "VC CACHE REMOVE FAILED | "
                        "Chat: %s | %s",
                        chat_id,
                        e,
                    )

            LOGGER(__name__).info(
                "VC MONITOR CLEANED | Chat: %s",
                chat_id,
            )

            LOGGER(__name__).info(
                "=================================================="
            )

    # ========================================================
    # START VC MONITOR
    # ========================================================

    async def _start_vc_monitor(
        self,
        chat_id: int,
        assistant,
    ):

        chat_id = int(chat_id)

        # ----------------------------------------------------
        # MODULE CHECK
        # ----------------------------------------------------

        if not VC_JOIN_AVAILABLE:

            LOGGER(__name__).error(
                "VC JOIN MONITOR UNAVAILABLE | "
                "Chat: %s",
                chat_id,
            )

            return

        # ----------------------------------------------------
        # CHECK EXISTING TASK
        # ----------------------------------------------------

        existing_task = (
            self._vc_monitor_tasks.get(
                chat_id
            )
        )

        if (
            existing_task
            and not existing_task.done()
        ):

            LOGGER(__name__).info(
                "VC MONITOR ALREADY RUNNING | "
                "Chat: %s",
                chat_id,
            )

            return

        # ----------------------------------------------------
        # REMOVE OLD CACHE
        # ----------------------------------------------------

        if remove_vc_cache is not None:

            try:

                remove_vc_cache(
                    chat_id
                )

            except Exception:
                pass

        # ----------------------------------------------------
        # ADD RUNNING STATE
        # ----------------------------------------------------

        self._vc_monitor_running.add(
            chat_id
        )

        # ----------------------------------------------------
        # CREATE TASK
        # ----------------------------------------------------

        task = asyncio.create_task(
            self._vc_monitor_loop(
                chat_id,
                assistant,
            )
        )

        self._vc_monitor_tasks[
            chat_id
        ] = task

        LOGGER(__name__).info(
            "VC MONITOR STARTED | Chat: %s",
            chat_id,
        )

    # ========================================================
    # STOP VC MONITOR
    # ========================================================

    async def _stop_vc_monitor(
        self,
        chat_id: int,
    ):

        chat_id = int(chat_id)

        # ----------------------------------------------------
        # REMOVE RUNNING STATE
        # ----------------------------------------------------

        self._vc_monitor_running.discard(
            chat_id
        )

        # ----------------------------------------------------
        # GET TASK
        # ----------------------------------------------------

        task = self._vc_monitor_tasks.pop(
            chat_id,
            None,
        )

        # ----------------------------------------------------
        # CANCEL TASK
        # ----------------------------------------------------

        if task and not task.done():

            task.cancel()

            try:

                await task

            except asyncio.CancelledError:
                pass

            except Exception as e:

                LOGGER(__name__).warning(
                    "VC MONITOR STOP ERROR | "
                    "Chat: %s | %s",
                    chat_id,
                    e,
                )

        # ----------------------------------------------------
        # REMOVE CACHE
        # ----------------------------------------------------

        if remove_vc_cache is not None:

            try:

                remove_vc_cache(
                    chat_id
                )

            except Exception as e:

                LOGGER(__name__).warning(
                    "VC CACHE REMOVE ERROR | "
                    "Chat: %s | %s",
                    chat_id,
                    e,
                )

        LOGGER(__name__).info(
            "VC MONITOR STOPPED | Chat: %s",
            chat_id,
        )

    # ========================================================
    # PAUSE
    # ========================================================

    async def pause_stream(
        self,
        chat_id: int,
    ):

        assistant = await group_assistant(
            self,
            chat_id,
        )

        await assistant.pause_stream(
            chat_id
        )

    # ========================================================
    # MUTE
    # ========================================================

    async def mute_stream(
        self,
        chat_id: int,
    ):

        assistant = await group_assistant(
            self,
            chat_id,
        )

        await assistant.mute_stream(
            chat_id
        )

    # ========================================================
    # UNMUTE
    # ========================================================

    async def unmute_stream(
        self,
        chat_id: int,
    ):

        assistant = await group_assistant(
            self,
            chat_id,
        )

        await assistant.unmute_stream(
            chat_id
        )

    # ========================================================
    # GET PARTICIPANTS
    # ========================================================

    async def get_participant(
        self,
        chat_id: int,
    ):

        assistant = await group_assistant(
            self,
            chat_id,
        )

        try:

            participant = (
                await assistant.get_group_call_participants(
                    chat_id
                )
            )

            if participant is None:

                participant = []

            LOGGER(__name__).info(
                "GET PARTICIPANTS | "
                "Chat: %s | Count: %s",
                chat_id,
                len(participant),
            )

            return participant

        except Exception as e:

            LOGGER(__name__).error(
                "GET PARTICIPANTS FAILED | "
                "Chat: %s | %s",
                chat_id,
                e,
                exc_info=True,
            )

            return []

    # ========================================================
    # RESUME
    # ========================================================

    async def resume_stream(
        self,
        chat_id: int,
    ):

        assistant = await group_assistant(
            self,
            chat_id,
        )

        await assistant.resume_stream(
            chat_id
        )

    # ========================================================
    # STOP STREAM
    # ========================================================

    async def stop_stream(
        self,
        chat_id: int,
    ):

        assistant = await group_assistant(
            self,
            chat_id,
        )

        try:

            await self._stop_vc_monitor(
                chat_id
            )

            await _clear_(
                chat_id
            )

            await assistant.leave_group_call(
                chat_id
            )

        except Exception:

            pass

    # ========================================================
    # FORCE STOP ALL
    # ========================================================

    async def stop_stream_force(
        self,
        chat_id: int,
    ):

        await self._stop_vc_monitor(
            chat_id
        )

        # ----------------------------------------------------
        # ASSISTANT 1
        # ----------------------------------------------------

        try:

            if config.STRING1:

                await self.one.leave_group_call(
                    chat_id
                )

        except Exception:
            pass

        # ----------------------------------------------------
        # ASSISTANT 2
        # ----------------------------------------------------

        try:

            if config.STRING2:

                await self.two.leave_group_call(
                    chat_id
                )

        except Exception:
            pass

        # ----------------------------------------------------
        # ASSISTANT 3
        # ----------------------------------------------------

        try:

            if config.STRING3:

                await self.three.leave_group_call(
                    chat_id
                )

        except Exception:
            pass

        # ----------------------------------------------------
        # ASSISTANT 4
        # ----------------------------------------------------

        try:

            if config.STRING4:

                await self.four.leave_group_call(
                    chat_id
                )

        except Exception:
            pass

        # ----------------------------------------------------
        # ASSISTANT 5
        # ----------------------------------------------------

        try:

            if config.STRING5:

                await self.five.leave_group_call(
                    chat_id
                )

        except Exception:
            pass

        # ----------------------------------------------------
        # CLEAR DATABASE
        # ----------------------------------------------------

        try:

            await _clear_(
                chat_id
            )

        except Exception:
            pass

    # ========================================================
    # SPEEDUP STREAM
    # ========================================================

    async def speedup_stream(
        self,
        chat_id: int,
        file_path,
        speed,
        playing,
    ):

        assistant = await group_assistant(
            self,
            chat_id,
        )

        if str(speed) != "1.0":

            base = os.path.basename(
                file_path
            )

            chatdir = os.path.join(
                os.getcwd(),
                "playback",
                str(speed),
            )

            if not os.path.isdir(
                chatdir
            ):

                os.makedirs(
                    chatdir
            )

            out = os.path.join(
                chatdir,
                base,
            )

            if not os.path.isfile(
                out
            ):

                if str(speed) == "0.5":
                    vs = 2.0

                elif str(speed) == "0.75":
                    vs = 1.35

                elif str(speed) == "1.5":
                    vs = 0.68

                elif str(speed) == "2.0":
                    vs = 0.5

                else:
                    vs = 1.0

                proc = (
                    await asyncio.create_subprocess_shell(
                        cmd=(
                            "ffmpeg "
                            "-i "
                            f'"{file_path}" '
                            "-filter:v "
                            f"setpts={vs}*PTS "
                            "-filter:a "
                            f"atempo={speed} "
                            f'"{out}"'
                        ),
                        stdin=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE,
                    )
                )

                await proc.communicate()

        else:

            out = file_path

        dur = await loop.run_in_executor(
            None,
            check_duration,
            out,
        )

        dur = int(dur)

        played, con_seconds = speed_converter(
            playing[0]["played"],
            speed,
        )

        duration = seconds_to_min(
            dur
        )

        stream = (

            MediaStream(
                out,
                audio_parameters=AudioQuality.HIGH,
                video_parameters=VideoQuality.SD_480p,
                ffmpeg_parameters=(
                    f"-ss {played} -to {duration}"
                ),
            )

            if playing[0]["streamtype"] == "video"

            else MediaStream(
                out,
                audio_parameters=AudioQuality.HIGH,
                ffmpeg_parameters=(
                    f"-ss {played} -to {duration}"
                ),
                video_flags=MediaStream.IGNORE,
            )
        )

        if str(
            db[chat_id][0]["file"]
        ) == str(file_path):

            await assistant.change_stream(
                chat_id,
                stream,
            )

        else:

            raise AssistantErr(
                "Umm"
            )

        if str(
            db[chat_id][0]["file"]
        ) == str(file_path):

            exis = (
                playing[0]
            ).get(
                "old_dur"
            )

            if not exis:

                db[chat_id][0][
                    "old_dur"
                ] = db[chat_id][0][
                    "dur"
                ]

                db[chat_id][0][
                    "old_second"
                ] = db[chat_id][0][
                    "seconds"
                ]

            db[chat_id][0][
                "played"
            ] = con_seconds

            db[chat_id][0][
                "dur"
            ] = duration

            db[chat_id][0][
                "seconds"
            ] = dur

            db[chat_id][0][
                "speed_path"
            ] = out

            db[chat_id][0][
                "speed"
            ] = speed

    # ========================================================
    # FORCE STOP
    # ========================================================

    async def force_stop_stream(
        self,
        chat_id: int,
    ):

        assistant = await group_assistant(
            self,
            chat_id,
        )

        try:

            check = db.get(
                chat_id
            )

            check.pop(
                0
            )

        except Exception:
            pass

        await self._stop_vc_monitor(
            chat_id
        )

        await remove_active_video_chat(
            chat_id
        )

        await remove_active_chat(
            chat_id
        )

        try:

            await assistant.leave_group_call(
                chat_id
            )

        except Exception:

            pass

    # ========================================================
    # SKIP
    # ========================================================

    async def skip_stream(
        self,
        chat_id: int,
        link: str,
        video: Union[bool, str] = None,
        image: Union[bool, str] = None,
    ):

        assistant = await group_assistant(
            self,
            chat_id,
        )

        if video:

            stream = MediaStream(
                link,
                audio_parameters=AudioQuality.HIGH,
                video_parameters=VideoQuality.SD_480p,
            )

        else:

            stream = MediaStream(
                link,
                audio_parameters=AudioQuality.HIGH,
                video_flags=MediaStream.IGNORE,
            )

        await assistant.change_stream(
            chat_id,
            stream,
        )

    # ========================================================
    # SEEK
    # ========================================================

    async def seek_stream(
        self,
        chat_id,
        file_path,
        to_seek,
        duration,
        mode,
    ):

        assistant = await group_assistant(
            self,
            chat_id,
        )

        stream = (

            MediaStream(
                file_path,
                audio_parameters=AudioQuality.HIGH,
                video_parameters=VideoQuality.SD_480p,
                ffmpeg_parameters=(
                    f"-ss {to_seek} -to {duration}"
                ),
            )

            if mode == "video"

            else MediaStream(
                file_path,
                audio_parameters=AudioQuality.HIGH,
                ffmpeg_parameters=(
                    f"-ss {to_seek} -to {duration}"
                ),
                video_flags=MediaStream.IGNORE,
            )
        )

        await assistant.change_stream(
            chat_id,
            stream,
        )

    # ========================================================
    # STREAM CALL
    # ========================================================

    async def stream_call(
        self,
        link,
    ):

        assistant = await group_assistant(
            self,
            config.LOGGER_ID,
        )

        await assistant.join_group_call(
            config.LOGGER_ID,
            MediaStream(link),
        )

        await asyncio.sleep(
            0.2
        )

        await assistant.leave_group_call(
            config.LOGGER_ID
        )

    # ========================================================
    # JOIN CALL
    # ========================================================

    async def join_call(
        self,
        chat_id: int,
        original_chat_id: int,
        link,
        video: Union[bool, str] = None,
        image: Union[bool, str] = None,
    ):

        assistant = await group_assistant(
            self,
            chat_id,
        )

        language = await get_lang(
            chat_id
        )

        _ = get_string(
            language
        )

        # ----------------------------------------------------
        # VIDEO STREAM
        # ----------------------------------------------------

        if video:

            stream = MediaStream(
                link,
                audio_parameters=AudioQuality.HIGH,
                video_parameters=VideoQuality.SD_480p,
            )

        # ----------------------------------------------------
        # AUDIO STREAM
        # ----------------------------------------------------

        else:

            stream = MediaStream(
                link,
                audio_parameters=AudioQuality.HIGH,
                video_flags=MediaStream.IGNORE,
            )

        # ----------------------------------------------------
        # JOIN GROUP CALL
        # ----------------------------------------------------

        try:

            await assistant.join_group_call(
                chat_id,
                stream,
            )

        except NoActiveGroupCall:

            raise AssistantErr(
                _["call_8"]
            )

        except AlreadyJoinedError:

            raise AssistantErr(
                _["call_9"]
            )

        except TelegramServerError:

            raise AssistantErr(
                _["call_10"]
            )

        except Exception as e:

            if "phone.CreateGroupCall" in str(e):

                raise AssistantErr(
                    _["call_8"]
                )

            LOGGER(__name__).error(
                "JOIN CALL FAILED | "
                "Chat: %s | %s",
                chat_id,
                e,
                exc_info=True,
            )

            raise

        # ----------------------------------------------------
        # MUSIC DATABASE
        # ----------------------------------------------------

        await add_active_chat(
            chat_id
        )

        await music_on(
            chat_id
        )

        if video:

            await add_active_video_chat(
                chat_id
            )

        # ----------------------------------------------------
        # START VC JOIN MONITOR
        # ----------------------------------------------------

        await self._start_vc_monitor(
            chat_id,
            assistant,
        )

        # ----------------------------------------------------
        # AUTO END
        # ----------------------------------------------------

        if await is_autoend():

            counter[chat_id] = {}

            try:

                users = (
                    await assistant.get_group_call_participants(
                        chat_id
                    )
                )

                if users is None:
                    users = []

                users = len(
                    users
                )

            except Exception as e:

                LOGGER(__name__).warning(
                    "AUTOEND PARTICIPANT CHECK FAILED | "
                    "Chat: %s | %s",
                    chat_id,
                    e,
                )

                users = 0

            if users == 1:

                autoend[chat_id] = (
                    datetime.now()
                    + timedelta(
                        minutes=1
                    )
                )

    # ========================================================
    # CHANGE STREAM
    # ========================================================

    async def change_stream(
        self,
        client,
        chat_id,
    ):

        check = db.get(
            chat_id
        )

        popped = None

        loop_count = await get_loop(
            chat_id
        )

        try:

            if loop_count == 0:

                popped = check.pop(
                    0
                )

            else:

                loop_count -= 1

                await set_loop(
                    chat_id,
                    loop_count,
                )

            await auto_clean(
                popped
            )

            if not check:

                await _clear_(
                    chat_id
                )

                await self._stop_vc_monitor(
                    chat_id
                )

                return await client.leave_group_call(
                    chat_id
                )

        except Exception:

            try:

                await _clear_(
                    chat_id
                )

                await self._stop_vc_monitor(
                    chat_id
                )

                return await client.leave_group_call(
                    chat_id
                )

            except Exception:

                return

        else:

            queued = check[0]["file"]

            language = await get_lang(
                chat_id
            )

            _ = get_string(
                language
            )

            title = (
                check[0]["title"]
            ).title()

            user = check[0]["by"]

            original_chat_id = (
                check[0]["chat_id"]
            )

            streamtype = (
                check[0]["streamtype"]
            )

            videoid = (
                check[0]["vidid"]
            )

            db[chat_id][0][
                "played"
            ] = 0

            if exis := check[0].get(
                "old_dur"
            ):

                db[chat_id][0][
                    "dur"
                ] = exis

                db[chat_id][0][
                    "seconds"
                ] = check[0][
                    "old_second"
                ]

                db[chat_id][0][
                    "speed_path"
                ] = None

                db[chat_id][0][
                    "speed"
                ] = 1.0

            video = (
                str(streamtype)
                == "video"
            )

            # =================================================
            # LIVE STREAM
            # =================================================

            if "live_" in queued:

                n, link = await YouTube.video(
                    videoid,
                    True,
                )

                if n == 0:

                    return await app.send_message(
                        original_chat_id,
                        text=_["call_6"],
                    )

                if video:

                    stream = MediaStream(
                        link,
                        audio_parameters=AudioQuality.HIGH,
                        video_parameters=VideoQuality.SD_480p,
                    )

                else:

                    stream = MediaStream(
                        link,
                        audio_parameters=AudioQuality.HIGH,
                        video_flags=MediaStream.IGNORE,
                    )

                try:

                    await client.change_stream(
                        chat_id,
                        stream,
                    )

                except Exception:

                    return await app.send_message(
                        original_chat_id,
                        text=_["call_6"],
                    )

                img = await get_thumb(
                    videoid
                )

                button = stream_markup2(
                    _,
                    chat_id,
                )

                run = await app.send_photo(
                    chat_id=original_chat_id,
                    photo=img,
                    caption=_["stream_1"].format(
                        f"https://t.me/{app.username}?start=info_{videoid}",
                        title[:23],
                        check[0]["dur"],
                        user,
                    ),
                    reply_markup=InlineKeyboardMarkup(
                        button
                    ),
                )

                db[chat_id][0][
                    "mystic"
                ] = run

                db[chat_id][0][
                    "markup"
                ] = "tg"

            # =================================================
            # VIDEO DOWNLOAD
            # =================================================

            elif "vid_" in queued:

                mystic = await app.send_message(
                    original_chat_id,
                    _["call_7"],
                )

                try:

                    file_path, direct = (
                        await YouTube.download(
                            videoid,
                            mystic,
                            videoid=True,
                            video=str(
                                streamtype
                            ) == "video",
                        )
                    )

                except Exception:

                    return await mystic.edit_text(
                        _["call_6"],
                        disable_web_page_preview=True,
                    )

                if video:

                    stream = MediaStream(
                        file_path,
                        audio_parameters=AudioQuality.HIGH,
                        video_parameters=VideoQuality.SD_480p,
                    )

                else:

                    stream = MediaStream(
                        file_path,
                        audio_parameters=AudioQuality.HIGH,
                        video_flags=MediaStream.IGNORE,
                    )

                try:

                    await client.change_stream(
                        chat_id,
                        stream,
                    )

                except Exception:

                    return await app.send_message(
                        original_chat_id,
                        text=_["call_6"],
                    )

                img = await get_thumb(
                    videoid
                )

                button = stream_markup(
                    _,
                    videoid,
                    chat_id,
                )

                try:

                    await mystic.delete()

                except Exception:
                    pass

                run = await app.send_photo(
                    chat_id=original_chat_id,
                    photo=img,
                    caption=_["stream_1"].format(
                        f"https://t.me/{app.username}?start=info_{videoid}",
                        title[:23],
                        check[0]["dur"],
                        user,
                    ),
                    reply_markup=InlineKeyboardMarkup(
                        button
                    ),
                )

                db[chat_id][0][
                    "mystic"
                ] = run

                db[chat_id][0][
                    "markup"
                ] = "stream"

            # =================================================
            # INDEX STREAM
            # =================================================

            elif "index_" in queued:

                stream = (

                    MediaStream(
                        videoid,
                        audio_parameters=AudioQuality.HIGH,
                        video_parameters=VideoQuality.SD_480p,
                    )

                    if str(streamtype) == "video"

                    else MediaStream(
                        videoid,
                        audio_parameters=AudioQuality.HIGH,
                        video_flags=MediaStream.IGNORE,
                    )
                )

                try:

                    await client.change_stream(
                        chat_id,
                        stream,
                    )

                except Exception:

                    return await app.send_message(
                        original_chat_id,
                        text=_["call_6"],
                    )

                button = stream_markup2(
                    _,
                    chat_id,
                )

                run = await app.send_photo(
                    chat_id=original_chat_id,
                    photo=config.STREAM_IMG_URL,
                    caption=_["stream_2"].format(
                        user
                    ),
                    reply_markup=InlineKeyboardMarkup(
                        button
                    ),
                )

                db[chat_id][0][
                    "mystic"
                ] = run

                db[chat_id][0][
                    "markup"
                ] = "tg"

            # =================================================
            # TELEGRAM / SOUNDCLOUD / OTHER
            # =================================================

            else:

                if video:

                    stream = MediaStream(
                        queued,
                        audio_parameters=AudioQuality.HIGH,
                        video_parameters=VideoQuality.SD_480p,
                    )

                else:

                    stream = MediaStream(
                        queued,
                        audio_parameters=AudioQuality.HIGH,
                        video_flags=MediaStream.IGNORE,
                    )

                try:

                    await client.change_stream(
                        chat_id,
                        stream,
                    )

                except Exception:

                    return await app.send_message(
                        original_chat_id,
                        text=_["call_6"],
                    )

                # ------------------------------------------------
                # TELEGRAM
                # ------------------------------------------------

                if videoid == "telegram":

                    button = stream_markup2(
                        _,
                        chat_id,
                    )

                    run = await app.send_photo(
                        chat_id=original_chat_id,
                        photo=(
                            config.TELEGRAM_AUDIO_URL
                            if str(streamtype) == "audio"
                            else config.TELEGRAM_VIDEO_URL
                        ),
                        caption=_["stream_1"].format(
                            config.SUPPORT_CHAT,
                            title[:23],
                            check[0]["dur"],
                            user,
                        ),
                        reply_markup=InlineKeyboardMarkup(
                            button
                        ),
                    )

                    db[chat_id][0][
                        "mystic"
                    ] = run

                    db[chat_id][0][
                        "markup"
                    ] = "tg"

                # ------------------------------------------------
                # SOUNDCLOUD
                # ------------------------------------------------

                elif videoid == "soundcloud":

                    button = stream_markup2(
                        _,
                        chat_id,
                    )

                    run = await app.send_photo(
                        chat_id=original_chat_id,
                        photo=config.SOUNDCLOUD_IMG_URL,
                        caption=_["stream_1"].format(
                            config.SUPPORT_CHAT,
                            title[:23],
                            check[0]["dur"],
                            user,
                        ),
                        reply_markup=InlineKeyboardMarkup(
                            button
                        ),
                    )

                    db[chat_id][0][
                        "mystic"
                    ] = run

                    db[chat_id][0][
                        "markup"
                    ] = "tg"

                # ------------------------------------------------
                # OTHER SOURCE
                # ------------------------------------------------

                else:

                    img = await get_thumb(
                        videoid
                    )

                    button = stream_markup(
                        _,
                        videoid,
                        chat_id,
                    )

                    run = await app.send_photo(
                        chat_id=original_chat_id,
                        photo=img,
                        caption=_["stream_1"].format(
                            f"https://t.me/{app.username}?start=info_{videoid}",
                            title[:23],
                            check[0]["dur"],
                            user,
                        ),
                        reply_markup=InlineKeyboardMarkup(
                            button
                        ),
                    )

                    db[chat_id][0][
                        "mystic"
                    ] = run

                    db[chat_id][0][
                        "markup"
                    ] = "stream"

    # ========================================================
    # PING
    # ========================================================

    async def ping(
        self,
    ):

        pings = []

        if config.STRING1:

            pings.append(
                await self.one.ping
            )

        if config.STRING2:

            pings.append(
                await self.two.ping
            )

        if config.STRING3:

            pings.append(
                await self.three.ping
            )

        if config.STRING4:

            pings.append(
                await self.four.ping
            )

        if config.STRING5:

            pings.append(
                await self.five.ping
            )

        if not pings:

            return "0"

        return str(
            round(
                sum(pings) / len(pings),
                3,
            )
        )

    # ========================================================
    # START
    # ========================================================

    async def start(
        self,
    ):

        LOGGER(__name__).info(
            "Starting PyTgCalls Client...\n"
        )

        if config.STRING1:

            await self.one.start()

        if config.STRING2:

            await self.two.start()

        if config.STRING3:

            await self.three.start()

        if config.STRING4:

            await self.four.start()

        if config.STRING5:

            await self.five.start()

        LOGGER(__name__).info(
            "PyTgCalls Clients Started Successfully"
        )

    # ========================================================
    # DECORATORS
    # ========================================================

    async def decorators(
        self,
    ):

        @self.one.on_kicked()
        @self.two.on_kicked()
        @self.three.on_kicked()
        @self.four.on_kicked()
        @self.five.on_kicked()

        @self.one.on_closed_voice_chat()
        @self.two.on_closed_voice_chat()
        @self.three.on_closed_voice_chat()
        @self.four.on_closed_voice_chat()
        @self.five.on_closed_voice_chat()

        @self.one.on_left()
        @self.two.on_left()
        @self.three.on_left()
        @self.four.on_left()
        @self.five.on_left()

        async def stream_services_handler(
            _,
            chat_id: int,
        ):

            await self.stop_stream(
                chat_id
            )

        @self.one.on_stream_end()
        @self.two.on_stream_end()
        @self.three.on_stream_end()
        @self.four.on_stream_end()
        @self.five.on_stream_end()

        async def stream_end_handler(
            client,
            update: Update,
        ):

            if not isinstance(
                update,
                StreamAudioEnded,
            ):

                return

            await self.change_stream(
                client,
                update.chat_id,
            )


# ============================================================
# HOTTY INSTANCE
# ============================================================

Hotty = Call()
