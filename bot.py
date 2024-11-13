import os
from pyrogram import Client, filters
from pyrogram.types import Message
import asyncio
import re
import yt_dlp

api_id = '20944746'
api_hash = 'd169162c1bcf092a6773e685c62c3894'
app = Client("my_account1", api_id=api_id, api_hash=api_hash)
authorized_user_id = 7381921215  # استبدل بمعرف المستخدم المخوّل
download_path = r"C:\Users\majds\Downloads\New folder"

# Ensure the download path exists
if not os.path.exists(download_path):
    os.makedirs(download_path)

# قائمة المستخدمين المكتمين
muted_users = set()

# أمر .كرر
@app.on_message(filters.command("كرر", prefixes="."))
async def repeat(client: Client, message: Message):
    print("Received .كرر command")
    if message.from_user.id != authorized_user_id:
        return  # لا يرد على الرسائل إذا لم يكن المستخدم المخول
    try:
        await message.delete()
    except Exception as e:
        print(f"Error while deleting message: {e}")
    
    text = message.text
    try:
        parts = text.split(maxsplit=1)
        if len(parts) < 2:
            await message.reply("يرجى استخدام الصيغة الصحيحة: .كرر <النص> <العدد>")
            return
        text = parts[1].strip()
        match = re.search(r'(\d+)\s*$', text)
        if not match:
            await message.reply("يرجى إدخال عدد صحيح في نهاية الرسالة.")
            return
        count = int(match.group(1))
        word = text[:match.start()].strip()
        if count <= 0:
            await message.reply("العدد يجب أن يكون أكبر من 0.")
            return
        for _ in range(count):
            await message.reply_text(word)
            await asyncio.sleep(0.5)
    except ValueError:
        await message.reply_text("يرجى إدخال عدد صحيح للمرات.")

# أمر .حذف
@app.on_message(filters.regex(r"^\.حذف\s+\d+$"))
async def delete_messages(client: Client, message: Message):
    print("Received .حذف command")
    if message.from_user.id != authorized_user_id:
        return
    try:
        await message.delete()
    except Exception as e:
        print(f"Error while deleting message: {e}")
    
    parts = message.text.split()
    if len(parts) != 2:
        await message.reply("Usage: .حذف <number>")
        return
    try:
        num = int(parts[1])
    except ValueError:
        await message.reply("The number must be an integer.")
        return
    if num <= 0:
        await message.reply("The number must be greater than 0.")
        return
    async for msg in client.get_chat_history(message.chat.id, limit=num):
        try:
            await msg.delete()
        except Exception as e:
            await message.reply(f"Error: {e}")
            break
    await message.reply(f"حذفت آخر {num} رسائل بيبي ❤️.")

# أمر .حظر
@app.on_message(filters.command("حظر", prefixes=".") & filters.reply)
async def ban_user(client: Client, message: Message):
    print("Received .حظر command")
    if message.from_user.id != authorized_user_id:
        return
    try:
        await message.delete()
    except Exception as e:
        print(f"Error while deleting message: {e}")
    
    try:
        username = message.reply_to_message.from_user.username or "none"
        await client.block_user(message.reply_to_message.from_user.id)
        await message.reply_text(f"تم حظر المستخدم @{username} بنجاح.")
    except Exception as e:
        await message.reply_text(f"حدث خطأ أثناء محاولة حظر المستخدم: {e}")

# أمر .يوت لتحميل الأغاني
@app.on_message(filters.command("يوت", prefixes="."))
async def download_song(client: Client, message: Message):
    print("Received .يوت command")
    if message.from_user.id != authorized_user_id:
        print(f"Unauthorized user: {message.from_user.id}")
        return  # لا يرد على الرسائل إذا لم يكن المستخدم المخوّل
    try:
        await message.delete()
    except Exception as e:
        print(f"Error while deleting message: {e}")

    text = message.text
    parts = text.split(maxsplit=1)
    if len(parts) < 2:
        await message.reply("يرجى استخدام الصيغة الصحيحة: .يوت <اسم الأغنية>")
        return

    song_name = parts[1].strip()
    await message.reply("جارٍ البحث عن الأغنية...")

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'ffmpeg_location': r"C:\Users\majds\Downloads\yt-dlp\ffmpeg.exe",  # مسار ffmpeg
        'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),  # المسار حيث سيتم حفظ الملف
        'quiet': False,
        'encoding': 'utf-8',  # تأكد من استخدام الترميز الصحيح
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            search_query = f"ytsearch:{song_name}"
            info = ydl.extract_info(search_query, download=True)
            downloaded_file = ydl.prepare_filename(info)
            mp3_filename = downloaded_file.rsplit('.', 1)[0] + '.mp3'

            print(f"Downloaded file: {downloaded_file}")  # طباعة اسم الملف الذي تم تحميله
            print(f"Expected mp3 filename: {mp3_filename}")

            # التحقق من الملفات الموجودة في المسار
            files_in_directory = os.listdir(download_path)
            print(f"Files in download directory: {files_in_directory}")

            found_file = None
            for file in files_in_directory:
                print(f"Checking file: {file}")
                if file.endswith(".mp3") and song_name.split()[0] in file:
                    found_file = os.path.join(download_path, file)
                    break

            if found_file:
                print(f"Found file to upload: {found_file}")
                await message.reply_audio(audio=found_file)
                os.remove(found_file)  # حذف الملف بعد الإرسال
            else:
                await message.reply("لم يتم العثور على الأغنية.")
    except Exception as e:
        await message.reply(f"حدث خطأ أثناء محاولة تحميل الأغنية: {e}")
        print(f"Error: {e}")

# أمر .كتم
@app.on_message(filters.command("كتم", prefixes=".") & filters.reply)
async def mute_user(client: Client, message: Message):
    print("Received .كتم command")
    if message.from_user.id != authorized_user_id:
        return
    try:
        await message.delete()
    except Exception as e:
        print(f"Error while deleting message: {e}")
    
    user_id = message.reply_to_message.from_user.id
    muted_users.add(user_id)
    await message.reply_text(f"تم كتم المستخدم @{message.reply_to_message.from_user.username} بنجاح.")

# أمر .الغاء_كتم
@app.on_message(filters.command("الغاء_كتم", prefixes=".") & filters.reply)
async def unmute_user(client: Client, message: Message):
    print("Received .الغاء_كتم command")
    if message.from_user.id != authorized_user_id:
        return
    try:
        await message.delete()
    except Exception as e:
        print(f"Error while deleting message: {e}")
    
    user_id = message.reply_to_message.from_user.id
    muted_users.discard(user_id)
    await message.reply_text(f"تم إلغاء كتم المستخدم @{message.reply_to_message.from_user.username} بنجاح.")

# التحقق من المستخدمين المكتمين وحذف رسائلهم
@app.on_message(filters.text)
async def filter_muted_users(client: Client, message: Message):
    if message.from_user.id in muted_users:
        try:
            await message.delete()
        except Exception as e:
            print(f"Error while deleting muted message: {e}")

app.run()
