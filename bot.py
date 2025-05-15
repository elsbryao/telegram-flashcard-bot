# bot.py
import os
import zipfile
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from utils import generate_flashcards_from_word, generate_flashcards_from_eng_phrases, generate_flashcards_from_rus_phrases

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
VOICE_ID = os.getenv("VOICE_ID")

output_zip = "flashcards.zip"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Отправь одну из команд:\n/word [слово] — фразы с этим словом\n/eng — фразы на английском (переводит и озвучивает)\n/rus — фразы на русском (переводит и озвучивает)")

async def word_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Пожалуйста, укажи слово после команды /word")
        return
    word = context.args[0]
    await update.message.reply_text(f"Генерирую карточки для слова: {word}...")
    generate_flashcards_from_word(word, OPENAI_API_KEY, ELEVENLABS_API_KEY, VOICE_ID)
    with open(output_zip, 'rb') as f:
        await update.message.reply_document(document=f, filename="flashcards.zip")

async def eng_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phrases = update.message.text.replace("/eng", "").strip().split("\n")
    if not phrases or phrases == ['']:
        await update.message.reply_text("Пожалуйста, отправь список английских фраз после команды /eng")
        return
    await update.message.reply_text("Обрабатываю английские фразы...")
    generate_flashcards_from_eng_phrases(phrases, OPENAI_API_KEY, ELEVENLABS_API_KEY, VOICE_ID)
    with open(output_zip, 'rb') as f:
        await update.message.reply_document(document=f, filename="flashcards.zip")


async def rus_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phrases = update.message.text.replace("/rus", "").strip().split("\n")
    if not phrases or phrases == ['']:
        await update.message.reply_text("Пожалуйста, отправь список русских фраз после команды /rus")
        return
    await update.message.reply_text("Обрабатываю русские фразы...")
    generate_flashcards_from_rus_phrases(phrases, OPENAI_API_KEY, ELEVENLABS_API_KEY, VOICE_ID)
    with open(output_zip, 'rb') as f:
        await update.message.reply_document(document=f, filename="flashcards.zip")


def main():
    app = ApplicationBuilder().token(os.getenv("TELEGRAM_TOKEN")).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("word", word_handler))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^/eng"), eng_handler))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^/rus"), rus_handler))
    app.run_polling()

if __name__ == '__main__':
    main()
