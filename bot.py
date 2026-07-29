#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram Bot for linettka_ph portfolio management.
Allows uploading photos directly from mobile Telegram into website portfolio
with automatic WebP optimization and category selection.
"""

import os
import sys
import time
import datetime
from PIL import Image
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Insert your Telegram Bot Token from @BotFather here or set BOT_TOKEN environment variable
BOT_TOKEN = os.getenv("BOT_TOKEN", "8917917475:AAH3NO3OOt4QF7nTTZWDCJgwTkaPnS2PN_o").strip()

bot = telebot.TeleBot(BOT_TOKEN)

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_HTML = os.path.join(BASE_DIR, "index.html")
TEMP_DIR = os.path.join(BASE_DIR, "images", "temp_bot")
os.makedirs(TEMP_DIR, exist_ok=True)

# Temporary memory for pending photo uploads by user_id
pending_photos = {}

CATEGORIES = {
    "studio": {"name": "Студія 📷", "folder": "studio", "alt": "Студійна зйомка"},
    "outdoor": {"name": "Заобрій 🌿", "folder": "outdoor", "alt": "Заобрій"},
    "couple": {"name": "Пари 👩‍❤️‍👨", "folder": "couple", "alt": "Фото пари"},
    "event": {"name": "Події 🕊️", "folder": "event", "alt": "Подія"}
}

def get_category_keyboard(photo_id):
    markup = InlineKeyboardMarkup(row_width=2)
    buttons = [
        InlineKeyboardButton(cat["name"], callback_data=f"cat:{cat_key}:{photo_id}")
        for cat_key, cat in CATEGORIES.items()
    ]
    markup.add(*buttons)
    return markup

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "✨ **Вітаю у боті управління портфоліо linettka!** ✨\n\n"
        "Надішліть мені будь-яку фотографію (як фото або як документ без втрати якості).\n"
        "Я автоматично:\n"
        "1. Запитаю, у яку категорію її додати (*Студія*, *Заобрій*, *Пари*, *Події*)\n"
        "2. Оптимізую її в ультра-швидкий формат `.webp`\n"
        "3. Додам її на сайт у портфоліо!"
    )
    bot.reply_to(message, welcome_text, parse_mode="Markdown")

@bot.message_handler(content_types=['photo', 'document'])
def handle_photo(message):
    try:
        file_id = None
        if message.content_type == 'photo':
            file_id = message.photo[-1].file_id
        elif message.content_type == 'document':
            if message.document.mime_type and message.document.mime_type.startswith('image/'):
                file_id = message.document.file_id
            else:
                bot.reply_to(message, "⚠️ Будь ласка, надішліть файл зображення (.jpg, .png, .jpeg, .webp).")
                return

        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        temp_filename = f"temp_{int(time.time())}_{message.message_id}.jpg"
        temp_filepath = os.path.join(TEMP_DIR, temp_filename)

        with open(temp_filepath, 'wb') as new_file:
            new_file.write(downloaded_file)

        temp_id = f"{message.chat.id}_{message.message_id}"
        pending_photos[temp_id] = temp_filepath

        msg = bot.reply_to(
            message,
            "📸 **Отримано нове фото!**\n\nОберіть категорію, куди додати це фото у портфоліо:",
            reply_markup=get_category_keyboard(temp_id),
            parse_mode="Markdown"
        )
    except Exception as e:
        bot.reply_to(message, f"❌ Помилка під час завантаження фото: {str(e)}")

@bot.callback_query_handler(func=lambda call: call.data.startswith('cat:'))
def process_category_choice(call):
    try:
        parts = call.data.split(':')
        cat_key = parts[1]
        temp_id = parts[2]

        if temp_id not in pending_photos:
            bot.answer_callback_query(call.id, "⚠️ Фото вже оброблено або сесія застаріла.")
            return

        temp_filepath = pending_photos.pop(temp_id)
        cat_info = CATEGORIES[cat_key]
        folder_name = cat_info["folder"]

        timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename_webp = f"img_bot_{timestamp_str}.webp"

        opt_dir = os.path.join(BASE_DIR, "images", "optimized", folder_name)
        thumb_dir = os.path.join(BASE_DIR, "images", "thumbs", folder_name)
        os.makedirs(opt_dir, exist_ok=True)
        os.makedirs(thumb_dir, exist_ok=True)

        opt_filepath = os.path.join(opt_dir, filename_webp)
        thumb_filepath = os.path.join(thumb_dir, filename_webp)

        img = Image.open(temp_filepath).convert('RGB')

        # Save ultra-sharp optimized (max 2560px, quality 95)
        img_opt = img.copy()
        img_opt.thumbnail((2560, 2560), Image.LANCZOS)
        img_opt.save(opt_filepath, 'WEBP', quality=95, optimize=True)

        # Save Retina-sharp thumbnail (max 1200px, quality 92)
        img_thumb = img.copy()
        img_thumb.thumbnail((1200, 1200), Image.LANCZOS)
        img_thumb.save(thumb_filepath, 'WEBP', quality=92, optimize=True)

        if os.path.exists(temp_filepath):
            os.remove(temp_filepath)

        rel_thumb = f"images/thumbs/{folder_name}/{filename_webp}"
        rel_opt = f"images/optimized/{folder_name}/{filename_webp}"

        insert_photo_to_html(cat_key, rel_thumb, rel_opt, cat_info["alt"])

        size_kb = os.path.getsize(opt_filepath) / 1024

        success_text = (
            f"✅ **Успішно опубліковано!** 🎉\n\n"
            f"📁 **Категорія:** {cat_info['name']}\n"
            f"⚡ **Розмір WebP:** {size_kb:.1f} KB\n"
            f"🌐 **Фото додано на сайт!**"
        )

        # Delete button markup
        delete_markup = InlineKeyboardMarkup()
        delete_markup.add(InlineKeyboardButton("🗑️ Видалити це фото з сайту", callback_data=f"del:{folder_name}:{filename_webp}"))

        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=success_text,
            reply_markup=delete_markup,
            parse_mode="Markdown"
        )
        bot.answer_callback_query(call.id, "Опубліковано на сайті!")

    except Exception as e:
        bot.answer_callback_query(call.id, "Помилка при збереженні.")
        bot.send_message(call.message.chat.id, f"❌ Помилка під час обробки: {str(e)}")

@bot.message_handler(commands=['gallery', 'delete', 'manage'])
def start_gallery_manage(message):
    markup = InlineKeyboardMarkup(row_width=2)
    buttons = [
        InlineKeyboardButton(f"🖼️ {cat['name']}", callback_data=f"gal:{cat_key}:0")
        for cat_key, cat in CATEGORIES.items()
    ]
    markup.add(*buttons)
    bot.reply_to(
        message,
        "🖼️ **Оберіть категорію для перегляду та видалення фотографій з сайту:**",
        reply_markup=markup,
        parse_mode="Markdown"
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('gal:'))
def process_gallery_browse(call):
    try:
        parts = call.data.split(':')
        cat_key = parts[1]
        page_idx = int(parts[2])

        cat_info = CATEGORIES[cat_key]
        folder_name = cat_info["folder"]

        # Parse current photos in index.html for this category
        photos = get_photos_for_category_from_html(cat_key)

        if not photos:
            bot.answer_callback_query(call.id, f"У категорії {cat_info['name']} немає фотографій.")
            bot.send_message(call.message.chat.id, f"📭 У категорії **{cat_info['name']}** наразі немає фотографій.")
            return

        total_photos = len(photos)
        if page_idx >= total_photos:
            page_idx = 0
        elif page_idx < 0:
            page_idx = total_photos - 1

        photo_item = photos[page_idx]
        thumb_path = photo_item["thumb"]
        abs_thumb_path = os.path.join(BASE_DIR, thumb_path)

        # Pagination & Delete markup
        markup = InlineKeyboardMarkup(row_width=3)
        prev_idx = (page_idx - 1) % total_photos
        next_idx = (page_idx + 1) % total_photos

        nav_btns = [
            InlineKeyboardButton("⬅️ Попередня", callback_data=f"gal:{cat_key}:{prev_idx}"),
            InlineKeyboardButton(f"{page_idx + 1} / {total_photos}", callback_data="ignore"),
            InlineKeyboardButton("Наступна ➡️", callback_data=f"gal:{cat_key}:{next_idx}")
        ]
        markup.add(*nav_btns)
        markup.add(InlineKeyboardButton("🗑️ Видалити ЦЕ фото з сайту", callback_data=f"del_path:{thumb_path}:{cat_key}:{page_idx}"))

        caption_text = (
            f"🖼️ **Категорія:** {cat_info['name']}\n"
            f"📍 **Фото {page_idx + 1} з {total_photos}**\n"
            f"📄 `{os.path.basename(thumb_path)}`"
        )

        bot.answer_callback_query(call.id)

        if os.path.exists(abs_thumb_path):
            with open(abs_thumb_path, 'rb') as photo_file:
                bot.send_photo(
                    call.message.chat.id,
                    photo=photo_file,
                    caption=caption_text,
                    reply_markup=markup,
                    parse_mode="Markdown"
                )
        else:
            bot.send_message(
                call.message.chat.id,
                text=caption_text,
                reply_markup=markup,
                parse_mode="Markdown"
            )

    except Exception as e:
        bot.answer_callback_query(call.id, "Помилка при перегляді.")
        bot.send_message(call.message.chat.id, f"❌ Помилка: {str(e)}")

@bot.callback_query_handler(func=lambda call: call.data.startswith('del:'))
def process_photo_delete_direct(call):
    try:
        parts = call.data.split(':')
        folder_name = parts[1]
        filename_webp = parts[2]

        # Remove from HTML
        remove_photo_from_html(filename_webp)

        # Remove files from disk
        opt_filepath = os.path.join(BASE_DIR, "images", "optimized", folder_name, filename_webp)
        thumb_filepath = os.path.join(BASE_DIR, "images", "thumbs", folder_name, filename_webp)

        if os.path.exists(opt_filepath):
            os.remove(opt_filepath)
        if os.path.exists(thumb_filepath):
            os.remove(thumb_filepath)

        bot.answer_callback_query(call.id, "Фото видалено з сайту!")
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"🗑️ **Фото `{filename_webp}` успішно видалено з сайту та з диска!**",
            parse_mode="Markdown"
        )
    except Exception as e:
        bot.answer_callback_query(call.id, "Помилка при видаленні.")
        bot.send_message(call.message.chat.id, f"❌ Помилка видалення: {str(e)}")

@bot.callback_query_handler(func=lambda call: call.data.startswith('del_path:'))
def process_delete_by_path(call):
    try:
        parts = call.data.split(':', 3)
        thumb_path = parts[1]
        cat_key = parts[2]
        page_idx = parts[3]

        filename_webp = os.path.basename(thumb_path)

        # Remove from HTML
        remove_photo_from_html(filename_webp)

        # Remove files from disk
        abs_thumb = os.path.join(BASE_DIR, thumb_path)
        opt_path = thumb_path.replace("images/thumbs/", "images/optimized/")
        abs_opt = os.path.join(BASE_DIR, opt_path)

        if os.path.exists(abs_thumb):
            os.remove(abs_thumb)
        if os.path.exists(abs_opt):
            os.remove(abs_opt)

        bot.answer_callback_query(call.id, "❌ Фото видалено з сайту!")
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"🗑️ **Фото `{filename_webp}` успішно видалено з сайту та з диска!**",
            parse_mode="Markdown"
        )

    except Exception as e:
        bot.answer_callback_query(call.id, "Помилка при видаленні.")
        bot.send_message(call.message.chat.id, f"❌ Помилка видалення: {str(e)}")

def get_photos_for_category_from_html(category):
    if not os.path.exists(INDEX_HTML):
        return []

    with open(INDEX_HTML, 'r', encoding='utf-8') as f:
        content = f.read()

    import re
    pattern = r'<div\s+class="gallery__item[^"]*"\s+data-category="' + re.escape(category) + r'"[^>]*>.*?<img\s+src="([^"]+)".*?</div>'
    matches = re.findall(pattern, content, re.DOTALL)

    photos = []
    for thumb_src in matches:
        photos.append({
            "thumb": thumb_src,
            "category": category
        })
    return photos

def insert_photo_to_html(category, thumb_path, opt_path, alt_text):
    if not os.path.exists(INDEX_HTML):
        return

    with open(INDEX_HTML, 'r', encoding='utf-8') as f:
        content = f.read()

    new_item_html = (
        f'        <div class="gallery__item gallery__item--portrait" data-category="{category}">\n'
        f'          <img src="{thumb_path}" data-src="{opt_path}"\n'
        f'            alt="{alt_text}" loading="lazy" width="600" height="800">\n'
        f'        </div>\n'
    )

    marker = '<div class="gallery__track" id="galleryTrack">'
    if marker in content:
        content = content.replace(marker, f'{marker}\n{new_item_html}')
        with open(INDEX_HTML, 'w', encoding='utf-8') as f:
            f.write(content)
        git_push_changes(f"Auto upload photo to {category} via Telegram Bot")

def remove_photo_from_html(photo_filename):
    if not os.path.exists(INDEX_HTML):
        return False

    filename = os.path.basename(photo_filename)

    with open(INDEX_HTML, 'r', encoding='utf-8') as f:
        content = f.read()

    import re
    pattern = r'\s*<div\s+class="gallery__item[^"]*"[^>]*>[\s\S]*?' + re.escape(filename) + r'[\s\S]*?</div>'
    new_content = re.sub(pattern, '', content)

    if new_content != content:
        with open(INDEX_HTML, 'w', encoding='utf-8') as f:
            f.write(new_content)
        git_push_changes(f"Auto delete photo {filename} via Telegram Bot")
        return True
    return False

def git_push_changes(commit_msg="Auto update portfolio via Telegram Bot"):
    try:
        import subprocess
        subprocess.run(["git", "add", "."], cwd=BASE_DIR, check=False)
        subprocess.run(["git", "commit", "-m", commit_msg], cwd=BASE_DIR, check=False)
        
        git_res = subprocess.run(["git", "push"], cwd=BASE_DIR, capture_output=True, text=True)
        if git_res.returncode == 0:
            print(f"🚀 Git push executed: {commit_msg}")
        else:
            print("ℹ️ Git remote unconfigured, trying Netlify CLI deploy...")
            subprocess.run(["npx", "netlify", "deploy", "--prod", "--dir=."], cwd=BASE_DIR, check=False)
    except Exception as e:
        print(f"⚠️ Deploy notice: {e}")

if __name__ == '__main__':
    print("🚀 Telegram Bot linettka portfolio uploader запущено...")
    bot.infinity_polling()
