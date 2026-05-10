"""
VIS ART Ko'z Klinikasi - Telegram Bot
=====================================
O'rnatish:
    pip install python-telegram-bot==20.7

Ishlatish:
    1. @BotFather orqali yangi bot yarating va TOKEN oling
    2. Quyidagi BOT_TOKEN o'zgaruvchisini to'ldiring
    3. python visart_bot.py buyrug'i bilan ishga tushiring
"""

import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes, ConversationHandler
)

# ─── SOZLAMALAR ────────────────────────────────────────────────────────────────
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
ADMIN_CHAT_ID = int(os.environ.get("ADMIN_CHAT_ID", "0"))

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ─── HOLAT KONSTANTLARI (ConversationHandler uchun) ────────────────────────────
ASK_NAME, ASK_PHONE, ASK_DATE, ASK_SERVICE = range(4)

# ─── KLINIKA MA'LUMOTLARI ──────────────────────────────────────────────────────
CLINIC_INFO = {
    "nomi": "VIS ART Ko'z Klinikasi",
    "manzil": "Toshkent, Uchtepa tumani, 7-tor Qo'shilish ko'chasi, 1A-uy",
    "telefon": ["+998 71 275-77-88", "+998 71 275-77-66",
                "+998 97 729-76-56", "+998 94 642-22-91"],
    "email": "visartuz@gmail.com",
    "instagram": "@visart_uz",
    "telegram": "t.me/visart_uz",
    "ish_vaqti": {
        "Dushanba – Juma": "09:00 – 17:00",
        "Shanba":          "09:00 – 12:00",
        "Yakshanba":       "Dam olish kuni",
    },
    "maps": "https://maps.google.com/?q=41.2857587,69.1649972",
}

XIZMATLAR = {
    "👁 Vitreoretinal jarrohlik": (
        "Ko'z olmasi to'r pardasidagi murakkab operatsiyalar. "
        "Klinikamiz bu sohadagi O'zbekiston yetakchilaridan biri hisoblanadi."
    ),
    "🔬 Ko'z kasalliklari diagnostikasi": (
        "15+ yillik tajriba bilan barcha ko'z kasalliklarini aniq tashxislash va davolash."
    ),
    "👓 Ko'rish tuzatish": (
        "Ko'rish nuqsonlarini aniqlash, ko'zoynak va linzalar tanlash."
    ),
    "🕶 Optika": (
        "Individual ko'zoynak tayyorlash — fotoximik, monoxrom va quyoshdan himoya qiluvchi."
    ),
    "👂 LOR (Quloq-Burun-Tomoq)": (
        "Quloq, burun va tomoq kasalliklarini yuqori darajada diagnostika va davolash."
    ),
    "❤️ Kardiologiya": (
        "Yurak kasalliklarini tashxislash va davolash bo'yicha mutaxassislar xizmati."
    ),
    "🧪 Laboratoriya": (
        "Barcha zarur qon va boshqa tahlillar."
    ),
    "💆 Kosmetologiya": (
        "Estetik tibbiyot va teri parvarishi xizmatlari."
    ),
}

SHIFOKORLAR = [
    {
        "ism":       "Ibrohimova La'li Omonilyevna",
        "mutaxassis": "Vitreoretinal jarroh",
        "emoji":     "👩‍⚕️",
    },
    {
        "ism":       "Fayzulloyev San'at Sayfilloyevich",
        "mutaxassis": "Vitreoretinal jarroh",
        "emoji":     "👨‍⚕️",
    },
    {
        "ism":       "Karimova Gulnora Omonilyevna",
        "mutaxassis": "LOR-jarroh",
        "emoji":     "👩‍⚕️",
    },
    {
        "ism":       "Umarov Farrux Yaqubovich",
        "mutaxassis": "Oftalmojarroh",
        "emoji":     "👨‍⚕️",
    },
    {
        "ism":       "Umarova Kamola Jabbarovna",
        "mutaxassis": "Oftalmojarroh",
        "emoji":     "👩‍⚕️",
    },
    {
        "ism":       "Bakayev Iskandar Axrorovich",
        "mutaxassis": "Kardioreanimatolог",
        "emoji":     "👨‍⚕️",
    },
]

# ─── ASOSIY MENYU ──────────────────────────────────────────────────────────────
def asosiy_menyu():
    tugmalar = [
        [InlineKeyboardButton("🩺 Xizmatlar", callback_data="xizmatlar"),
         InlineKeyboardButton("👨‍⚕️ Shifokorlar", callback_data="shifokorlar")],
        [InlineKeyboardButton("📅 Qabul uchun yozilish", callback_data="yozilish")],
        [InlineKeyboardButton("🕐 Ish vaqti", callback_data="ish_vaqti"),
         InlineKeyboardButton("📍 Manzil", callback_data="manzil")],
        [InlineKeyboardButton("📞 Kontaktlar", callback_data="kontaktlar")],
    ]
    return InlineKeyboardMarkup(tugmalar)

def ortga_tugma():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Asosiy menyu", callback_data="asosiy")]])

