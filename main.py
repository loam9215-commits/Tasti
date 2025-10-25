import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from deep_translator import GoogleTranslator
import asyncio

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot token - Replace with your actual bot token from @BotFather
TOKEN = '8301920673:AAHwv9Jh97blKYnchrcnee6xHhqZqm--4nw'  # <-- CHANGE THIS!

# Initialize translator for Oromo ('om') - auto-detects source
translator = GoogleTranslator(source='auto', target='om')

# Oromo messages (pre-defined for speed)
OROMO_WELCOME = "Baga nagaan dhufte! 📝 \n\nBarreeffama kamuu naaf ergaa Afaan Oromootti nan hiika"

OROMO_SUPPORT = "@Pabloecov support ergaa. Message ergaa fi malee ergaa! 📞"

OROMO_ERROR = "😔 *Hin dabaratu!*"

OROMO_GREETING = "Akkami?"

OROMO_LANGUAGES = "Afaan 100+ kanneen naaf ergaa nan hiika: English, Amharic, Arabic, French, Spanish, etc. /help ergaa!"

async def translate_text(text: str) -> str:
    """Async wrapper for translation to allow non-blocking."""
    try:
        return await asyncio.to_thread(translator.translate, text)
    except Exception as e:
        logger.error(f"Translation error: {e}")
        raise

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start."""
    try:
        await update.message.reply_text(OROMO_WELCOME, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error in start: {e}")
        await update.message.reply_text(OROMO_ERROR, parse_mode='Markdown')

async def support_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /support - Direct to @Pabloecov."""
    try:
        await update.message.reply_text(OROMO_SUPPORT, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error in support_command: {e}")
        await update.message.reply_text(OROMO_ERROR, parse_mode='Markdown')

async def languages_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /languages - List supported (more feature)."""
    try:
        await update.message.reply_text(OROMO_LANGUAGES, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error in languages_command: {e}")
        await update.message.reply_text(OROMO_ERROR, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help - More features overview."""
    try:
        help_text = await translate_text(
            "• /start - Ergaa\n• /support - @Pabloecov ergaa\n• /languages - Afaan kanneen\n• Barreeffama ergaa - Afaan Oromootti nan hiika\n\nGroupoota keessatti add gochuu!"
        )
        await update.message.reply_text(help_text)
    except Exception as e:
        logger.error(f"Error in help_command: {e}")
        await update.message.reply_text(OROMO_ERROR, parse_mode='Markdown')

async def translate_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Translate messages to Oromo - Pure translation only."""
    text = update.message.text.lower().strip() if update.message.text else ""

    try:
        # Skip commands
        if text.startswith('/'):
            return

        # Special greeting case (handles emojis/numbers implicitly via translator)
        if text in ['hi', 'hello', 'hey']:
            await update.message.reply_text(OROMO_GREETING)
            return

        # Translate and respond with pure Oromo (handles emojis/numbers naturally)
        translation = await translate_text(update.message.text)
        await update.message.reply_text(translation)
    except Exception as e:
        logger.error(f"Error in translate_message: {e}")
        await update.message.reply_text(OROMO_ERROR, parse_mode='Markdown')

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle photo messages (including forwarded) - Translate caption only."""
    caption = update.message.caption or ""

    try:
        if caption:
            # Translate caption (preserves emojis/numbers)
            translation = await translate_text(caption)
            # Reply with the same photo and translated caption
            await update.message.reply_photo(
                photo=update.message.photo[-1].file_id,
                caption=translation
            )
        # If no caption, silently ignore (focus on translation only)
    except Exception as e:
        logger.error(f"Error in handle_photo: {e}")
        # For forwards/photos, if translation fails, perhaps reply with original caption or just error
        if caption:
            await update.message.reply_photo(
                photo=update.message.photo[-1].file_id,
                caption=caption
            )
        else:
            await update.message.reply_text(OROMO_ERROR, parse_mode='Markdown')

def main() -> None:
    """Run the bot."""
    if TOKEN == 'YOUR_BOT_TOKEN_HERE':
        print("🚨 Set your TOKEN first! 🚨")
        return

    application = Application.builder().token(TOKEN).build()

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("support", support_command))
    application.add_handler(CommandHandler("languages", languages_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, translate_message))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print("🤖 Pure Oromo Bot Starting... (No Rate Limit | Support: @Pabloecov)")
    application.run_polling()

if __name__ == '__main__':
    main()
