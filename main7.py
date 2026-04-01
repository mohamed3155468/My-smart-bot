import datetime
import requests
import time
import asyncio
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, CommandHandler

# --- 1. الويب سيرفر للبقاء أونلاين ---
app_web = Flask('')
@app_web.route('/')
def home(): return "🤖 Mohamed's Journey Bot is Live!"

def run_server(): app_web.run(host='0.0.0.0', port=8080)

# --- 2. إعدادات البوت والبيانات الشخصية ---
class BotConfig:
    TG_TOKEN = '8688241569:AAGh2U58zOExXRkfchZf_SnU2mfocfMorII'
    MY_ID = 7804212970
    G_ID = '7107571550'
    G_TOKEN = 'B65d1e96662e4f9db5f2df1d58faf2e67848787ccb924aa1b0'
    
    # رسالة التعريف المزخرفة (الرحلة)
    ABOUT_ME = (
        "✨ ━━━━━━━ ● ━━━━━━━ ✨\n"
        "👨‍💻 *بِطَاقَةُ التَّعْرِيفِ الخَاصَّةِ بِالمُطَوِّرِ*\n"
        "✨ ━━━━━━━ ● ━━━━━━━ ✨\n\n"
        "👤 **الاسم:** محمد (المبرمج محمد)\n"
        "🎓 **المستوى:** طالب ثانوي - مبرمج بايثون شغوف\n"
        "🚀 **رحلة البوت:** بدأت من فكرة بسيطة لتنظيم الوقت أثناء المذاكرة، "
        "وتطورت لتصبح جسراً ذكياً يربط بين الواتساب والتليجرام بكفاءة عالية.\n\n"
        "💡 *مبدئي في الحياة:*\n"
        "⚡️ « **العِلْمُ لَا يَعْرِفُ عُمْراً** » ⚡️\n\n"
        "🤖 تم تطوير هذا البوت ليكون مساعداً شخصياً ذكياً.\n"
        "✨ ━━━━━━━ ● ━━━━━━━ ✨"
    )

    AUTO_REPLY = True
    MESSAGES_COUNT = 0

# --- 3. القواميس الموسعة ---
HEALTH_KEYS = ["ازيك", "الازيك", "اخبارك", "الاخبار", "شلونك", "كيفك", "عامل ايه", "تمام", "بخير"]
STUDY_KEYS = ["مذاكرة", "المذاكرة", "تذاكر", "دراسة", "فيزياء", "فيزيا", "physics", "study"]
ABOUT_KEYS = ["انت مين", "إنت مين", "مين", "عنك", "المطور", "المبرمج", "حكايتك", "البوت", "عنك", "تعريف"]

# --- 4. محرك العمليات ---
def send_wa(chat_id, text):
    url = f"https://api.green-api.com/waInstance{BotConfig.G_ID}/sendMessage/{BotConfig.G_TOKEN}"
    try:
        requests.post(url, json={"chatId": chat_id, "message": text}, timeout=10)
    except: pass

def wa_monitor():
    recv_url = f"https://api.green-api.com/waInstance{BotConfig.G_ID}/receiveNotification/{BotConfig.G_TOKEN}"
    del_url = f"https://api.green-api.com/waInstance{BotConfig.G_ID}/deleteNotification/{BotConfig.G_TOKEN}"
    
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

                        # إرسال إشعار لمحمد
                        log = f"📩 **رسالة واتساب جديدة**\n👤: {sender_name}\n🆔: `{sender_id}`\n💬: {text}"
                        requests.post(f"https://api.telegram.org/bot{BotConfig.TG_TOKEN}/sendMessage", 
                                      json={"chat_id": BotConfig.MY_ID, "text": log, "parse_mode": "Markdown"})

                        # الردود التلقائية المزخرفة
                        if BotConfig.AUTO_REPLY:
                            low_text = text.lower()
                            
                            # الرد عن التعريف والرحلة
                            if any(k in low_text for k in ABOUT_KEYS):
                                send_wa(sender_id, BotConfig.ABOUT_ME.replace('*', '').replace('`', '')) # تنظيف الماركدوان للواتساب
                            
                            # الرد على الحال
                            elif any(k in low_text for k in HEALTH_KEYS):
                                send_wa(sender_id, "🌟 الحمد لله، مبرمجي بخير وبأفضل حال! شكراً لسؤالك الراقي. ✨\n\n« العلم لا يعرف عمراً » 💡")
                            
                            # الرد على المذاكرة
                            elif any(k in low_text for k in STUDY_KEYS):
                                send_wa(sender_id, "📖 وضع المذاكرة مفعل حالياً ⚡\nمحمد يذاكر الفيزياء (ثانية ثانوي).. سيعاود الاتصال بك فور انتهائه! ✍️")

                    requests.delete(f"{del_url}/{receipt_id}")
        except: time.sleep(1)

# --- 5. أوامر التليجرام ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != BotConfig.MY_ID: return
    await update.message.reply_text(BotConfig.ABOUT_ME, parse_mode="Markdown")

async def handle_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id == BotConfig.MY_ID and update.message.reply_to_message:
        original = update.message.reply_to_message.text
        if "🆔:" in original:
            wa_id = original.split("🆔: ")[1].split("\n")[0].strip()
            send_wa(wa_id, update.message.text)
            await update.message.reply_text("🚀 تم إرسال الرد بنجاح!")

# --- 6. التشغيل ---
if __name__ == '__main__':
    Thread(target=run_server, daemon=True).start()
    Thread(target=wa_monitor, daemon=True).start()
    
    app = ApplicationBuilder().token(BotConfig.TG_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_reply))
    
    print("🚀 البوت انطلق بقصة النجاح والزخرفة!")
    app.run_polling()
