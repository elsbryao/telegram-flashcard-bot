# bot.py
import os
import zipfile
from telegram import Update, InputFile, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters, CallbackQueryHandler
from utils import generate_flashcards_from_word, generate_flashcards_from_eng_phrases, generate_flashcards_from_rus_phrases

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

output_zip = "flashcards.zip"

# 🔊 Доступные голоса
VOICES = {
    "Theresa": "ORI4FGngxVpyYi4rGvdr",
    "Chris": "iP95p4xoKVk53GoZ742B",
    "Brian": "nPczCjzI2devNBz1zQrb"
}

# 💾 Выбор голоса на пользователя
user_voice_map = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я помогу тебе учить английский через карточки.\n\nКоманды:\n/word [слово] — карточки с этим словом\n/eng — англ. фразы (перевод + озвучка)\n/rus — рус. фразы (перевод + озвучка)\n/voice — выбрать голос озвучки"
    )

async def voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(name, callback_data=f"voice:{vid}")] for name, vid in VOICES.items()
    ]
    await update.message.reply_text(
        "Выбери голос для озвучки:", reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def voice_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    voice_id = query.data.split(":")[1]
    user_id = query.from_user.id
    user_voice_map[user_id] = voice_id
    await query.edit_message_text("Голос выбран!")

async def word_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Пожалуйста, укажи слово после команды /word")
        return
    word = context.args[0]
    await update.message.reply_text(f"Генерирую карточки для слова: {word}...")
    voice_id = user_voice_map.get(update.effective_user.id, list(VOICES.values())[0])
    generate_flashcards_from_word(word, OPENAI_API_KEY, ELEVENLABS_API_KEY, voice_id)
    with open(output_zip, 'rb') as f:
        await update.message.reply_document(document=f, filename="flashcards.zip")

async def eng_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phrases = update.message.text.replace("/eng", "").strip().split("\n")
    if not phrases or phrases == ['']:
        await update.message.reply_text("Пожалуйста, отправь список английских фраз после команды /eng")
        return
    await update.message.reply_text("Обрабатываю английские фразы...")
    voice_id = user_voice_map.get(update.effective_user.id, list(VOICES.values())[0])
    generate_flashcards_from_eng_phrases(phrases, OPENAI_API_KEY, ELEVENLABS_API_KEY, voice_id)
    with open(output_zip, 'rb') as f:
        await update.message.reply_document(document=f, filename="flashcards.zip")

async def rus_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phrases = update.message.text.replace("/rus", "").strip().split("\n")
    if not phrases or phrases == ['']:
        await update.message.reply_text("Пожалуйста, отправь список русских фраз после команды /rus")
        return
    await update.message.reply_text("Обрабатываю русские фразы...")
    voice_id = user_voice_map.get(update.effective_user.id, list(VOICES.values())[0])
    generate_flashcards_from_rus_phrases(phrases, OPENAI_API_KEY, ELEVENLABS_API_KEY, voice_id)
    with open(output_zip, 'rb') as f:
        await update.message.reply_document(document=f, filename="flashcards.zip")

def main():
    app = ApplicationBuilder().token(os.getenv("TELEGRAM_TOKEN")).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("word", word_handler))
    app.add_handler(CommandHandler("eng", eng_handler))
    app.add_handler(CommandHandler("rus", rus_handler))
    app.add_handler(CommandHandler("voice", voice))
    app.add_handler(CallbackQueryHandler(voice_callback, pattern="^voice:"))
    app.run_polling()

if __name__ == '__main__':
    main()
