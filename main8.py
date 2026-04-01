import requests
import time
import asyncio
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, CommandHandler

# --- 1. الويب سيرفر (عشان يفضل صاحي 24 ساعة) ---
app_web = Flask('')
@app_web.route('/')
def home(): return "🤖 Mohamed's PRO Bot is Running!"

def run_server():
    app_web.run(host='0.0.0.0', port=8080)

# --- 2. الإعدادات والبيانات ---
class BotConfig:
    TG_TOKEN = '8688241569:AAGh2U58zOExXRkfchZf_SnU2mfocfMorII'
    MY_ID = 7804212970
    G_ID = '7107571550'
    G_TOKEN = 'B65d1e96662e4f9db5f2df1d58faf2e67848787ccb924aa1b0'
    
    # رسالة التعريف المزخرفة
    ABOUT_ME = (
        "✨ ━━━━━━━ ● ━━━━━━━ ✨\n"
        "👨‍💻 *بِطَاقَةُ التَّعْرِيفِ المُنَظَّمَةِ*\n"
        "✨ ━━━━━━━ ● ━━━━━━━ ✨\n\n"
        "👤 **المطور:** محمد (المبرمج الشاب)\n"
        "📚 **التخصص:** طالب ثانوي - مبرمج بايثون\n"
        "🛠 **الوظيفة:** تنظيم رسائل الواتساب آلياً\n\n"
        "⚡️ « **العِلْمُ لَا يَعْرِفُ عُمْراً** » ⚡️\n\n"
        "🚀 بدأت رحلتي من الصفر، واليوم أصنع جسراً ذكياً للتواصل.\n"
        "✨ ━━━━━━━ ● ━━━━━━━ ✨"
    )

    AUTO_REPLY = True
    MESSAGES_COUNT = 0

# --- 3. قواميس الكلمات الدلالية (القاموس الشامل) ---
HEALTH_KEYS = [
    "ازيك", "الازيك", "إزيك", "اخبارك", "الاخبار", "أخبارك", "عامل ايه", "العامل", "شلونك", "الشلون", 
    "كيفك", "الكيف", "تمام", "التمام", "بخير", "البخير", "طمني", "صحتك", "علومك", "امورك"
]

STUDY_KEYS = ["مذاكرة", "المذاكرة", "تذاكر", "دراسة", "الدراسة", "فيزياء", "فيزيا", "physics", "study"]

ABOUT_KEYS = ["انت مين", "مين", "عنك", "المطور", "المبرمج", "حكايتك", "تعريف"]

# --- 4. محرك العمليات الأساسي ---
def send_wa(chat_id, text):
    url = f"https://api.green-api.com/waInstance{BotConfig.G_ID}/sendMessage/{BotConfig.G_TOKEN}"
    try:
        requests.post(url, json={"chatId": chat_id, "message": text}, timeout=10)
    except: pass

def wa_monitor():
    recv_url = f"https://api.green-api.com/waInstance{BotConfig.G_ID}/receiveNotification/{BotConfig.G_TOKEN}"
    del_url = f"https://api.green-api.com/waInstance{BotConfig.G_ID}/deleteNotification/{BotConfig.G_TOKEN}"
    
    print("📡 [System] المحرك يعمل وجاري جلب الرسائل...")
    
    while True:
        try:
            r = requests.get(recv_url, timeout=20)
            if r.status_code == 200:
                data = r.json()
                if data and 'body' in data:
                    receipt_id = data['receiptId']
                    body = data['body']
                    
                    if body.get('typeWebhook') in ['incomingMessageReceived', 'incomingGroupMessageReceived']:
                        BotConfig.MESSAGES_COUNT += 1
                        msg_data = body.get('messageData', {})
                        text = msg_data.get('textMessageData', {}).get('textMessage', '') or \
                               msg_data.get('extendedTextMessageData', {}).get('text', '')
                        
                        sender_id = body['senderData']['chatId']
                        sender_name = body['senderData']['senderName']

                        # تحويل الرسالة للتليجرام (بدون رموز معقدة لضمان الوصول)
                        log = f"📩 رسالة واتساب\n👤: {sender_name}\n🆔: {sender_id}\n💬: {text}"
                        requests.post(f"https://api.telegram.org/bot{BotConfig.TG_TOKEN}/sendMessage", 
                                      json={"chat_id": BotConfig.MY_ID, "text": log})

                        # نظام الردود التلقائية المزخرفة
                        if BotConfig.AUTO_REPLY:
                            low_text = text.lower()
                            
                            if any(k in low_text for k in ABOUT_KEYS):
                                clean_about = BotConfig.ABOUT_ME.replace('*', '').replace('_', '')
                                send_wa(sender_id, clean_about)
                            
                            elif any(k in low_text for k in HEALTH_KEYS):
                                send_wa(sender_id, "🌟 الحمد لله، مبرمجي محمد بخير وبأحسن حال! شكراً لسؤالك الذوق. ✨\n\n« العلم لا يعرف عمراً »")
                            
                            elif any(k in low_text for k in STUDY_KEYS):
                                send_wa(sender_id, "📖 وضع المذاكرة (ثانية ثانوي) مفعل حالياً ⚡\nمحمد يذاكر الفيزياء الآن.. سيعاود الاتصال بك لاحقاً! ✍️")

                    requests.delete(f"{del_url}/{receipt_id}")
        except: time.sleep(1)

# --- 5. أوامر لوحة التحكم (تليجرام) ---

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != BotConfig.MY_ID: return
    await update.message.reply_text(BotConfig.ABOUT_ME, parse_mode="Markdown")

async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != BotConfig.MY_ID: return
    msg = f"📊 **إحصائيات البوت:**\n\n✅ الحالة: متصل\n📩 رسائل اليوم: {BotConfig.MESSAGES_COUNT}\n⚙️ الرد التلقائي: شغّال"
    await update.message.reply_text(msg, parse_mode="Markdown")

async def handle_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """الرد اليدوي على الواتساب عبر التليجرام"""
    if update.message.from_user.id == BotConfig.MY_ID and update.message.reply_to_message:
        try:
            original_text = update.message.reply_to_message.text
            # استخراج الآيدي من الرسالة المحولة
            wa_id = original_text.split("🆔: ")[1].split("\n")[0].strip()
            send_wa(wa_id, update.message.text)
            await update.message.reply_text("🚀 تم الإرسال للواتساب.")
        except:
            await update.message.reply_text("❌ لم أستطع تحديد آيدي المستلم.")

# --- 6. تشغيل النظام بالكامل ---
if __name__ == '__main__':
    # تشغيل السيرفر والمراقب في الخلفية
    Thread(target=run_server, daemon=True).start()
    Thread(target=wa_monitor, daemon=True).start()
    
    # تشغيل بوت التليجرام
    app = ApplicationBuilder().token(BotConfig.TG_TOKEN).build()
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("status", status_cmd))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_reply))
    
    print("🚀 تم تفعيل النسخة الشاملة يا محمد! جرب الآن.")
    app.run_polling()
