import datetime
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# --- جزء الويب سيرفر (عشان UptimeRobot) ---
app_web = Flask('')
@app_web.route('/')
def home(): return "🚀 البوت يعمل بنجاح!"

def run(): app_web.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()
# ----------------------------------------------

TOKEN = '8688241569:AAGh2U58zOExXRkfchZf_SnU2mfocfMorII'
user_last_seen = {}

async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
        
    user_id = update.message.from_user.id
    user_name = update.message.from_user.first_name
    user_text = update.message.text.lower()
    now = datetime.datetime.now()

    # 1. معلومات المطور
    dev_keywords = ["المطور", "مين المبرمج", "عنك", "مين عملك"]
    dev_reply = "👨‍💻 **المطور:** المبرمج محمد\n🎓 **المستوى:** ثانية ثانوي\n🤖 **الحالة:** متاح للرد التلقائي"

    # 2. المذاكرة
    study_keywords = ["بتذاكر", "مذاكرة", "وراك ايه", "فيزياء"]
    study_reply = f"📖 ┋ محمد حالياً {'بيذاكر فيزياء' if now.hour < 20 else 'بيراجع دروسه'}.. ثانية ثانوي محتاجة تركيز! ✍️"

    # 3. المواعيد
    time_keywords = ["امتى", "إمتى", "تفتح", "موجود"]
    time_reply = "✨ ┋ المبرمج محمد بيفتح عادةً في المساء، سيب رسالتك وهيقرأها أول ما يدخل! 🌙"

    # 4. الرسالة الافتراضية (لو السؤال مش معروف)
    unknown_reply = (
        "⚠️ **عذراً يا صديقي، المبرمج يعمل حالياً على بقية الردود.**\n\n"
        "الرجاء اختيار سؤال آخر مما يليه:\n"
        "• اسأل عن (المذاكرة) 📖\n"
        "• اسأل عن (المطور) 👨‍💻\n"
        "• اسأل عن (المواعيد) ⏳\n"
        "• اسأل عن (الحال) 😊"
    )

    # منطق الترحيب (كل 30 دقيقة)
    is_new_session = True
    if user_id in user_last_seen:
        if (now - user_last_seen[user_id]).total_seconds() / 60 < 30: is_new_session = False
    user_last_seen[user_id] = now

    if is_new_session:
        await update.message.reply_text(f"╭─── • {user_name} • ───╮\n  أهلاً بك! أنا بوت المبرمج محمد.\n╰──── • ✨ • ────╯")

    # فحص الردود
    if any(word in user_text for word in dev_keywords):
        await update.message.reply_text(dev_reply, parse_mode='Markdown')
    elif any(word in user_text for word in study_keywords):
        await update.message.reply_text(study_reply)
    elif any(word in user_text for word in time_keywords):
        await update.message.reply_text(time_reply)
    elif any(word in user_text for word in ["ازيك", "اخبارك", "عامل ايه"]):
        await update.message.reply_text("🌟 ┋ مبرمجي بخير، شكراً لسؤالك!")
    else:
        # الرد لو الرسالة مش معروفة
        await update.message.reply_text(unknown_reply, parse_mode='Markdown')

if __name__ == '__main__':
    keep_alive()
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), reply))
    print("🚀 البوت المطور يعمل الآن!")
    app.run_polling()