# ─── /start BUYRUG'I ───────────────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    foydalanuvchi = update.effective_user.first_name or "Mehmon"
    xabar = (
        f"🏥 Assalomu alaykum, {foydalanuvchi}!\n\n"
        f"*VIS ART Ko'z Klinikasiga xush kelibsiz!*\n\n"
        f"Biz 15+ yillik tajriba bilan ko'z kasalliklarini davolash, "
        f"vitreoretinal jarrohlik va boshqa tibbiy xizmatlarni taklif etamiz.\n\n"
        f"⭐ *10 000+* muvaffaqiyatli operatsiya\n"
        f"👨‍⚕️ Malakali mutaxassislar jamoasi\n\n"
        f"Quyidagi bo'limlardan birini tanlang:"
    )
    await update.message.reply_text(xabar, parse_mode="Markdown", reply_markup=asosiy_menyu())

# ─── CALLBACK QUERY HANDLER ────────────────────────────────────────────────────
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    # Asosiy menyu
    if data == "asosiy":
        xabar = (
            "🏥 *VIS ART Ko'z Klinikasi*\n\n"
            "Kerakli bo'limni tanlang:"
        )
        await query.edit_message_text(xabar, parse_mode="Markdown", reply_markup=asosiy_menyu())

    # Xizmatlar
    elif data == "xizmatlar":
        tugmalar = []
        for i, xizmat in enumerate(XIZMATLAR.keys()):
            tugmalar.append([InlineKeyboardButton(xizmat, callback_data=f"xizmat_{i}")])
        tugmalar.append([InlineKeyboardButton("🔙 Asosiy menyu", callback_data="asosiy")])
        xabar = "🩺 *Bizning xizmatlarimiz:*\n\nBatafsil ma'lumot uchun xizmatni tanlang:"
        await query.edit_message_text(xabar, parse_mode="Markdown",
                                       reply_markup=InlineKeyboardMarkup(tugmalar))

    # Alohida xizmat
    elif data.startswith("xizmat_"):
        idx = int(data.split("_")[1])
        xizmat_nomi = list(XIZMATLAR.keys())[idx]
        xizmat_tavsifi = list(XIZMATLAR.values())[idx]
        xabar = f"*{xizmat_nomi}*\n\n{xizmat_tavsifi}"
        tugmalar = [
            [InlineKeyboardButton("📅 Shu xizmat uchun yozilish", callback_data=f"yozilish_xizmat_{idx}")],
            [InlineKeyboardButton("🔙 Xizmatlar", callback_data="xizmatlar")],
        ]
        await query.edit_message_text(xabar, parse_mode="Markdown",
                                       reply_markup=InlineKeyboardMarkup(tugmalar))

    # Shifokorlar
    elif data == "shifokorlar":
        xabar = "👨‍⚕️ *Bizning mutaxassislarimiz:*\n\n"
        for sh in SHIFOKORLAR:
            xabar += f"{sh['emoji']} *{sh['ism']}*\n   _{sh['mutaxassis']}_\n\n"
        xabar += "📞 Qabul uchun: +998 71 275-77-88"
        await query.edit_message_text(xabar, parse_mode="Markdown", reply_markup=ortga_tugma())

    # Ish vaqti
    elif data == "ish_vaqti":
        xabar = "🕐 *Ish vaqtimiz:*\n\n"
        for kun, vaqt in CLINIC_INFO["ish_vaqti"].items():
            xabar += f"📅 {kun}: *{vaqt}*\n"
        xabar += "\n💡 Qabul oldindan belgilanishi tavsiya etiladi."
        await query.edit_message_text(xabar, parse_mode="Markdown", reply_markup=ortga_tugma())

    # Manzil
    elif data == "manzil":
        xabar = (
            f"📍 *Bizning manzilichimiz:*\n\n"
            f"{CLINIC_INFO['manzil']}\n\n"
            f"🗺 [Google Xaritada ko'rish]({CLINIC_INFO['maps']})\n\n"
            f"Mo'ljal: Uchtepa tumani, 7-tor Qo'shilish ko'chasi"
        )
        await query.edit_message_text(xabar, parse_mode="Markdown",
                                       reply_markup=ortga_tugma(), disable_web_page_preview=False)

    # Kontaktlar
    elif data == "kontaktlar":
        tel_matn = "\n".join([f"📞 {t}" for t in CLINIC_INFO["telefon"]])
        xabar = (
            f"📬 *Bizga bog'laning:*\n\n"
            f"{tel_matn}\n\n"
            f"📧 {CLINIC_INFO['email']}\n"
            f"📸 Instagram: {CLINIC_INFO['instagram']}\n"
            f"✈️ Telegram: {CLINIC_INFO['telegram']}\n\n"
            f"🕐 Ish vaqti: Du-Ju 09:00–17:00 | Sh 09:00–12:00"
        )
        await query.edit_message_text(xabar, parse_mode="Markdown", reply_markup=ortga_tugma())

    # Yozilish boshlash
    elif data == "yozilish" or data.startswith("yozilish_xizmat_"):
        if data.startswith("yozilish_xizmat_"):
            idx = int(data.split("_")[-1])
            xizmat_nomi = list(XIZMATLAR.keys())[idx]
            context.user_data["tanlangan_xizmat"] = xizmat_nomi
        xabar = (
            "📋 *Qabul uchun yozilish*\n\n"
            "Ismingizni kiriting (To'liq ism va familiya):"
        )
        await query.edit_message_text(xabar, parse_mode="Markdown")
        return ASK_NAME

