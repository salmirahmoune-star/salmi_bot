from telethon import TelegramClient, events
import asyncio, os, random

api_id = 36424796
api_hash = 'f200b29b67940b98fdf44c4ca7b4c08e'

client1 = TelegramClient('session_1', api_id, api_hash)
client2 = TelegramClient('session_2', api_id, api_hash)
client3 = TelegramClient('session_3', api_id, api_hash)

def load_words():
    if os.path.exists('words.txt'):
        with open('words.txt', 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    return ["مرحباً"]

# نظام قوائم عشوائية منظمة لكل شات لحفظ الترتيب ومنع التكرار المتشابه
shuffled_queues = {}

def get_next_random_line(chat_id):
    global shuffled_queues
    if chat_id not in shuffled_queues or not shuffled_queues[chat_id]:
        words = load_words()
        random.shuffle(words)  # خلط الـ 1000 سطر عشوائياً وبشكل منظم
        shuffled_queues[chat_id] = words
    
    return shuffled_queues[chat_id].pop(0)

def generate_spam_text(spam_chars_dict, chat_id):
    chosen_line = get_next_random_line(chat_id)
    
    separator = spam_chars_dict.get(chat_id, None)
    if separator:
        return chosen_line.replace(" ", f" {separator} ")
    
    return chosen_line

def setup_client_handlers(client, owner_id_container):
    active_spams = {}          
    auto_respond_targets = {}  
    muted_targets = set()      
    spam_speeds = {}           
    spam_chars = {}            

    @client.on(events.NewMessage(pattern=r'^\.(ابدا|يلا|س)$'))
    async def start_spam(event):
        if event.sender_id != owner_id_container.get('id'):
            return
        chat_id = event.chat_id
        if active_spams.get(chat_id, False):
            await event.delete()
            return

        reply_to = await event.get_reply_message() if event.is_reply else None
        reply_to_id = reply_to.id if reply_to else None

        await event.delete()
        active_spams[chat_id] = True
        
        if chat_id not in spam_speeds:
            spam_speeds[chat_id] = 1.5

        try:
            while active_spams.get(chat_id, False):
                line_text = generate_spam_text(spam_chars, chat_id)
                if reply_to_id:
                    await client.send_message(chat_id, line_text, reply_to=reply_to_id)
                else:
                    await client.send_message(chat_id, line_text)
                await asyncio.sleep(spam_speeds[chat_id])
        except:
            pass

    @client.on(events.NewMessage(pattern=r'^\.ايقاف$'))
    async def stop_spam(event):
        if event.sender_id != owner_id_container.get('id'):
            return
        await event.delete()
        chat_id = event.chat_id
        if active_spams.get(chat_id, False):
            active_spams[chat_id] = False

    @client.on(events.NewMessage(pattern=r'^\.سرعة\s+(.+)'))
    async def set_speed(event):
        if event.sender_id != owner_id_container.get('id'):
            return
        chat_id = event.chat_id
        try:
            speed_val = float(event.pattern_match.group(1).strip())
            if 0.1 <= speed_val <= 10.0:
                spam_speeds[chat_id] = speed_val
        except:
            pass
        await event.delete()

    @client.on(events.NewMessage(pattern=r'^\.خط\s*(.*)'))
    async def set_custom_line(event):
        if event.sender_id != owner_id_container.get('id'):
            return
        chat_id = event.chat_id
        char = event.pattern_match.group(1).strip()
        if char:
            spam_chars[chat_id] = char
        else:
            spam_chars.pop(chat_id, None)
        await event.delete()

    @client.on(events.NewMessage(pattern=r'^\.س$'))
    async def start_auto_reply(event):
        if event.sender_id != owner_id_container.get('id') or not event.is_reply:
            await event.delete()
            return
        reply_to = await event.get_reply_message()
        chat_id = event.chat_id
        auto_respond_targets[chat_id] = reply_to.sender_id
        await event.delete()

    @client.on(events.NewMessage(pattern=r'^\.ايقاف رد$'))
    async def stop_auto_reply(event):
        if event.sender_id != owner_id_container.get('id'):
            return
        await event.delete()
        auto_respond_targets.pop(event.chat_id, None)

    @client.on(events.NewMessage(pattern=r'^\.كتم$'))
    async def start_mute(event):
        if event.sender_id != owner_id_container.get('id') or not event.is_reply:
            await event.delete()
            return
        reply_to = await event.get_reply_message()
        muted_targets.add(reply_to.sender_id)
        await event.delete()

    @client.on(events.NewMessage(pattern=r'^\.ايقاف كتم$'))
    async def stop_mute(event):
        if event.sender_id != owner_id_container.get('id') or not event.is_reply:
            await event.delete()
            return
        reply_to = await event.get_reply_message()
        muted_targets.discard(reply_to.sender_id)
        await event.delete()

    @client.on(events.NewMessage(incoming=True))
    async def monitor_messages(event):
        chat_id = event.chat_id
        sender_id = event.sender_id
        if sender_id == owner_id_container.get('id'):
            return
        if sender_id in muted_targets:
            try: await event.delete()
            except: pass
            return
        if chat_id in auto_respond_targets and sender_id == auto_respond_targets[chat_id]:
            try: await event.reply(generate_spam_text(spam_chars, chat_id))
            except: pass

owner1, owner2, owner3 = {}, {}, {}
setup_client_handlers(client1, owner1)
setup_client_handlers(client2, owner2)
setup_client_handlers(client3, owner3)

async def main():
    await client1.start()
    me1 = await client1.get_me()
    owner1['id'] = me1.id
    print(f"✅ الحساب الأول جاهز: {me1.first_name}")

    await client2.start()
    me2 = await client2.get_me()
    owner2['id'] = me2.id
    print(f"✅ الحساب الثاني جاهز: {me2.first_name}")

    await client3.start()
    me3 = await client3.get_me()
    owner3['id'] = me3.id
    print(f"✅ الحساب الثالث جاهز: {me3.first_name}")

    os.system('clear')
    print(f"\033[1;32m🔥 السورس يعمل بكامل ميزاته بنجاح للحسابات الثلاثة!\033[0m")
    await asyncio.gather(
        client1.run_until_disconnected(), 
        client2.run_until_disconnected(),
        client3.run_until_disconnected()
    )

if __name__ == '__main__':
    asyncio.run(main())

