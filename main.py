import logging
import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Define states
CITY, PRODUCT, QUANTITY = range(3)

user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        logger.error("No message in update")
        return ConversationHandler.END

    reply_markup = ReplyKeyboardMarkup([
        ['🏙️ Vilnius'], ['🏙️ Kaunas'], ['🏙️ Klaipėda']
    ], one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("🏡 Pasirink savo miestą:", reply_markup=reply_markup)
    return CITY

async def city_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None or update.effective_user is None:
        logger.error("No message or user in update")
        return ConversationHandler.END

    user_data[update.effective_user.id] = {'city': update.message.text}

    reply_markup = ReplyKeyboardMarkup([
        ['☘️ Product A'], ['❄️ Product B'], ['💎 Product C']
    ], one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("🛍️ Pasirink produktą:", reply_markup=reply_markup)
    return PRODUCT

async def product_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None or update.effective_user is None:
        logger.error("No message or user in update")
        return ConversationHandler.END

    user_id = update.effective_user.id
    product = update.message.text
    
    # Check if product is None
    if product is None:
        await update.message.reply_text("❌ Negautas produkto pasirinkimas. Bandyk iš naujo.")
        return PRODUCT
    
    user_data[user_id]['product'] = product

    # Decide quantities based on product
    if "Product A" in product:
        quantities = [['2'], ['5'], ['10']]
    elif "Product B" in product:
        quantities = [['1'], ['2'], ['3']]
    elif "Product C" in product:
        quantities = [['1'], ['2'], ['5']]
    else:
        await update.message.reply_text("❌ Nežinomas produktas. Bandyk iš naujo.")
        return PRODUCT

    reply_markup = ReplyKeyboardMarkup(quantities, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("🔢 Pasirink kiekį:", reply_markup=reply_markup)
    return QUANTITY

async def quantity_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None or update.effective_user is None:
        logger.error("No message or user in update")
        return ConversationHandler.END

    user_id = update.effective_user.id
    user_data[user_id]['quantity'] = update.message.text

    # Static or generated crypto address
    crypto_address = "bc1qexampleaddress..."

    order = user_data[user_id]
    summary = (
        f"🛒 Užsakymo suvestinė:\n"
        f"📍 Miestas: {order['city']}\n"
        f"📦 Produktas: {order['product']}\n"
        f"🔢 Kiekis: {order['quantity']}\n\n"
        f"💸 Prašome atlikti mokėjimą į šį kripto adresą:\n\n`{crypto_address}`"
    )
    await update.message.reply_text(summary, parse_mode="Markdown")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        logger.error("No message in update for cancel")
        return ConversationHandler.END

    await update.message.reply_text("❌ Užsakymas atšauktas.")
    return ConversationHandler.END

if __name__ == '__main__':
    try:
        logger.info("Starting Telegram bot...")
        token = os.getenv("BOT_TOKEN")
        if not token:
            logger.error("TELEGRAM_BOT_TOKEN environment variable not found")
            raise ValueError("Bot token is required")
        
        app = ApplicationBuilder().token(token).build()

        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', start)],
            states={
                CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, city_chosen)],
                PRODUCT: [MessageHandler(filters.TEXT & ~filters.COMMAND, product_chosen)],
                QUANTITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, quantity_chosen)],
            },
            fallbacks=[CommandHandler('cancel', cancel)]
        )

        app.add_handler(conv_handler)
        logger.info("Bot handlers registered. Starting polling...")
        app.run_polling()
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        raise
