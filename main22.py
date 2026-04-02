import os
import requests
import time
from flask import Flask, request
from threading import Thread
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# --- 1. إعدادات الهوية ---
TG_TOKEN = '8637053407:AAELVpuwoMtPh0n1ekNOdMf0V6WM6F4lOKk' 
MY_ID = 7804212970 
G_ID = '7107571550'
G_TOKEN = 'B65d1e96662e4f9db5f2df1d58faf2e67848787ccb924aa1b0'

app_web = Flask(__name__)

# --- 2. النصوص والرسائل المزخرفة (القصة الكاملة بالتفصيل) ---

WELCOME_MSG = (
    "👑 **مرحباً بك في المحطة الرسمية للمبرمج محمد** 👑\n"
    "✨ ━━━━━━━ ● ━━━━━━━ ✨\n\n"
    "🤖 **أنا المساعد الرقمي فائق السرعة.**\n"
    "أعمل كجسر ذكي يربط عالم الواتساب بالتليجرام لحظياً.\n\n"
    "🚀 **استكشف تفاصيل الرحلة:**\n"
    "🔹 [ معلوماتك ] | 🔹 [ حالتك ]\n"
    "🔹 [ رحلتك ] | 🔹 [ المذاكرة ]\n\n"
    "✨ ━━━━━━━ ● ━━━━━━━ ✨"
)

ABOUT_REPLY = (
    "👨‍💻 **سِجِلُّ المُمَبرمجِ مُحَمَّد: قصةُ طموحٍ وتحدٍّ**\n"
    "✨ ━━━━━━━ ● ━━━━━━━ ✨\n\n"
    "👤 **مَن هو محمد؟**\n"
    "طالب بالصف الثاني الثانوي (علمي)، مبرمج شغوف بلغة Python، استطاع تحويل هاتفه المحمول إلى بيئة تطوير احترافية.\n\n"
    "🛣 **تفاصيل رحلة الكفاح البرمجية:**\n\n"
    "🌱 **المرحلة الأولى: البداية من الصفر**\n"
    "بدأ محمد بتعلم أساسيات البرمجة من الموبايل عبر تطبيق Pydroid 3. كانت أولى التحديات هي فهم المنطق البرمجي وكيفية كتابة دوال بسيطة.\n\n"
    "🔧 **المرحلة الثانية: بناء العقل (Telegram API)**\n"
    "انتقل محمد لبناء أول بوت تليجرام، حيث تعلم التعامل مع مكتبات `python-telegram-bot`. واجه صعوبات في معالجة الرسائل وتنظيم الردود، لكنه أصر على التكرار حتى نجح.\n\n"
    "🔗 **المرحلة الثالثة: الجسر المستحيل (WhatsApp API)**\n"
    "جاءت الفكرة العبقرية بربط الواتساب بالتليجرام. استخدم تقنية **Green API** وواجه تحديات في ربط الـ Instance واستقبال الإشعارات، وقام ببرمجة نظام `wa_monitor` للفحص الدوري.\n\n"
    "⚡️ **المرحلة الرابعة: عصر السرعة والـ Webhooks**\n"
    "لم يكتفِ محمد بالبطء، فقام بتطوير البوت ليعمل بنظام الـ **Webhook** عبر مكتبة **Flask**. هذا مكنه من استقبال الرسائل في جزء من الثانية فور وصولها للواتساب.\n\n"
    "☁️ **المرحلة الخامسة: الانطلاق السحابي**\n"
    "ختام الرحلة كان بربط المشروع بـ **GitHub** ورفعه على سيرفرات **Render** السحابية، مع إضافة نظام 'النغز' (Ping) لضمان بقاء البوت مستيقظاً 24/7.\n\n"
    "📚 **الهدف:** التميز في دراسة الفيزياء والرياضيات مع تطوير مشاريع ذكاء اصطناعي تخدم المجتمع.\n\n"
    "💡 **الحكمة:** « العِلْمُ لَا يَعْرِفُ عُمْراً.. والمثابرة تصنع المستحيل » ⚡️\n"
    "✨ ━━━━━━━ ● ━━━━━━━ ✨"
)

