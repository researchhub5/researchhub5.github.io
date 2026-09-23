import os
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# ============================================
# ✏️ EDIT ONLY THESE 3 LINES
# ============================================
BOT_TOKEN    = "8666777791:AAEfGJe9lPLB9OzTWu6uFwmmaEDOg5Rp6s8"
CHANNEL_ID   = "@researcheraservice"
CHANNEL_LINK = "https://t.me/+tjP08iEcaK9mY2Zk"
# ============================================

# Map file IDs to their download URLs
FILES = {
    "file_101": {"name": "Anesthesia Dept Research Papers", "url": "https://github.com/researchhub5/researchhub5.github.io/raw/main/ANESTHESIA%20DEPT%20RESEARCH%20PAPER.zip"},
    "file_102": {"name": "Department of Accounting and Finance", "url": "https://github.com/researchhub5/researchhub5.github.io/raw/main/Department%20of%20Accounting%20and%20Finance.rar"},
    "file_103": {"name": "Department of Marketing Management", "url": "https://github.com/researchhub5/researchhub5.github.io/raw/main/DEPARTMENT%20OF%20MARKETING%20MANAGEMENT.rar"},
    "file_104": {"name": "Department of Public Administration", "url": "https://github.com/researchhub5/researchhub5.github.io/raw/main/Department%20of%20Public%20Administration.rar"},
    "file_105": {"name": "Economics Department Research Papers", "url": "https://github.com/researchhub5/researchhub5.github.io/raw/main/ECONOMICS%20DEPARTMENT%20RESEARCH%20PAPER.rar"},
    "file_108": {"name": "Master of Business Administration (MBA)", "url": "https://github.com/researchhub5/researchhub5.github.io/raw/main/MASTER%20OF%20BUSINESS%20ADMINISTRATION.rar"},
    "file_113": {"name": "School of Commerce Research Papers", "url": "https://github.com/researchhub5/researchhub5.github.io/raw/main/School%20of%20Commerce.rar"},
    "file_11":  {"name": "Fikadu Thesis - Vitamin D Study", "url": "https://github.com/researchhub5/researchhub5.github.io/raw/main/FIKADU%20THESIS1.pdf"},
}

async def is_subscribed(user_id, context):
    """Check if user is a member of the channel."""
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        print("Check error:", e)
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    args = context.args
    file_code = args[0] if args else None

    if not file_code or file_code not in FILES:
        await update.message.reply_text(
            "👋 Welcome to Research & Thesis Support Center!\n\n"
            "Please choose a file from our website:\n"
            "https://researchhub5.github.io"
        )
        return

    context.user_data['pending_file'] = file_code

    if await is_subscribed(user_id, context):
        await send_file_link(update, context, file_code)
    else:
        await prompt_sub(update, context)

async def prompt_sub(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📢 Join Our Channel", url=CHANNEL_LINK)],
        [InlineKeyboardButton("✅ I Joined — Verify Me", callback_data="check_sub")]
    ]
    text = ("⚠️ *Access Locked*\n\n"
            "You must join our Telegram channel before downloading.\n\n"
            "1️⃣ Tap *Join Our Channel*\n"
            "2️⃣ Then tap *I Joined — Verify Me*")
    markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text(text, reply_markup=markup, parse_mode="Markdown")
    else:
        await update.callback_query.message.edit_text(text, reply_markup=markup, parse_mode="Markdown")

async def verify_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if await is_subscribed(user_id, context):
        file_code = context.user_data.get('pending_file')
        if file_code:
            await send_file_link(update, context, file_code)
        else:
            await query.message.edit_text("✅ Verified! Please choose a file from the website again.")
    else:
        await query.answer("❌ You haven't joined yet. Please join first!", show_alert=True)

async def send_file_link(update: Update, context: ContextTypes.DEFAULT_TYPE, file_code: str):
    info = FILES[file_code]
    keyboard = [[InlineKeyboardButton("⬇️ Download Now", url=info["url"])]]
    text = f"✅ *Verified!*\n\n📄 *{info['name']}*\n\nTap below to download:"
    markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text(text, reply_markup=markup, parse_mode="Markdown")
    else:
        await update.callback_query.message.edit_text(text, reply_markup=markup, parse_mode="Markdown")

# --- Tiny web server (keeps Render happy) ---
app = Flask(__name__)

@app.route('/')
@app.route('/health')
def health():
    return "OK", 200

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(verify_callback, pattern="^check_sub$"))
    application.run_polling()
