import requests
import time
from threading import Thread
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# --- 1. إعدادات الهوية (بيانات المبرمج محمد) ---
TG_TOKEN = '8637053407:AAELVpuwoMtPh0n1ekNOdMf0V6WM6F4lOKk' 
MY_ID = 7804212970 

# بيانات Green-API 
G_ID = '7107571550'
G_TOKEN = 'B65d1e96662e4f9db5f2df1d58faf2e67848787ccb924aa1b0'

# --- 2. النصوص والرسائل المزخرفة (الإصدار العاشر - القصة الكاملة) ---

WELCOME_MSG = (
    "👑 **مرحباً بك في عالم المبرمج محمد الذكي** 👑\n"
    "✨ ━━━━━━━ ● ━━━━━━━ ✨\n\n"
    "🤖 **أنا المساعد الرقمي لمحمد.**\n"
    "أقوم بنقل رسائل الواتساب والتليجرام وتنظيمها بذكاء.\n\n"
    "🚀 **استكشف الآن:**\n"
    "🔹 [ معلوماتك ] | 🔹 [ حالتك ]\n"
    "🔹 [ رحلتك ] | 🔹 [ المذاكرة ]\n\n"
    "✨ ━━━━━━━ ● ━━━━━━━ ✨"
)

ABOUT_REPLY = (
    "👨‍💻 **سِجِلُّ المُمَبرمجِ مُحَمَّد (التفاصيل الكاملة)**\n"
    "✨ ━━━━━━━ ● ━━━━━━━ ✨\n\n"
    "👤 **مَن هو محمد؟**\n"
    "طالب مبدع بالصف الثاني الثانوي (علمي)، مبرمج متخصص في لغة البايثون، يعشق الأتمتة ويسعى لتبسيط التواصل الرقمي.\n\n"
    "🛣 **قصة كفاح صناعة البوت:**\n"
    "بدأت الرحلة من الصفر، لم تكن مجرد سطور كود بل كانت تحدياً ذاتياً. واجه محمد صعوبات في فهم الـ APIs وكيفية ربط السيرفرات ببعضها.\n\n"
    "🔍 **التفاصيل التقنية للرحلة:**\n"
    "1️⃣ **البداية:** تعلم أساسيات لغة Python والتعامل مع المكتبات البرمجية.\n"
    "2️⃣ **التحدي الأول:** ربط مكتبة `Telebot` و `Pyrogram` لبناء عقل البوت في تليجرام.\n"
    "3️⃣ **الجسر الذكي:** استخدام تقنية **Green API** لكسر حواجز الواتساب وتوجيه الرسائل.\n"
    "4️⃣ **الأتمتة:** برمجة نظام الرد التلقائي ليقوم بالرد بالنيابة عن محمد أثناء أوقات المذاكرة المكثفة.\n"
    "5️⃣ **الانطلاق السحابي:** ختام الرحلة كان برفع البوت وكامل الملفات على سيرفر سحابي (Cloud Server) لضمان العمل على مدار الساعة دون انقطاع، مما جعل البوت جسراً حقيقياً ومستقراً للتواصل.\n\n"
    "📚 **الهدف الحالي:** التوفيق بين رحلتي البرمجية ودراستي للفيزياء والرياضيات لبناء مستقبل تقني مشرق.\n\n"
    "💡 **الحكمة:** « العِلْمُ لَا يَعْرِفُ عُمْراً » ⚡️\n"
    "✨ ━━━━━━━ ● ━━━━━━━ ✨"
)

# القواميس (بألف ولام وبدونها)
HEALTH_KEYS = ["ازيك", "الازيك", "عامل ايه", "حالتك", "الحالة", "بخير", "اخبارك", "الاخبار"]
STUDY_KEYS = ["مذاكرة", "المذاكرة", "تذاكر", "التذاكر", "دراسة", "الدراسة", "فيزياء", "الفيزياء", "فيزيا", "physics"]
ABOUT_KEYS = ["انت مين", "إنت مين", "معلوماتك", "المعلومات", "عنك", "ملفك", "المطور", "المبرمج"]
JOURNEY_KEYS = ["رحلتك", "الرحلة", "قصتك", "القصة", "صناعة", "الصناعة", "بدايتك", "البداية", "ازاي عملت"]

# --- 3. وظائف الواتساب ---

def send_wa(chat_id, text):
    url = f"https://api.green-api.com/waInstance{G_ID}/sendMessage/{G_TOKEN}"
    clean_text = text.replace('*', '').replace('_', '')
    try: requests.post(url, json={"chatId": chat_id, "message": clean_text}, timeout=10)
    except: pass

