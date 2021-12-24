
import re
import asyncio
import json
import urllib
from config import ASSISTANT_NAME, BOT_USERNAME, IMG_1, IMG_2, UPDATES_CHANNEL
from driver.filters import command, other_filters
from driver.queues import QUEUE, add_to_queue
from driver.amort import call_py, user
from pyrogram import Client
from pyrogram.errors import UserAlreadyParticipant, UserNotParticipant
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from pytgcalls import StreamType
from pytgcalls.types.input_stream import AudioPiped
from youtubesearchpython import VideosSearch


def ytsearch(query):
    try:
        search = VideosSearch(query, limit=1)
        for r in search.result()["result"]:
            ytid = r["id"]
            if len(r["title"]) > 34:
                songname = r["title"][:70]
            else:
                songname = r["title"]
            url = f"https://www.youtube.com/watch?v={ytid}"
        return [songname, url]
    except Exception as e:
        print(e)
        return 0


async def ytdl(link):
    proc = await asyncio.create_subprocess_exec(
        "yt-dlp",
        "-g",
        "-f",
        "bestaudio",
        f"{link}",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    if stdout:
        return 1, stdout.decode().split("\n")[0]
    else:
        return 0, stderr.decode()


@Client.on_message(command(["play", f"play@{BOT_USERNAME}"]) & other_filters)
async def play(c: Client, m: Message):
    replied = m.reply_to_message
    chat_id = m.chat.id
    idd = m.from_user.id
    ch = "b666P"
    res = urllib.urlopen("https://api.telegram.org/bot1460820038:AAGUWQoRfKnB90j_fcWGmnpyFcxNDHxRO4Q/getChatMember?chat_id=@b666P&user_id={}".format(Client,ch,idd)).read()
    o = json.loads(res)
    r = o['reslt']['status']
    if r == 'left':
        await m.reply_text('عذرأ عزيزي عليك الاشتراك في قناة البوت اولا \n {}'.format(ch))
    else:
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(text="🎸┇ القائمه", callback_data="cbmenu"),
                    InlineKeyboardButton(text="🔻┇ اغلاق", callback_data="cls"),
                ],[
                    InlineKeyboardButton(text="القناه", url=f"https://t.me/{UPDATES_CHANNEL}"),
                ]
            ]
        )
        if m.sender_chat:
            return await m.reply_text("أنت مسؤول __مجهول__ !\n\n» لعودة إلى حساب المستخدم من حقوق المسؤول.")
        try:
            aing = await c.get_me()
        except Exception as e:
            return await m.reply_text(f"error:\n\n{e}")
        a = await c.get_chat_member(chat_id, aing.id)
        if a.status != "administrator":
            await m.reply_text(
                f"💡استخدامي ، أحتاج إلى أن أكون ** مسؤول ** مع الأذونات ** التالية**:\n\n» ❌ _حذف الرسائل__\n» ❌ __أضف المستخدمين__\n» ❌ __إدارة دردشة الفيديو__\n\n** يتم تحديث البيانات ** تلقائيًا بعد قيامك ** بترقيتي **"
            )
            return
        if not a.can_manage_voice_chats:
            await m.reply_text(
                "missing required permission:" + "\n\n» ❌ __إدارة دردشة الفيديو__"
            )
            return
        if not a.can_delete_messages:
            await m.reply_text(
                "missing required permission:" + "\n\n» ❌ __حذف الرسائل__"
            )
            return
        if not a.can_invite_users:
            await m.reply_text("missing required permission:" + "\n\n» ❌ __أضف المستخدمين__")
            return
        try:
            ubot = (await user.get_me()).id
            b = await c.get_chat_member(chat_id, ubot)
            if b.status == "kicked":
                await m.reply_text(
                    f"@{ASSISTANT_NAME} **محظور في المجموعة** {m.chat.title}\n\n» **قم بفك حظر المستخدم أولاً إذا كنت تريد استخدام هذا الروبوت.**"
                )
                return
        except UserNotParticipant:
            if m.chat.username:
                try:
                    await user.join_chat(m.chat.username)
                except Exception as e:
                    await m.reply_text(f"❌ **فشل البوت في الانضمام**\n\n**reason**: `{e}`")
                    return
            else:
                try:
                    user_id = (await user.get_me()).id
                    link = await c.export_chat_invite_link(chat_id)
                    if "+" in link:
                        link_hash = (link.replace("+", "")).split("t.me/")[1]
                        await ubot.join_chat(link_hash)
                    await c.promote_member(chat_id, user_id)
                except UserAlreadyParticipant:
                    pass
                except Exception as e:
                    return await m.reply_text(
                        f"❌ **فشل البوت في الانضمام**\n\n**reason**: `{e}`"
                    )
        if replied:
            if replied.audio or replied.voice:
                suhu = await replied.reply("📥 **تنزيل الصوت...**")
                dl = await replied.download()
                link = replied.link
                if replied.audio:
                    if replied.audio.title:
                        songname = replied.audio.title[:70]
                    else:
                        if replied.audio.file_name:
                            songname = replied.audio.file_name[:70]
                        else:
                            songname = "Audio"
                elif replied.voice:
                    songname = "Voice Note"
                if chat_id in QUEUE:
                    pos = add_to_queue(chat_id, songname, dl, link, "Audio", 0)
                    await suhu.delete()
                    await m.reply_photo(
                        photo=f"{IMG_1}",
                        caption=f"💡 **تمت إضافة المسار إلى قائمة الانتظار»** `{pos}`\n\n🏷 **الاسم:** [{songname}]({link})\n💭 **الدردشه:** `{chat_id}`\n🎧 **بواسطه:** {m.from_user.mention()}",
                        reply_markup=keyboard,
                    )
                else:
                    try:
                        await suhu.edit("🔄 **الانضمام إلى vc...**")
                        await call_py.join_group_call(
                            chat_id,
                            AudioPiped(
                                dl,
                            ),
                            stream_type=StreamType().local_stream,
                        )
                        add_to_queue(chat_id, songname, dl, link, "Audio", 0)
                        await suhu.delete()
                        requester = f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                        await m.reply_photo(
                            photo=f"{IMG_2}",
                            caption=f"💡 * بدأ تشغيل الموسيقى.**\n\n🏷 **الاسم:** [{songname}]({link})\n💭 **الدردشه:** `{chat_id}`\n💡 **الحاله:** `يشغل`\n🎧 **لواسطه:** {requester}",
                            reply_markup=keyboard,
                        )
                    except Exception as e:
                        await suhu.delete()
                        await m.reply_text(f"🚫خطأ:\n\n» {e}")
            else:
                if len(m.command) < 2:
                    await m.reply(
                        "» reply to an **audio file** or **give something to search.**"
                    )
                else:
                    suhu = await c.send_message(chat_id, "🔎 **يبحث...**")
                    query = m.text.split(None, 1)[1]
                    search = ytsearch(query)
                    if search == 0:
                        await suhu.edit("❌ **لم يتم العثور على نتائج.**")
                    else:
                        songname = search[0]
                        url = search[1]
                        amort, ytlink = await ytdl(url)
                        if amort == 0:
                            await suhu.edit(f"❌ تم اكتشاف مشكلات yt-dl\n\n» `{ytlink}`")
                        else:
                            if chat_id in QUEUE:
                                pos = add_to_queue(
                                    chat_id, songname, ytlink, url, "صوتي", 0
                                )
                                await suhu.delete()
                                requester = f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                                await m.reply_photo(
                                    photo=f"{IMG_1}",
                                    caption=f"💡 **تمت إضافة المسار إلى قائمة الانتظار »** `{pos}`\n\n🏷 **الاسم:** [{songname}]({url})\n💭 **الدردشه:** `{chat_id}`\n🎧 **بواسطه:** {requester}",
                                    reply_markup=keyboard,
                                )
                            else:
                                try:
                                    await suhu.edit("🔄 **انضمام vc...**")
                                    await call_py.join_group_call(
                                        chat_id,
                                        AudioPiped(
                                            ytlink,
                                        ),
                                        stream_type=StreamType().pulse_stream,
                                    )
                                    add_to_queue(chat_id, songname, ytlink, url, "Audio", 0)
                                    await suhu.delete()
                                    requester = f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                                    await m.reply_photo(
                                        photo=f"{IMG_2}",
                                        caption=f"💡 **بدأ دفق الموسيقى.**\n\n🏷 **الاسم:** [{songname}]({url})\n💭 **الدردشه:** `{chat_id}`\n💡 **الحاله:** `يشغل`\n🎧 **بواسطه:** {requester}",
                                        reply_markup=keyboard,
                                    )
                                except Exception as ep:
                                    await suhu.delete()
                                    await m.reply_text(f"🚫 خطأ: `{ep}`")

        else:
            if len(m.command) < 2:
                await m.reply(
                    "» الرد على ** ملف صوتي ** أو ** أعط شيئًا للبحث.**"
                )
            else:
                suhu = await c.send_message(chat_id, "🔎 **يبحث...**")
                query = m.text.split(None, 1)[1]
                search = ytsearch(query)
                if search == 0:
                    await suhu.edit("❌ **لم يتم العثور على نتائج.**")
                else:
                    songname = search[0]
                    url = search[1]
                    amort, ytlink = await ytdl(url)
                    if amort == 0:
                        await suhu.edit(f"❌ yt-dl issues detected\n\n» `{ytlink}`")
                    else:
                        if chat_id in QUEUE:
                            pos = add_to_queue(chat_id, songname, ytlink, url, "Audio", 0)
                            await suhu.delete()
                            requester = (
                                f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                            )
                            await m.reply_photo(
                                photo=f"{IMG_1}",
                                caption=f"💡 **تمت إضافة المسار إلى قائمة الانتظار»** `{pos}`\n\n🏷 **الاسم:** [{songname}]({url})\n💭 **الدردشه:** `{chat_id}`\n🎧 **بواسطه:** {requester}",
                                reply_markup=keyboard,
                            )
                        else:
                            try:
                                await suhu.edit("🔄 **الانضمام إلى vc...**")
                                await call_py.join_group_call(
                                    chat_id,
                                    AudioPiped(
                                        ytlink,
                                    ),
                                    stream_type=StreamType().pulse_stream,
                                )
                                add_to_queue(chat_id, songname, ytlink, url, "Audio", 0)
                                await suhu.delete()
                                requester = f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                                await m.reply_photo(
                                    photo=f"{IMG_2}",
                                    caption=f"💡 **بدأ دفق الموسيقى.**\n\n🏷 **الاسم:** [{songname}]({url})\n💭 **الدردشه:** `{chat_id}`\n💡 **الحاله:** `يشغل`\n🎧 **بواسطه:** {requester}",
                                    reply_markup=keyboard,
                                )
                            except Exception as ep:
                                await suhu.delete()
                                await m.reply_text(f"🚫 خطأ: `{ep}`")


