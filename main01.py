from whatsapp_api_client_python import API
import time

# بياناتك الخاصة من Green-API
ID_INSTANCE = '7107571550'
API_TOKEN_INSTANCE = '57cd9401766049c895941419144969012d6be4687d4241deae'

greenAPI = API.GreenApi(ID_INSTANCE, API_TOKEN_INSTANCE)

# قاموس لحفظ وقت آخر رسالة ترحيب لكل مستخدم (بالثواني)
user_sessions = {}

def main():
    print("🚀 فضاء محمد البرمجي يعمل الآن بنظام الذاكرة السحابية...")
    
    while True:
        try:
            notifications = greenAPI.receiving.receiveNotification()
            if notifications.data:
                res = notifications.data
                receipt_id = res.get('receiptId')
                body = res.get('body', {})
                
                if body.get('typeWebhook') == 'incomingMessageReceived':
                    chat_id = body.get('senderData', {}).get('chatId')
                    message_data = body.get('messageData', {})
                    
                    if 'textMessageData' in message_data:
                        user_text = message_data['textMessageData'].get('textMessage', '').strip()
                        current_time = time.time()

                        # --- النصوص الكاملة كما طلبتها ---
                        welcome_msg = (
                            "👋 أهلاً بك في فضاء محمد البرمجي ✨\n"
                            "━━━━━━━━━━━━━━━\n"
                            "أنا مساعدك الآلي المتطور 🤖.\n"
                            "اختر وجهتك:\n"
                            "1️⃣ ↫ 🏗️ قـصـة الـتـأسـيـس\n"
                            "2️⃣ ↫ ⚡ الـعـتـاد والـتـقـنـيـة\n"
                            "3️⃣ ↫ 🚀 رؤيـة الـتـطـويـر\n"
                            "4️⃣ ↫ 📞 تـواصـل مـبـاشـر\n"
                            "━━━━━━━━━━━━━━━\n"
                            "⌨️ فقط أرسل رقم القسم المراد استكشافه"
                        )

                        alert_msg = (
                            "🛡️ ┃ تـنـبـيـه نـظـام الـمُـبـرمـج ┃\n"
                            "━━━━━━━━━━━━━━━\n"
                            "✅ تـم اسـتـلام رسـالـتـك بـنـجـاح\n"
                            "💬 وصلت كلماتك الآن إلى مبرمجي الشخصي، وهو يعمل حالياً في بيئة التطوير 👨‍💻🔥.\n"
                            "⏳ سـيـتـم الـرد عـلـيـك: في أقرب وقت ممكن بمجرد التفرغ.\n"
                            "━━━━━━━━━━━━━━━\n"
                            "✨ شكرًا لانتظارك وتفهمك!\n"
                            "✨ان لم يتم الرد عليك في أقرب وقت\n"
                            "✨أو كنت في استعجال يمكنك مراسلت مبمرجي\n"
                            "✨في تليجرام ابحث عن\n"
                            " @MOHAMED4358bot✨\n"
                            "✨وابدا بالمراسله"
                        )

                        # --- منطق الردود المطور ---
                        
                        # الحصول على وقت آخر ترحيب لهذا المستخدم (0 إذا كان أول مرة)
                        last_welcome_time = user_sessions.get(chat_id, 0)

                        # الحالة 1: إرسال رسالة الترحيب لأول مرة أو بعد مرور 30 دقيقة
                        if current_time - last_welcome_time > 1800: # 1800 ثانية = 30 دقيقة
                            greenAPI.sending.sendMessage(chat_id, welcome_msg)
                            user_sessions[chat_id] = current_time
                            
                            # إذا كانت أول رسالة "رقم"، نكمل لنرسل له القسم أيضاً
                            # إذا لم تكن "رقم"، نكتفي بالترحيب ونحذف الإشعار
                            if user_text not in ["1", "2", "3", "4"]:
                                greenAPI.receiving.deleteNotification(receipt_id)
                                continue

                        # الحالة 2: الرد على الأوامر (1، 2، 3، 4)
                        if user_text == "1":
                            response = "🏗️ ┃ مـحـطـة الـتـأسـيـس والـبـنـاء ┃\n━━━━━━━━━━━━━━━\n💡 خلف الكواليس: تم تطوير هذا النظام ليكون رفيقك الذكي، يعتمد كلياً على لغة Python.\n✨ شكرًا لاهتمامك بمعرفة البدايات!"
                        elif user_text == "2":
                            response = "⚡ ┃ الـتـرسـانـة الـتـقـنـيـة ┃\n━━━━━━━━━━━━━━━\n🖥️ Environment: Android Termux\n🐍 Engine: Python 3.x\n⚙️ الحالة: جميع الأنظمة تعمل بكفاءة 100%."
                        elif user_text == "3":
                            response = "🚀 ┃ رُؤيـة الـمُـسـتـقـبـل ┃\n━━━━━━━━━━━━━━━\n🧠 دمج الـ AI للرد الذكي قريباً.\n📈 ترقبوا التحديثات القادمة!"
                        elif user_text == "4":
                            response = "📩 ┃ بـوابـة الـتـواصـل الـمُـبـاشـر ┃\n━━━━━━━━━━━━━━━\n⏳ حالة محمد الآن: في وضع التطوير والإبداع 👨‍💻🔥\n✉️ اترك رسالتك الآن، وسيتم الرد عليك فور تفرغه."
                        else:
                            # الحالة 3: أي رسالة أخرى غير الأوامر (بعد إرسال الترحيب فعلياً)
                            response = alert_msg

                        greenAPI.sending.sendMessage(chat_id, response)
                
                # مسح الإشعار من السيرفر
                greenAPI.receiving.deleteNotification(receipt_id)
            
            time.sleep(1)
        except Exception as e:
            print(f"حدث خطأ: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
