import datetime
import requests
import time
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, CommandHandler

# --- 1. إعداد الويب سيرفر (UptimeRobot) ---
app_web = Flask('')
@app_web.route('/')
def home(): return "🤖 WhatsApp-Telegram Bridge is Online & Active!"

def run(): app_web.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

# --- 2. البيانات الخاصة بك ---
TELEGRAM_TOKEN = '8688241569:AAGh2U58zOExXRkfchZf_SnU2mfocfMorII'
MY_ID = 7804212970

# بيانات Green-API (تأكد من حالة Instance: Authorized في الموقع)
GREEN_ID = '7107571550' 
GREEN_TOKEN = 'B65d1e96662e4f9db5f2df1d58faf2e67848787ccb924aa1b0'

# --- 3. القاموس العملاق للكلمات المفتاحية ---
STUDY_KEYS = ["مذاكرة", "المذاكرة", "تذاكر", "التذاكر", "دراسة", "الدراسة", "تدرس", "التدريس", "فيزياء", "الفيزياء", "فيزيا", "الفيزيا", "ذاكر", "ادرس", "بتذاكر", "وراك ايه", "physics", "study", "الدرس", "دروس"]
DEV_KEYS = ["المطور", "مطور", "المبرمج", "مبرمج", "developer", "dev", "سواك", "عملك", "مين", "منو", "إنت مين", "عنك", "معلومات", "بطاقة", "قولي", "وريني", "صاحب البوت"]
TIME_KEYS = ["وقت", "الوقت", "ساعة", "الساعة", "مواعيد", "المواعيد", "امتى", "متى", "شوكت", "تفتح", "موجود", "اونلاين", "time", "ساعتك"]
HEALTH_KEYS = ["ازيك", "اخبارك", "أخبارك", "عامل", "شلونك", "كيفك", "حالك", "بخير", "طمني", "أخبار", "how are you", "يا نجم"]
THANKS_KEYS = ["شكرا", "الشكر", "تسلم", "يا بطل", "عاش", "أحسنت", "thanks", "جزاك الله خير"]

# --- 4. وظائف الإرسال والردود ---

def send_to_whatsapp(chat_id, text):
    """إرسال رسالة من التليجرام إلى الواتساب"""
    url = f"https://api.green-api.com/waInstance{GREEN_ID}/sendMessage/{GREEN_TOKEN}"
    payload = {"chatId": chat_id, "message": text}
    try:
        requests.post(url, json=payload, timeout=10)
    except: pass

def check_whatsapp_messages():
    """مراقب رسائل الواتساب (فردي + مجموعات)"""
    receive_url = f"https://api.green-api.com/waInstance{GREEN_ID}/receiveNotification/{GREEN_TOKEN}"
    delete_url = f"https://api.green-api.com/waInstance{GREEN_ID}/deleteNotification/{GREEN_TOKEN}"
    
    print("📡 جاري مراقبة رسائل الواتساب (فردي ومجموعات)...")
    
    while True:
        try:
            response = requests.get(receive_url, timeout=20).json()
            if response and 'body' in response:
                receipt_id = response['receiptId']
                body = response['body']
                type_webhook = body.get('typeWebhook')

                # التحقق من نوع الرسالة (فردي أو مجموعة)
                if type_webhook in ['incomingMessageReceived', 'incomingGroupMessageReceived']:
                    message_data = body.get('messageData', {})
                    text_msg = ""
                    
                    if 'textMessageData' in message_data:
                        text_msg = message_data['textMessageData'].get('textMessage', '')
                    elif 'extendedTextMessageData' in message_data:
                        text_msg = message_data['extendedTextMessageData'].get('text', '')

                    sender_data = body.get('senderData', {})
                    sender_id = sender_data.get('chatId')
                    sender_name = sender_data.get('senderName', 'شخص مجهول')
                    
                    # تحديد نوع الشات للإشعار
                    chat_type = "👤 فردي" if "@c.us" in sender_id else "👥 مجموعة"

                    # 1. إرسال الإشعار لمحمد على التليجرام
                    tg_notify = f"🟢 **رسالة واتساب ({chat_type})**\n👤: {sender_name}\n🆔: `{sender_id}`\n💬: {text_msg}"
                    requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", 
                                  json={"chat_id": MY_ID, "text": tg_notify, "parse_mode": "Markdown"})

                    # 2. الرد التلقائي الذكي بناءً على الكلمات المفتاحية
                    msg_lower = text_msg.lower()
                    if any(word in msg_lower for word in STUDY_KEYS):
                        send_to_whatsapp(sender_id, "📖 محمد حالياً بيذاكر فيزياء (تانية ثانوي محتاجة تركيز).. هيرد عليك أول ما يخلص دراسته! ✨")
                    elif any(word in msg_lower for word in DEV_KEYS):
                        send_to_whatsapp(sender_id, "👨‍💻 أنا بوت المبرمج محمد، طالب ومطور بايثون مصري. صُنعت لتنظيم الرسايل وقت المذاكرة.")
                    elif any(word in msg_lower for word in TIME_KEYS):
                        send_to_whatsapp(sender_id, "🕒 المبرمج متاح غالباً بعد 9 مساءً. اترك رسالتك هنا وسيقرأها لاحقاً.")
                    elif any(word in msg_lower for word in HEALTH_KEYS):
                        send_to_whatsapp(sender_id, "مبرمجي بخير والحمد لله، شكراً لسؤالك الراقي! 😊")
                    elif any(word in msg_lower for word in THANKS_KEYS):
                        send_to_whatsapp(sender_id, "العفو! تحت أمرك دايماً. 🤖")

                # حذف الإشعار لضمان عدم التكرار
                requests.delete(f"{delete_url}/{receipt_id}")
        except:
            time.sleep(1)

# --- 5. أوامر التليجرام (الرد اليدوي) ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"أهلاً يا مبرمج محمد! 🤖\nجسر الواتساب يعمل الآن للفردي والمجموعات.\nللرد: اعمل Reply على رسالة البوت.")

async def handle_tg_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    text = update.message.text

    # نظام الرد العكسي من التليجرام للواتساب
    if user.id == MY_ID and update.message.reply_to_message:
        reply_text = update.message.reply_to_message.text
        if "🆔:" in reply_text:
            try:
                wa_chat_id = reply_text.split("🆔: ")[1].split("\n")[0].strip()
                send_to_whatsapp(wa_chat_id, text)
                await update.message.reply_text(f"✅ تم إرسال ردك للواتساب بنجاح.")
                return
            except: pass

    await update.message.reply_text("استلمت رسالتك على التليجرام!")

# --- 6. تشغيل المحركات ---
if __name__ == '__main__':
    keep_alive() # تشغيل Flask للبقاء أونلاين
    
    # تشغيل مراقب الواتساب في Thread مستقل
    wa_thread = Thread(target=check_whatsapp_messages)
    wa_thread.daemon = True
    wa_thread.start()
    
    # تشغيل بوت التليجرام
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_tg_message))
    
    print("🚀 الانطلاق! البوت يراقب الفردي والمجموعات الآن.")
    app.run_polling()
