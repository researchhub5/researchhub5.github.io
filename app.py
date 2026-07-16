import os
import logging
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import threading

# ============ YOUR SETTINGS ============
BOT_TOKEN = "7809043358:AAG0BNLgcCCn6KeHIc7WaDJMOPjIj8mst6E"
CHANNEL_USERNAME = "reseacheraservice"
WEBSITE_URL = "https://researchhub5.github.io"
# =======================================

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    try:
        member = await context.bot.get_chat_member(f"@{CHANNEL_USERNAME}", user_id)
        subscribed = member.status in ['member', 'administrator', 'creator']
    except:
        subscribed = False
    
    if subscribed:
        keyboard = [[InlineKeyboardButton("📥 Download Research Files", url=WEBSITE_URL)]]
        await update.message.reply_text(
            "✅ You're subscribed! Click below to access research files:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        keyboard = [
            [InlineKeyboardButton("🔗 Join Channel", url=f"https://t.me/{CHANNEL_USERNAME}")],
            [InlineKeyboardButton("🔄 Check Again", callback_data="check")]
        ]
        await update.message.reply_text(
            "⚠️ Please join @reseacheraservice first!\n\n"
            "1️⃣ Click 'Join Channel'\n"
            "2️⃣ Subscribe\n"
            "3️⃣ Click 'Check Again'",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    try:
        member = await context.bot.get_chat_member(f"@{CHANNEL_USERNAME}", user_id)
        subscribed = member.status in ['member', 'administrator', 'creator']
    except:
        subscribed = False
    
    if subscribed:
        keyboard = [[InlineKeyboardButton("📥 Download Research Files", url=WEBSITE_URL)]]
        await query.edit_message_text(
            "✅ Success! You're now subscribed.\n\nClick below to download:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await query.edit_message_text(
            "❌ Still not subscribed. Please join @reseacheraservice first!"
        )

# Create Flask app
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Bot is running!"

@app.route('/health')
def health():
    return "OK", 200

# Function to run Telegram bot
def run_telegram_bot():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(check, pattern="check"))
    print("🤖 Bot is running! Send /start to @Research_Thesis_Support_bot")
    application.run_polling()

# Start both the web server and the bot
if __name__ == "__main__":
    bot_thread = threading.Thread(target=run_telegram_bot)
    bot_thread.start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)