import datetime
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, CommandHandler

# --- 1. جزء الويب سيرفر (عشان UptimeRobot يصحيه) ---
app_web = Flask('')
@app_web.route('/')
def home(): return "🤖 Bot is running smoothly on the cloud!"

def run(): app_web.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

# --- 2. الإعدادات الأساسية ---
TOKEN = '8688241569:AAGh2U58zOExXRkfchZf_SnU2mfocfMorII' # <--- تم وضع التوكن الخاص بك
MY_ID = 7804212970 # <--- معرفك الشخصي لاستقبال الرسائل
GITHUB_URL = "https://github.com/mohamed3155468"

# --- 3. الكلمات المفتاحية ---
STUDY_KEYS = ["مذاكرة", "تذاكر", "تدرس", "دراسة", "study", "studying", "فيزياء", "physics", "شنو تسوي", "شو عم تعمل", "وراك ايه"]
DEV_KEYS = ["المطور", "developer", "المبرمج", "dev", "منو سواك", "مين عملك", "about", "عنك", "معلومات"]
TIME_KEYS = ["امتى", "وقت", "time", "متى", "تفتح", "موجود", "شوكت", "open", "ساعة"]
HEALTH_KEYS = ["ازيك", "اخبارك", "عامل ايه", "كيف حالك", "شلونك", "how are you"]

# --- 4. الأوامر والردود ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر البداية مع أزرار تفاعلية"""
    keyboard = [
        [InlineKeyboardButton("👨‍💻 المطور والرحلة", callback_data='dev'),
         InlineKeyboardButton("📖 المذاكرة والدروس", callback_data='study')],
        [InlineKeyboardButton("⏳ المواعيد", callback_data='time'),
         InlineKeyboardButton("💻 حسابي على GitHub", url=GITHUB_URL)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = (
        f"╭─── • {update.message.from_user.first_name} • ───╮\n"
        "  أهلاً بك في بوت المبرمج محمد العالمي! 🌍\n"
        "  أنا أفهم كل اللهجات (مصر، خليج، شام) والإنجليزية.\n"
        "╰──── • ✨ • ────╯\n"
        "اضغط على الأزرار بالأسفل أو اسألني أي سؤال!"
    )
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة كافة الرسائل وإرسال نسخة للمطور"""
    if not update.message or not update.message.text: return
    
    user = update.message.from_user
    text = update.message.text
    text_lower = text.lower()
    now = datetime.datetime.now()

    # --- الجزء المضاف: إرسال نسخة لك ---
    if user.id != MY_ID:
        forward_info = (
            f"🔔 **رسالة جديدة للمستودع:**\n"
            f"👤 الاسم: {user.first_name}\n"
            f"🆔 الآيدي: `{user.id}`\n"
            f"💬 الرسالة: {text}"
        )
        await context.bot.send_message(chat_id=MY_ID, text=forward_info, parse_mode='Markdown')
    # --------------------------------

    dev_reply = (
        "✨ **بـطـاقـة تـعـريـف المـطـور والـرحـلـة** ✨\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "👤 **المطور:** المبرمج محمد 🇪🇬\n"
        "🎓 **المستوى:** طالب ثانية ثانوي (مبدع مستقبلي)\n"
        "💻 **التخصص:** Python & Bot Developer\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "🚀 **رحـلـة بـنـاء هـذا الـبـوت:**\n"
        "1️⃣ **البداية:** كود بسيط على Pydroid من الموبايل.\n"
        "2️⃣ **التنظيم:** رفع الكود على GitHub كالمحترفين.\n"
        "3️⃣ **السحاب:** النشر على Replit ليعمل أونلاين.\n"
        "4️⃣ **الاستمرارية:** ربطه بـ UptimeRobot للعمل 24 ساعة.\n"
        "5️⃣ **العالمية:** دعم اللغات واللهجات المتعددة.\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "🌟 **الهدف:** إثبات أن الإبداع لا يعرف عمراً!\n"
        "📈 **الحالة:** يعمل بنجاح في السحاب ☁️\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "✨ *صُنع بكل فخر بواسطة محمد*"
    )

    if any(word in text_lower for word in DEV_KEYS):
        await update.message.reply_text(dev_reply, parse_mode='Markdown')
    
    elif any(word in text_lower for word in STUDY_KEYS):
        reply = f"📖 ┋ محمد حالياً {'بيذاكر فيزياء' if now.hour < 21 else 'بيخلص دروسه'}.. تانية ثانوي محتاجة تركيز! ✍️"
        await update.message.reply_text(reply)

    elif any(word in text_lower for word in TIME_KEYS):
        reply = "🕒 ┋ المبرمج يتواجد غالباً من 9 مساءً بتوقيت القاهرة. سيب رسالتك وهيقرأها!"
        await update.message.reply_text(reply)

    elif any(word in text_lower for word in HEALTH_KEYS):
        reply = "🌟 ┋ مبرمجي بخير ولله الحمد، شكراً لسؤالك الراقي! 😊"
        await update.message.reply_text(reply)

    else:
        unknown_reply = (
            "⚠️ **عذراً يا صديقي، المبرمج يعمل على بقية الردود.**\n\n"
            "الرجاء اختيار سؤال آخر:\n"
            "• اسأل عن (المذاكرة) 📖\n"
            "• اسأل عن (المطور) 👨‍💻\n"
            "• اسأل عن (المواعيد) ⏳\n"
            "أو جرب التحدث بالإنجليزية (Study, Dev)!"
        )
        await update.message.reply_text(unknown_reply, parse_mode='Markdown')

# --- 5. تشغيل البوت ---
if __name__ == '__main__':
    keep_alive()
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("🚀 البوت العالمي المطور انطلق الآن مع خاصية التنبيهات!")
    app.run_polling()