# القواميس
HEALTH_KEYS = ["ازيك", "الازيك", "عامل ايه", "حالتك", "الحالة", "بخير", "اخبارك", "الاخبار"]
STUDY_KEYS = ["مذاكرة", "المذاكرة", "تذاكر", "التذاكر", "دراسة", "الدراسة", "فيزياء", "الفيزياء", "فيزيا", "physics"]
ABOUT_KEYS = ["انت مين", "إنت مين", "معلوماتك", "المعلومات", "عنك", "ملفك", "المطور", "المبرمج"]
JOURNEY_KEYS = ["رحلتك", "الرحلة", "قصتك", "القصة", "صناعة", "الصناعة", "بدايتك", "البداية", "ازاي عملت", "كفاح", "الكفاح"]

# --- 3. وظائف الإرسال ---
def send_wa(chat_id, text):
    url = f"https://api.green-api.com/waInstance{G_ID}/sendMessage/{G_TOKEN}"
    try: requests.post(url, json={"chatId": chat_id, "message": text.replace('*', '')}, timeout=10)
    except: pass

# --- 4. مستقبل الويب هوك (Flask) ---
@app_web.route('/webhook', methods=['POST'])
def webhook_handler():
    data = request.json
    if data and data.get('typeWebhook') == 'incomingMessageReceived':
        body = data.get('body', {})
        sender_name = body['senderData']['senderName']
        sender_id = body['senderData']['chatId']
        msg_data = body.get('messageData', {})
        text = msg_data.get('textMessageData', {}).get('textMessage', '') or \
               msg_data.get('extendedTextMessageData', {}).get('text', '')

        report = (
            f"⚡️ **واتساب فوري**\n"
            f"👤 **المرسل:** {sender_name}\n"
            f"🆔 **الآيدي:** `{sender_id}`\n"
            f"💬 **النص:** {text}\n\n"
            f"🔄 *اسحب للرد اليدوي*"
        )
        requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage", 
                      json={"chat_id": MY_ID, "text": report, "parse_mode": "Markdown"})
    return "OK", 200

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app_web.run(host='0.0.0.0', port=port)

# --- 5. معالجة رسائل التليجرام ---
async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    user_id = update.effective_user.id
    msg_id = update.message.message_id

    if user_id == MY_ID:
        if update.message.reply_to_message:
            try:
                original = update.message.reply_to_message.text
                if "🆔" in original:
                    target_id = original.split("الآيدي:** `")[1].split("`")[0]
                    if "@c.us" in target_id:
                        send_wa(target_id, update.message.text)
                        await update.message.reply_text("✅ تم إرسال الرد للواتساب.")
                    else:
                        await context.bot.send_message(chat_id=int(target_id), text=update.message.text)
                        await update.message.reply_text("✅ تم إرسال الرد للتليجرام.")
            except: pass
        return

    else:
        # تنبيه لمحمد + رد تلقائي
        alert = f"🔔 **تليجرام جديد:**\n👤: {update.effective_user.first_name}\n🆔: `{user_id}`\n💬: {update.message.text}"
        await context.bot.send_message(chat_id=MY_ID, text=alert, parse_mode='Markdown')
        
        if any(k in text for k in ABOUT_KEYS) or any(k in text for k in JOURNEY_KEYS):
            await update.message.reply_text(ABOUT_REPLY, reply_to_message_id=msg_id, parse_mode='Markdown')
        elif any(k in text for k in HEALTH_KEYS):
            await update.message.reply_text("🌟 محمد بخير وفي أفضل حال، شكراً لسؤالك الراقي! ✨", reply_to_message_id=msg_id)
        elif any(k in text for k in STUDY_KEYS):
            await update.message.reply_text("📖 وضع المذاكرة (ثانية ثانوي) مفعل حالياً.. دعواتك لمحمد بالتوفيق! ⚡", reply_to_message_id=msg_id)
        else:
            await update.message.reply_text("وصلت رسالتك! محمد مشغول حالياً وسيرد عليك فور تفرغه. 💡", reply_to_message_id=msg_id)

# --- 6. التشغيل ---
if __name__ == '__main__':
    Thread(target=run_flask, daemon=True).start()
    app = ApplicationBuilder().token(TG_TOKEN).build()
    app.add_handler(CommandHandler("start", lambda u, c: u.message.reply_text(WELCOME_MSG, reply_to_message_id=u.message.message_id, parse_mode='Markdown')))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_messages))
    print("🚀 نسخة الكفاح v10.8 جاهزة للعمل السحابي!")
    app.run_polling()