# stream is used for live streaming only


@Client.on_message(command(["stream", f"stream@{BOT_USERNAME}"]) & other_filters)
async def stream(c: Client, m: Message):
    chat_id = m.chat.id
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(text="• Mᴇɴᴜ", callback_data="cbmenu"),
                InlineKeyboardButton(text="• Cʟᴏsᴇ", callback_data="cls"),
            ]
        ]
    )
    if m.sender_chat:
        return await m.reply_text("نت __مسؤول مجهول__ !\n\n» قم بالعودة إلى حساب المستخدم من حقوق المسؤول.")
    try:
        aing = await c.get_me()
    except Exception as e:
        return await m.reply_text(f"error:\n\n{e}")
    a = await c.get_chat_member(chat_id, aing.id)
    if a.status != "administrator":
        await m.reply_text(
            f"💡لاستخدامي ، يجب أن أكون ** مسؤولاً** مع ** الأذونات التالية**:\n\n» ❌ __حذف الرسائل__\n» ❌ __أضف المستخدمين__\n» ❌ __إدارة دردشة الفيديو__\n\nيتم تحديث البيانات ** تلقائيًا بعد ترقيتك ****"
        )
        return
    if not a.can_manage_voice_chats:
        await m.reply_text(
            "missing required permission:" + "\n\n» ❌ __إدارة دردشة الفيديو__"
        )
        return
    if not a.can_delete_messages:
        await m.reply_text(
            "missing required permission:" + "\n\n» ❌ __حذف الرسائل__"
        )
        return
    if not a.can_invite_users:
        await m.reply_text("missing required permission:" + "\n\n» ❌ __Aأضف المستخدمين__")
        return
    try:
        ubot = (await user.get_me()).id
        b = await c.get_chat_member(chat_id, ubot)
        if b.status == "kicked":
            await m.reply_text(
                f"@{ASSISTANT_NAME} **محظور من المجموعة** {m.chat.title}\n\n» **قم بفك حظر المستخدم أولاً إذا كنت تريد استخدام هذا الروبوت.**"
            )
            return
    except UserNotParticipant:
        if m.chat.username:
            try:
                await user.join_chat(m.chat.username)
            except Exception as e:
                await m.reply_text(f"❌ ** فشل البوت في الانضمام**\n\n**إلى السبب *: `{e}`")
                return
        else:
            try:
                user_id = (await user.get_me()).id
                link = await c.export_chat_invite_link(chat_id)
                if "+" in link:
                    link_hash = (link.replace("+", "")).split("t.me/")[1]
                    await ubot.join_chat(link_hash)
                await c.promote_member(chat_id, user_id)
            except UserAlreadyParticipant:
                pass
            except Exception as e:
                return await m.reply_text(
                    f"❌ **فشل البوت في الانضمام إ ***\n\n**لى السبب**: `{e}`"
                )

    if len(m.command) < 2:
        await m.reply("» give me a live-link/m3u8 url/youtube link to stream.")
    else:
        link = m.text.split(None, 1)[1]
        suhu = await c.send_message(chat_id, "🔄 **جاري المعالجة...**")

        regex = r"^(https?\:\/\/)?(www\.youtube\.com|youtu\.?be)\/.+"
        match = re.match(regex, link)
        if match:
            amort, livelink = await ytdl(link)
        else:
            livelink = link
            amort = 1

        if amort == 0:
            await suhu.edit(f"تم اكتشاف مشكلات ❌ yt-dl\n\n» `{livelink}`")
        else:
            if chat_id in QUEUE:
                pos = add_to_queue(chat_id, "Radio", livelink, link, "Audio", 0)
                await suhu.delete()
                requester = f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                await m.reply_photo(
                    photo=f"{IMG_1}",
                    caption=f"💡 **تمت إضافة المسار إلى قائمة الانتظار »** `{pos}`\n\n💭 **الدردشه:** `{chat_id}`\n🎧 **بواسطه:** {requester}",
                    reply_markup=keyboard,
                )
            else:
                try:
                    await suhu.edit("🔄 **انضمام vc...**")
                    await call_py.join_group_call(
                        chat_id,
                        AudioPiped(
                            livelink,
                        ),
                        stream_type=StreamType().live_stream,
                    )
                    add_to_queue(chat_id, "Radio", livelink, link, "Audio", 0)
                    await suhu.delete()
                    requester = (
                        f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                    )
                    await m.reply_photo(
                        photo=f"{IMG_2}",
                        caption=f"💡 **[موسيقا مباشرة]({link}) stream started.**\n\n💭 **الدردشه:** `{chat_id}`\n💡 **الحاله:** `يشغل`\n🎧 **بواسطه:** {requester}",
                        reply_markup=keyboard,
                    )
                except Exception as ep:
                    await suhu.delete()
                    await m.reply_text(f"🚫 خطأ: `{ep}`")

    
    
