import time
import os
from threading import Thread
from flask import Flask
from whatsapp_api_client_python import API

# --- إعداد السيرفر الوهمي (Flask) لضمان استمرار العمل على Replit ---
app = Flask('')

@app.route('/')
def home():
    return "✅ Bot is Running 24/7!"

def run_web_server():
    # ريبلت بيحتاج بورت 8080 عشان الـ Deployment ينجح
    app.run(host='0.0.0.0', port=8080)

# --- بيانات الاعتماد الخاصة بك ---
ID_INSTANCE = "7107571550" 
API_TOKEN_INSTANCE = "57cd9401766049c895941419144969012d6be4687d4241deae"

# ربط المكتبة بالسيرفر
greenAPI = API.GreenApi(ID_INSTANCE, API_TOKEN_INSTANCE)
welcomed_users = set()

# --- القاموس الخاص بالردود المزخرفة (بدون أي تغيير) ---
RESOURCES = {
    "1": (
        "🏗️ *┃ مـحـطـة الـتـأسـيـس والـبـنـاء* ┃\n"
        "━━━━━━━━━━━━━━━\n\n"
        "💡 *خلف الكواليس:*\n"
        "تم تطوير هذا النظام ليكون رفيقك الذكي، حيث يعتمد كلياً على لغة *Python* القوية مع تكامل متطور لخدمات الـ *Cloud APIs*.\n\n"
        "🛡️ *الهدف الرئيسي:*\n"
        "خلق تجربة تواصل فريدة وسريعة تلبي احتياجاتك في أجزاء من الثانية.\n\n"
        "✨ _شكرًا لاهتمامك بمعرفة البدايات!_"
    ),
    "2": (
        "⚡ *┃ الـتـرسـانـة الـتـقـنـيـة* ┃\n"
        "━━━━━━━━━━━━━━━\n\n"
        "🖥️ *Environment:* Android Termux\n"
        "🐍 *Engine:* Python 3.10+\n"
        "🌐 *Protocol:* Green-API Gateway\n"
        "⚙️ *الحالة:* جميع الأنظمة تعمل بكفاءة *100%*."
    ),
    "3": (
        "🚀 *┃ رُؤيـة الـمُـسـتـقـبـل* ┃\n"
        "━━━━━━━━━━━━━━━\n\n"
        "تطلعاتنا لا تتوقف عند هذا الحد، نحن نعمل الآن على:\n\n"
        "🧠 دمج الـ *AI* (الذكاء الاصطناعي) للرد الذكي.\n"
        "📊 نظام تحليل بيانات الرسائل والردود.\n\n"
        "📈 *ترقبوا التحديثات القادمة!*"
    ),
    "4": (
        "📩 *┃ بـوابـة الـتـواصـل الـمُـبـاشـر* ┃\n"
        "━━━━━━━━━━━━━━━\n\n"
        "لقد وصلت إلى قسم الرسائل الخاصة بـ *محمد*.\n\n"
        "⏳ *حالة محمد الآن:* في وضع التطوير والإبداع 👨‍💻🔥\n\n"
        "✉️ *اترك رسالتك الآن* بكل وضوح، وسيتم تنبيه محمد فوراً للرد عليك بمجرد تفرغه.\n\n"
        "✨ _نحن نقدر وقتك جداً!_"
    )
}

WELCOME_MSG = (
    "👋 *أهلاً بك في فضاء محمد البرمجي* ✨\n"
    "━━━━━━━━━━━━━━━\n\n"
    "أنا مساعدك الآلي المتطور 🤖، يسعدني جداً اهتمامك بالتواصل معنا.\n\n"
    "للحصول على أفضل تجربة، اختر وجهتك من القائمة:\n\n"
    "1️⃣ ↫ 🏗️ *قـصـة الـتـأسـيـس*\n"
    "2️⃣ ↫ ⚡ *الـعـتـاد والـتـقـنـيـة*\n"
    "3️⃣ ↫ 🚀 *رؤيـة الـتـطـويـر*\n"
    "4️⃣ ↫ 📞 *تـواصـل مـبـاشـر*\n\n"
    "━━━━━━━━━━━━━━━\n"
    "⌨️ *فقط أرسل رقم القسم المراد استكشافه*"
)

BUSY_MSG = (
    "⌛ *نحن نقوم بمعالجة طلبك..*\n"
    "━━━━━━━━━━━━━━━\n"
    "عذراً، يبدو أن محمد مشغول حالياً 👨‍💻.\n\n"
    "✅ تم استلام رسالتك بنجاح.\n"
    "💡 يمكنك الاستمرار في استخدام القائمة أو انتظار الرد."
)

def start_bot():
    print("🚀 [System] البوت بدأ العمل ومراقب جيداً للرسائل بالزخارف الكاملة...")
    
    while True:
        try:
            # استلام الإشعارات من السيرفر
            receive_dict = greenAPI.receiveNotification()
            if receive_dict and receive_dict.value:
                payload = receive_dict.value
                type_webhook = payload.get('typeWebhook')
                
                print(f"📡 إشعار جديد وصل: {type_webhook}")

                if type_webhook == 'incomingMessageReceived':
                    chat_id = payload['senderData']['chatId']
                    user_msg = ""
                    msg_data = payload.get('messageData', {})
                    
                    if msg_data.get('typeMessage') == 'textMessage':
                        user_msg = msg_data.get('textMessageData', {}).get('text', '').strip()
                    elif msg_data.get('typeMessage') == 'extendedTextMessage':
                        user_msg = msg_data.get('extendedTextMessageData', {}).get('text', '').strip()
                    
                    print(f"💬 رسالة من {chat_id}: {user_msg}")

                    # معالجة الردود
                    if user_msg in RESOURCES:
                        reply = RESOURCES[user_msg]
                    elif chat_id not in welcomed_users:
                        reply = WELCOME_MSG
                        welcomed_users.add(chat_id)
                    else:
                        reply = BUSY_MSG

                    greenAPI.sending.sendMessage(chat_id, reply)
                    print(f"✅ تم الرد بنجاح على {chat_id}")

                greenAPI.deleteNotification(payload['receiptId'])
        
        except Exception as e:
            print(f"⚠️ خطأ أثناء التشغيل: {e}")
            time.sleep(2)

if __name__ == '__main__':
    # 1. تشغيل السيرفر الوهمي في خيط (Thread) منفصل
    server_thread = Thread(target=run_web_server)
    server_thread.start()
    
    # 2. تشغيل محرك البوت الأساسي
    start_bot()