def wa_monitor():
    recv_url = f"https://api.green-api.com/waInstance{G_ID}/receiveNotification/{G_TOKEN}"
    del_url = f"https://api.green-api.com/waInstance{G_ID}/deleteNotification/{G_TOKEN}"
    
    while True:
        try:
            response = requests.get(recv_url, timeout=15)
            if response.status_code == 200:
                data = response.json()
                if data and 'body' in data:
                    receipt_id = data['receiptId']
                    body = data['body']
                    if body.get('typeWebhook') in ['incomingMessageReceived', 'incomingGroupMessageReceived']:
                        msg_data = body.get('messageData', {})
                        text = msg_data.get('textMessageData', {}).get('textMessage', '') or \
                               msg_data.get('extendedTextMessageData', {}).get('text', '')
                        
                        sender_name = body['senderData']['senderName']
                        sender_id = body['senderData']['chatId']

                        report = (
                            f"📩 **رسالة واتساب جديدة**\n"
                            f"👤 **المرسل:** {sender_name}\n"
                            f"🆔 **الآيدي:** `{sender_id}`\n"
                            f"💬 **النص:** {text}\n\n"
                            f"🔄 *اسحب هذه الرسالة (Reply) للرد يدوياً.*"
                        )
                        requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage", 
                                      json={"chat_id": MY_ID, "text": report, "parse_mode": "Markdown"})

                    requests.delete(f"{del_url}/{receipt_id}")
        except: time.sleep(1)

# --- 4. وظائف التليجرام ---

async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    msg_id = update.message.message_id

    # أولاً: لو أنت (المبرمج محمد) اللي بتبعت رد (Reply)
    if user_id == MY_ID:
        if update.message.reply_to_message:
            try:
                original_text = update.message.reply_to_message.text
                if "الآيدي" in original_text:
                    parts = original_text.split("الآيدي")
                    target_id = parts[1].split("\n")[0].replace(":", "").replace("*", "").replace("`", "").strip()
                    
                    if "@c.us" in target_id: # رد للواتساب
                        send_wa(target_id, update.message.text)
                        await update.message.reply_text("✅ تم إرسال الرد للواتساب.", reply_to_message_id=msg_id)
                    else: # رد للتليجرام
                        await context.bot.send_message(chat_id=int(target_id), text=update.message.text)
                        await update.message.reply_text("✅ تم إرسال الرد للتليجرام.", reply_to_message_id=msg_id)
            except Exception as e:
                await update.message.reply_text(f"⚠️ خطأ في التوجيه: {e}", reply_to_message_id=msg_id)
        return

    # ثانياً: لو مستخدم تليجرام بيكلم البوت (تنبيه لك + رد تلقائي)
    else:
        report = (
            f"📩 **رسالة تليجرام جديدة**\n"
            f"👤 **المرسل:** {user_name}\n"
            f"🆔 **الآيدي:** `{user_id}`\n"
            f"💬 **النص:** {update.message.text}\n\n"
            f"🔄 *اسحب هذه الرسالة (Reply) للرد يدوياً.*"
        )
        await context.bot.send_message(chat_id=MY_ID, text=report, parse_mode='Markdown')

        if any(k in text for k in ABOUT_KEYS) or any(k in text for k in JOURNEY_KEYS):
            await update.message.reply_text(ABOUT_REPLY, reply_to_message_id=msg_id, parse_mode='Markdown')
        elif any(k in text for k in HEALTH_KEYS):
            await update.message.reply_text("🌟 محمد بخير، شكراً لسؤالك الراقي! ✨", reply_to_message_id=msg_id)
        elif any(k in text for k in STUDY_KEYS):
            await update.message.reply_text("📖 وضع المذاكرة مفعل.. محمد يذاكر الفيزياء حالياً. ⚡", reply_to_message_id=msg_id)
        else:
            await update.message.reply_text("وصلت رسالتك! محمد مشغول حالياً وسيرد عليك لاحقاً. 💡", reply_to_message_id=msg_id)

# --- 5. التشغيل ---
if __name__ == '__main__':
    Thread(target=wa_monitor, daemon=True).start()
    app = ApplicationBuilder().token(TG_TOKEN).build()
    app.add_handler(CommandHandler("start", lambda u, c: u.message.reply_text(WELCOME_MSG, reply_to_message_id=u.message.message_id, parse_mode='Markdown')))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_messages))
    print("🚀 نسخة القصة الكاملة v10.2 مع تحديث الرحلة السحابية تعمل بنجاح!")
    app.run_polling()
