from audio_transcriber import HuggingFaceModel
from bot_handler import BotHandler
from openai_handler import OpenaiHandler
from telegram.ext import MessageHandler, ApplicationBuilder, CommandHandler, filters



class Bot:
    def __init__(self, TOKEN, OPENAI_KEY):
        self.audio_transcriber = HuggingFaceModel()
        self.openai_handler =OpenaiHandler(OPENAI_KEY)
        self.bot_handler = BotHandler(self.audio_transcriber, self.openai_handler)
        self.application = ApplicationBuilder().token(TOKEN).build()
        self.setup_handlers()

    def setup_handlers(self):
        self.application.add_handler(CommandHandler('start', self.bot_handler.start))
        self.application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), self.bot_handler.echo))
        self.application.add_handler(MessageHandler(filters.AUDIO & (~filters.COMMAND), self.bot_handler.handle_audio))
        self.application.add_handler(CommandHandler('transcribe', self.bot_handler.transcribe_audio))
        self.application.add_handler(CommandHandler('summarize', self.bot_handler.summarize_transcription))
        self.application.add_handler(MessageHandler(filters.AUDIO & (~filters.COMMAND), self.bot_handler.handle_audio_message))
        self.application.add_handler(MessageHandler(filters.VIDEO & (~filters.COMMAND), self.bot_handler.handle_video))

    def run(self):
        self.application.run_polling()