# ─── QABUL YOZILISH (ConversationHandler) ─────────────────────────────────────
async def ask_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["ism"] = update.message.text
    xabar = (
        f"✅ Rahmat, *{update.message.text}*!\n\n"
        f"📱 Endi telefon raqamingizni kiriting:\n"
        f"_(Misol: +998901234567)_"
    )
    await update.message.reply_text(xabar, parse_mode="Markdown")
    return ASK_PHONE

async def ask_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["telefon"] = update.message.text
    tugmalar = []
    xizmatlar = list(XIZMATLAR.keys())
    for i in range(0, len(xizmatlar), 2):
        qator = [KeyboardButton(xizmatlar[i])]
        if i + 1 < len(xizmatlar):
            qator.append(KeyboardButton(xizmatlar[i + 1]))
        tugmalar.append(qator)
    if "tanlangan_xizmat" not in context.user_data:
        xabar = "🩺 Qaysi xizmat bo'yicha murojaat qilmoqchisiz?"
        await update.message.reply_text(
            xabar,
            reply_markup=ReplyKeyboardMarkup(tugmalar, resize_keyboard=True, one_time_keyboard=True)
        )
        return ASK_SERVICE
    else:
        xabar = "📅 Qaysi sana va vaqtda kelishni xohlaysiz?\n_(Misol: 15-may, soat 10:00)_"
        await update.message.reply_text(xabar, parse_mode="Markdown")
        return ASK_DATE

async def ask_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["tanlangan_xizmat"] = update.message.text
    xabar = "📅 Qaysi sana va vaqtda kelishni xohlaysiz?\n_(Misol: 15-may, soat 10:00)_"
    await update.message.reply_text(xabar, parse_mode="Markdown")
    return ASK_DATE

async def ask_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from telegram import ReplyKeyboardRemove
    context.user_data["sana"] = update.message.text
    d = context.user_data

    # Foydalanuvchiga tasdiqlash
    xabar = (
        "✅ *Qabulingiz qabul qilindi!*\n\n"
        f"👤 Ism: *{d.get('ism', '—')}*\n"
        f"📱 Telefon: *{d.get('telefon', '—')}*\n"
        f"🩺 Xizmat: *{d.get('tanlangan_xizmat', '—')}*\n"
        f"📅 Sana: *{d.get('sana', '—')}*\n\n"
        "📞 Tez orada administratorimiz siz bilan bog'lanadi.\n\n"
        "🕐 Ish vaqtimiz: Du-Ju 09:00–17:00 | Sh 09:00–12:00\n"
        "📞 Tel: +998 71 275-77-88"
    )
    await update.message.reply_text(xabar, parse_mode="Markdown",
                                     reply_markup=ReplyKeyboardRemove())

    # Adminga xabar yuborish
    admin_xabar = (
        "🔔 *YANGI QABUL SO'ROVI*\n\n"
        f"👤 Ism: {d.get('ism', '—')}\n"
        f"📱 Telefon: {d.get('telefon', '—')}\n"
        f"🩺 Xizmat: {d.get('tanlangan_xizmat', '—')}\n"
        f"📅 Sana: {d.get('sana', '—')}\n"
        f"🆔 Telegram ID: {update.effective_user.id}"
    )
    try:
        await context.bot.send_message(ADMIN_CHAT_ID, admin_xabar, parse_mode="Markdown")
    except Exception as e:
        logger.warning(f"Admin xabari yuborilmadi: {e}")

    # Asosiy menyuga qaytish
    await update.message.reply_text(
        "Asosiy menyuga qaytish uchun /start bosing.",
        reply_markup=asosiy_menyu()
    )
    context.user_data.clear()
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from telegram import ReplyKeyboardRemove
    await update.message.reply_text(
        "❌ Bekor qilindi. Asosiy menyu:",
        reply_markup=ReplyKeyboardRemove()
    )
    await update.message.reply_text("Tanlang:", reply_markup=asosiy_menyu())
    context.user_data.clear()
    return ConversationHandler.END

# ─── NOMA'LUM XABAR ────────────────────────────────────────────────────────────
async def noma_lum_xabar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Iltimos, quyidagi menyudan foydalaning:",
        reply_markup=asosiy_menyu()
    )

# ─── BOTNI ISHGA TUSHIRISH ─────────────────────────────────────────────────────
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Qabul yozilish suhbati
    conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(callback_handler, pattern="^yozilish"),
        ],
        states={
            ASK_NAME:    [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_name)],
            ASK_PHONE:   [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_phone)],
            ASK_SERVICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_service)],
            ASK_DATE:    [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_date)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, noma_lum_xabar))

    print("✅ VIS ART Bot ishga tushdi...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
