import datetime
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, CommandHandler, CallbackQueryHandler

# --- 1. جزء الويب سيرفر ---
app_web = Flask('')
@app_web.route('/')
def home(): return "🤖 Bot is running smoothly!"

def run(): app_web.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

# --- 2. الإعدادات الأساسية ---
TOKEN = '8688241569:AAGh2U58zOExXRkfchZf_SnU2mfocfMorII'
MY_ID = 7804212970
GITHUB_URL = "https://github.com/mohamed3155468"

# رد المطور الموحد
DEV_REPLY_TEXT = (
    "✨ **بـطـاقـة تـعـريـف المـطـور والـرحـلـة** ✨\n"
    "━━━━━━━━━━━━━━━━━━\n"
    "👤 **المطور:** المبرمج محمد 🇪🇬\n"
    "🎓 **المستوى:** طالب ثانية ثانوي\n"
    "💻 **التخصص:** Python & Bot Developer\n"
    "━━━━━━━━━━━━━━━━━━\n"
    "🚀 **الرحلة:** من Pydroid إلى السحاب ☁️\n"
    "━━━━━━━━━━━━━━━━━━\n"
    "✨ *صُنع بكل فخر بواسطة محمد*"
)

# --- 3. الكلمات المفتاحية ---
STUDY_KEYS = ["مذاكرة", "تذاكر", "تدرس", "دراسة", "فيزياء", "physics"]
DEV_KEYS = ["المطور", "developer", "المبرمج", "dev", "عنك"]
TIME_KEYS = ["امتى", "وقت", "time", "متى"]
HEALTH_KEYS = ["ازيك", "اخبارك", "عامل ايه", "كيف حالك"]

# --- 4. الأوامر والردود ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("👨‍💻 المطور والرحلة", callback_data='dev_info'),
         InlineKeyboardButton("📖 المذاكرة والدروس", callback_data='study_info')],
        [InlineKeyboardButton("⏳ المواعيد", callback_data='time_info'),
         InlineKeyboardButton("💻 حسابي على GitHub", url=GITHUB_URL)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("أهلاً بك في بوت المبرمج محمد! 🌍\nاختر من الأزرار بالأسفل:", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """هذا الجزء هو المسؤول عن تشغيل الأزرار"""
    query = update.callback_query
    await query.answer() # لإخفاء علامة التحميل من فوق الزر
    now = datetime.datetime.now()

    if query.data == 'dev_info':
        await query.message.reply_text(DEV_REPLY_TEXT, parse_mode='Markdown')
    elif query.data == 'study_info':
        reply = f"📖 ┋ محمد حالياً {'بيذاكر فيزياء' if now.hour < 21 else 'بيخلص دروسه'}.. تانية ثانوي محتاجة تركيز! ✍️"
        await query.message.reply_text(reply)
    elif query.data == 'time_info':
        await query.message.reply_text("🕒 ┋ المبرمج يتواجد غالباً من 9 مساءً بتوقيت القاهرة.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    
    user = update.message.from_user
    text = update.message.text
    text_lower = text.lower()
    now = datetime.datetime.now()

    # إرسال نسخة لك
    if user.id != MY_ID:
        await context.bot.send_message(chat_id=MY_ID, text=f"🔔 رسالة من {user.first_name}:\n{text}")

    # الردود الذكية
    if any(word in text_lower for word in DEV_KEYS):
        await update.message.reply_text(DEV_REPLY_TEXT, parse_mode='Markdown')
    elif any(word in text_lower for word in STUDY_KEYS):
        await update.message.reply_text(f"📖 محمد حالياً في رحلة مع الفيزياء.. دعواتك! ✍️")
    elif any(word in text_lower for word in TIME_KEYS):
        await update.message.reply_text("🕒 المبرمج متاح من 9 مساءً.")
    else:
        await update.message.reply_text("⚠️ اسألني عن (المذاكرة، المطور، أو المواعيد)!")

# --- 5. تشغيل البوت ---
if __name__ == '__main__':
    keep_alive()
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    # إضافة معالج الأزرار هنا
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("🚀 البوت انطلق والأزرار أصبحت تعمل الآن!")
    app.run_polling()
