import requests
import time
import asyncio
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, CommandHandler

# --- 1. سيرفر البقاء (Keep Alive) ---
app_web = Flask('')
@app_web.route('/')
def home(): return "🤖 Mohamed's Pro Bridge is ACTIVE!"

def run_server():
    app_web.run(host='0.0.0.0', port=8080)

# --- 2. البيانات والبطاقة التعريفية ---
class BotConfig:
    # ⚠️ حط التوكن الجديد بتاعك هنا ⚠️
    TG_TOKEN = '8637053407:AAELVpuwoMtPh0n1ekNOdMf0V6WM6F4lOKk'
    MY_ID = 7804212970
    
    # بيانات Green-API ثابتة
    G_ID = '7107571550'
    G_TOKEN = 'B65d1e96662e4f9db5f2df1d58faf2e67848787ccb924aa1b0'
    
    # بطاقة الرحلة المزخرفة
    INFO_CARD = (
        "✨ ━━━━━━━ ● ━━━━━━━ ✨\n"
        "👨‍💻 *بِطَاقَةُ تَعْرِيفِ المُطَوِّرِ وَالرِّحْلَةِ*\n"
        "✨ ━━━━━━━ ● ━━━━━━━ ✨\n\n"
        "👤 **الاسم:** محمد (المبرمج محمد)\n"
        "🎓 **المستوى:** طالب ثانوي - مبرمج بايثون\n"
        "🚀 **البداية:** بدأت الرحلة بشغف لتعلم البرمجة وتطويعها لخدمة العلم.\n"
        "🤖 **عن البوت:** صُنع هذا المحرك ليكون مساعداً ذكياً ينظم التواصل وقت المذاكرة.\n\n"
        "💡 *حكمة الرحلة:*\n"
        "⚡️ « **العِلْمُ لَا يَعْرِفُ عُمْراً** » ⚡️\n\n"
        "📈 *الإنجاز:* تم ربط التليجرام بالواتساب بنجاح لضمان عدم ضياع أي معلومة.\n"
        "✨ ━━━━━━━ ● ━━━━━━━ ✨"
    )

    AUTO_REPLY = True
    MESSAGES_COUNT = 0

# --- 3. قواميس الكلمات الدلالية الشاملة ---
HEALTH_KEYS = [
    "ازيك", "الازيك", "اخبارك", "الاخبار", "أخبارك", "الأخبار", "عامل", "العامل", "عامله", "كيفك", "الكيف", 
    "شلونك", "الشلون", "شحالك", "الشحال", "تمام", "التمام", "بخير", "البخير", "كويس", "الكويس", "طمني", 
    "أحوالك", "الأحوال", "احوالك", "الاحوال", "صحتك", "الصحة", "الصحه", "الأمور", "الامور", "امورك"
]

STUDY_KEYS = [
    "مذاكرة", "المذاكرة", "تذاكر", "التذاكر", "دراسة", "الدراسة", "تدرس", "فيزياء", "الفيزياء", 
    "فيزيا", "الفيزيا", "دروس", "الدروس", "درس", "الدرس", "physics", "study"
]

ABOUT_KEYS = [
    "انت مين", "إنت مين", "مين", "عنك", "المطور", "المبرمج", "حكايتك", "البوت", "تعريف", "البطاقة", "البطاقه"
]

# --- 4. محرك العمليات ---
def send_wa(chat_id, text):
    url = f"https://api.green-api.com/waInstance{BotConfig.G_ID}/sendMessage/{BotConfig.G_TOKEN}"
    try:
        # تنظيف النص من الماركدوان قبل إرساله للواتساب
        clean_text = text.replace('*', '').replace('`', '').replace('_', '')
        requests.post(url, json={"chatId": chat_id, "message": clean_text}, timeout=10)
    except: pass

