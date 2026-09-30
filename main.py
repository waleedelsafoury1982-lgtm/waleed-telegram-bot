import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from google import genai
from google.genai import types

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")

client = genai.Client(api_key=GEMINI_API_KEY)

# حط رابط التحميل المباشر لجوجل درايف هنا
DRIVE_PDF_URL = "https://drive.google.com/uc?export=download&id=1SHcGZGJLt00Rlyw7nMKfiYVKRAJs9736"
local_pdf_path = "transcript.pdf"

print("جاري تحميل ملف الشرح من جوجل درايف...")
response = requests.get(DRIVE_PDF_URL)
with open(local_pdf_path, "wb") as f:
    f.write(response.content)
print("تم تحميل الملف بنجاح، جاري رفعه لـ Gemini...")

uploaded_file = client.files.upload(file=local_pdf_path)
print("تم إعداد الملف وجاهز لاستقبال أسئلة الطلاب.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    
    system_instruction = """
    أنت مساعد ذكي خاص بالمهندس وليد. مهمتك الإجابة على أسئلة الطلاب بناءً فقط على ملف التفريغ المرفق.
    قواعد الرد:
    1. التزم تماماً بالمعلومات الموجودة في الملف وبنفس الأسلوب والشرح المبسط للمهندس وليد.
    2. إذا كان السؤال خارج محتوى الملف المرفق تماماً، رد بالحرف الواحد:
       "هذا السؤال خارج محتوى المحاضرة الحالية، برجاء الرجوع للمهندس وليد".
    3. لا تقم بتأليف أي معلومات من خارج الملف نهائياً.
    """

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[uploaded_file, user_message],
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.3,
            ),
        )
        bot_reply = response.text
    except Exception as e:
        bot_reply = "عذراً حدث خطأ تقني، برجاء المحاولة لاحقاً أو الرجوع للمهندس وليد."

    await update.message.reply_text(bot_reply)

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print("البوت يعمل الآن...")
    app.run_polling()

if __name__ == '__main__':
    main()
