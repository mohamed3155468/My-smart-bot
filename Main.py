import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# 1. التوكن الخاص بك (من BotFather)
TOKEN = '8688241569:AAGh2U58zOExXRkfchZf_SnU2mfocfMorII'

# قاموس لتخزين وقت آخر ظهور لكل مستخدم
user_last_seen = {}

async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_name = update.message.from_user.first_name
    user_text = update.message.text.lower()
    now = datetime.datetime.now()

    # ---------------------------------------------------------
    # الجزء الأول: تعريف الكلمات المفتاحية والردود المزخرفة
    # ---------------------------------------------------------

    # 1. المواعيد
    time_keywords = ["امتى", "إمتى", "تفتح", "موجود", "مواعيد", "الوقت", "ساعة", "ساعه"]
    time_reply = "✨ ┋ المبرمج محمد بيفتح عادةً في المساء، سيب رسالتك وهيقرأها أول ما يدخل! 🌙"

    # 2. السؤال عن الحال
    health_keywords = ["عامل ايه", "اخبارك", "أخبارك", "إزيك", "ازيك", "كيف حالك"]
    health_reply = "🌟 ┋ مبرمجي بخير ولله الحمد، شكراً لسؤالك الراقي! 😊"

    # 3. الدرس
    lesson_keywords = ["هتروح الدرس", "عندك درس", "رايح الدرس", "الدرس", "درس"]
    lesson_reply = "🏃‍♂️ ┋ مبرمجي أكيد هيروح الدرس، مفيش تزييغ النهاردة! 📚✨"

    # 4. المذاكرة
    study_keywords = ["بتذاكر", "مذاكرة", "مذاكره", "وراك ايه", "بتعمل ايه"]
    study_reply = f"📖 ┋ محمد حالياً {'بيذاكر فيزياء' if now.hour < 20 else 'بيراجع دروسه'}.. ثانية ثانوي محتاجة تركيز! ✍️"

    # 5. الصلاة
    prayer_keywords = ["صليت", "الصلاة", "صلاه", "الاذان", "أذان"]
    prayer_reply = "🕌 ┋ محمد دايماً بيحاول يلتزم بالصلاة في وقتها، جزاك الله خيراً للتذكير! ✨"

    # 6. الأكل
    food_keywords = ["كلت", "أكلت", "جوعان", "فطرت", "غديت", "تعشيت"]
    food_reply = "🍔 ┋ أكيد أكل عشان يقدر يركز في البرمجة والمذاكرة! 🍕"

    # 7. اللعب
    gaming_keywords = ["تلعب", "نلعب", "ببجي", "فيفا", "لعبة", "فورت"]
    gaming_reply = "🚫 ┋ مفيش لعب دلوقتي، وقت المذاكرة والبرمجة أولى! 🎮"

    # 8. رسالة الترحيب (المحطة الأولى)
    welcome_msg = (
        f"╭─── • {user_name} • ───╮\n"
        "  أهلاً بك يا صديقي! 👋\n"
        "  أنا البوت الخاص بالمبرمج محمد.\n"
        "  لو عايز تسأل هو هيفتح إمتى،\n"
        "  اتفضل اسأل وهرد عليك فوراً.\n"
        "╰──── • ✨ • ────╯"
    )

    # ---------------------------------------------------------
    # الجزء الثاني: منطق تشغيل البوت (Logic)
    # ---------------------------------------------------------

    # فحص مدة الجلسة (30 دقيقة)
    is_new_session = True
    if user_id in user_last_seen:
        time_diff = (now - user_last_seen[user_id]).total_seconds() / 60
        if time_diff < 30:
            is_new_session = False
    
    user_last_seen[user_id] = now

    if is_new_session:
        await update.message.reply_text(welcome_msg)
    else:
        # فحص الشروط بالترتيب
        if any(word in user_text for word in study_keywords):
            await update.message.reply_text(study_reply)
        
        elif any(word in user_text for word in prayer_keywords):
            await update.message.reply_text(prayer_reply)
            
        elif any(word in user_text for word in lesson_keywords):
            await update.message.reply_text(lesson_reply)
        
        elif any(word in user_text for word in health_keywords):
            await update.message.reply_text(health_reply)

        elif any(word in user_text for word in food_keywords):
            await update.message.reply_text(food_reply)

        elif any(word in user_text for word in gaming_keywords):
            await update.message.reply_text(gaming_reply)
            
        elif any(word in user_text for word in time_keywords):
            await update.message.reply_text(time_reply)
            
        else:
            # الرد الافتراضي لأي حاجة تانية
            await update.message.reply_text("رسالتك لم يبرمجني محمد عليها 😉")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), reply))
    
    print("🚀 البوت المزخرف والمنظم يعمل الآن بنجاح!")
    app.run_polling()