def wa_monitor():
    recv_url = f"https://api.green-api.com/waInstance{BotConfig.G_ID}/receiveNotification/{BotConfig.G_TOKEN}"
    del_url = f"https://api.green-api.com/waInstance{BotConfig.G_ID}/deleteNotification/{BotConfig.G_TOKEN}"
    
    print("📡 [System] مراقب الواتساب يعمل بالتوكن الجديد الآن..")
    
    while True:
        try:
            response = requests.get(recv_url, timeout=15)
            if response.status_code == 200:
                data = response.json()
                if data and 'body' in data:
                    receipt_id = data['receiptId']
                    body = data['body']
                    
                    if body.get('typeWebhook') in ['incomingMessageReceived', 'incomingGroupMessageReceived']:
                        BotConfig.MESSAGES_COUNT += 1
                        msg_data = body.get('messageData', {})
                        text = msg_data.get('textMessageData', {}).get('textMessage', '') or \
                               msg_data.get('extendedTextMessageData', {}).get('text', '')
                        
                        sender_name = body['senderData']['senderName']
                        sender_id = body['senderData']['chatId']

                        # تحويل للتليجرام (نص بسيط لضمان الوصول)
                        log = f"📩 رسالة جديدة\n👤 من: {sender_name}\n🆔: {sender_id}\n💬 النص: {text}"
                        requests.post(f"https://api.telegram.org/bot{BotConfig.TG_TOKEN}/sendMessage", 
                                      json={"chat_id": BotConfig.MY_ID, "text": log})

                        # الردود التلقائية
                        if BotConfig.AUTO_REPLY:
                            low_text = text.lower()
                            
                            if any(k in low_text for k in ABOUT_KEYS):
                                send_wa(sender_id, BotConfig.INFO_CARD)
                            
                            elif any(k in low_text for k in HEALTH_KEYS):
                                send_wa(sender_id, "🌟 الحمد لله، مبرمجي محمد بخير وبأفضل حال! شكراً لسؤالك الراقي. ✨\n\n« العلم لا يعرف عمراً » 💡")
                            
                            elif any(k in low_text for k in STUDY_KEYS):
                                send_wa(sender_id, "📖 وضع المذاكرة (ثانية ثانوي) مفعل حالياً ⚡\nمحمد يذاكر الفيزياء الآن.. سيعاود الاتصال بك فور انتهائه! ✍️")

                    requests.delete(f"{del_url}/{receipt_id}")
        except: time.sleep(1)

# --- 5. أوامر التليجرام ---

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != BotConfig.MY_ID: return
    await update.message.reply_text(BotConfig.INFO_CARD, parse_mode="Markdown")

async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != BotConfig.MY_ID: return
    status_msg = (
        f"📊 **إحصائيات البوت:**\n\n"
        f"✅ الحالة: متصل وسليم\n"
        f"📩 رسائل اليوم: {BotConfig.MESSAGES_COUNT}\n"
        f"⚙️ الرد التلقائي: فعّال 🟢"
    )
    await update.message.reply_text(status_msg, parse_mode="Markdown")

async def reply_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id == BotConfig.MY_ID and update.message.reply_to_message:
        try:
            original = update.message.reply_to_message.text
            wa_id = original.split("🆔: ")[1].split("\n")[0].strip()
            send_wa(wa_id, update.message.text)
            await update.message.reply_text("🚀 تم إرسال الرد للواتساب.")
        except:
            await update.message.reply_text("❌ مشكلة في استخراج آيدي المستلم.")

# --- 6. التشغيل النهائي ---
if __name__ == '__main__':
    Thread(target=run_server, daemon=True).start()
    Thread(target=wa_monitor, daemon=True).start()
    
    print("🚀 انطلق يا بطل! البوت يعمل الآن بالتوكن الجديد.")
    bot_app = ApplicationBuilder().token(BotConfig.TG_TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start_cmd))
    bot_app.add_handler(CommandHandler("status", status_cmd))
    bot_app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), reply_handler))
    bot_app.run_polling()
