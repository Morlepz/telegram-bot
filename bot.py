from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    ContextTypes,
    filters,
)
from telegram import Update, ChatPermissions
import sys
from datetime import datetime, timedelta
from datetime import timezone
import os
import asyncio
sys.stdout.reconfigure(encoding='utf-8')

TOKEN = os.getenv("TOKEN")

bad_words = ["sik", "sikim", "peyser", "peysər", "cindir", "cındır", "pesi", "qehbe",
             "qəhbə", "orospu", "oç", "gijdıllaq", "gijdillax", "gidjillax", "gijdılax", "gijdilax", "siktir", "sikdir", "osdur", "balası", "skdr", "götverən", "qancix", "yarrak", "yarak", "taşak", "am", "amina koyim", "ananı", "skm", "anneni", "amına"]

warns = {}


async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):

    for member in update.message.new_chat_members:
        await update.message.reply_text(
            f"👋 Xoş gəldin {member.first_name}!\n\n"
            """📌 SAİD FX – Qaydalar

Bu icma sistemli və ciddi trading üçündür.
Keyfiyyət hər şeydən vacibdir.

⚖️ Qaydalar

1️⃣ Hörmət – şəxsi hücum və aqressiya qadağandır.
2️⃣ Spam və reklam qəti qadağandır.
3️⃣ Siqnal istəmək və ya “haradan girim?” tipli suallar qəbul edilmir.
4️⃣ Risk öz məsuliyyətinizdədir. Burada paylaşılanlar təhsil məqsədlidir.
5️⃣ Emosional mübahisə yox, məntiqi müzakirə var.
                                                                                                                                                                     SAİD FX = Struktur + Statistika + Risk İdarəsi
Siqnal yoxdur. Sistem var."""
        )


# MUTE FUNCTION
async def mute_user(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    try:
        until_date = datetime.now(timezone.utc) + timedelta(minutes=10)
        await context.bot.restrict_chat_member(
            chat_id=update.effective_chat.id,
            user_id=user_id,
            permissions=ChatPermissions(
                can_send_messages=False,
                can_send_other_messages=False,
                can_add_web_page_previews=False
            ),
            until_date=until_date
        )
    except Exception:
        pass  # silently ignore if user is admin/owner

# MEDIA DELETE (PHOTO + VIDEO + STICKER + GIF)
async def delete_media(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user
    chat_id = update.effective_chat.id

    # mesajı sil
    await update.message.delete()

    if chat_id not in warns:
        warns[chat_id] = {}

    if user.id not in warns[chat_id]:
        warns[chat_id][user.id] = 0

    warns[chat_id][user.id] += 1
    count = warns[chat_id][user.id]

    if count < 3:
        await update.message.reply_text(
            f"{user.first_name}, media (şəkil/video/stiker) qadağandır ⚠️ ({count}/3)"
        )
    else:
        await mute_user(update, context, user.id)
        await update.message.reply_text(
            f"{user.first_name} 3 dəfə media qaydası pozdu → MUTE 🔇"
        )


# TEXT ARGO FILTER
async def filter_bad_words(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    # rest of the function stays the same

    user = update.effective_user
    chat_id = update.effective_chat.id
    text = update.message.text.lower()

    if chat_id not in warns:
        warns[chat_id] = {}

    if user.id not in warns[chat_id]:
        warns[chat_id][user.id] = 0

    for word in bad_words:
        if word in text:

            warns[chat_id][user.id] += 1
            count = warns[chat_id][user.id]

            if count < 3:
                await update.message.reply_text(
                    f"{user.first_name}, xəbərdarlıq {count}/3 ⚠️"
                )
            else:
                await mute_user(update, context, user.id)
                await update.message.reply_text(
                    f"{user.first_name} 3 dəfə arqo → MUTE 🔇"
                )
            await update.message.delete()
            break


# APP
app = ApplicationBuilder().token(TOKEN).build()

# TEXT
app.add_handler(MessageHandler(
    filters.TEXT & ~filters.COMMAND, filter_bad_words))

# MEDIA (PHOTO + VIDEO + GIF + STICKER)
app.add_handler(MessageHandler(
    filters.PHOTO | filters.VIDEO | filters.ANIMATION | filters.Sticker.ALL,
    delete_media
))

app.add_handler(
    MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome)
)

print("Bot işləyir...")
asyncio.run(app.run_polling())






