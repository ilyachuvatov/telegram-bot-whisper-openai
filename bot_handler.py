from telegram import Update
from telegram.ext import ContextTypes
import requests
import logging
import ffmpeg
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class BotHandler:
    def __init__(self, audio_transcriber, openai_handler):
        self.audio_transcriber = audio_transcriber
        self.openai_handler = openai_handler
        self.logger = logging.getLogger(__name__)

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.logger.info("Received start command")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot that can help you transcribe an audio file and make a summary")

    async def echo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.logger.info(f"Echoing message: {update.message.text}")
        await context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)

    async def handle_video(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.logger.info(f"Received video file: {update.message.video.file_id}")
        video_file_id = update.message.video.file_id
        if video_file_id:
            context.user_data['video_file_id'] = video_file_id
            self.logger.info("Video file ID saved in user data")
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Video received. You can transcribe it with /transcribe")
        else:
            self.logger.warning("No video file ID received")

    async def transcribe_audio(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.logger.info("Attempting to transcribe audio")
        if 'audio_file_id' in context.user_data or 'video_file_id' in context.user_data:
            file_id = context.user_data.get('audio_file_id') or context.user_data.get('video_file_id')
            try:
                file = await context.bot.getFile(file_id)
                file_path = file.file_path
                if 'video_file_id' in context.user_data:
                    audio_data = self.extract_audio_from_video(file_path)
                else:
                    audio_data = requests.get(file_path).content
                
                transcription = self.audio_transcriber.transcribe(audio_data)
                context.user_data['transcription'] = transcription['text']
                self.logger.info(f"Transcription successful: {transcription['text']}")
                await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Transcription: {transcription['text']}")
            except Exception as e:
                self.logger.error(f"Error in transcription: {e}")
                await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Error in transcription: {str(e)}")
        else:
            self.logger.warning("No audio or video file ID found in user data")
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Please send an audio or video file first")

    def extract_audio_from_video(self, video_file_url):
        response = requests.get(video_file_url)
        video_filename = 'downloaded_video.mp4'
        with open(video_filename, 'wb') as f:
            f.write(response.content)
        audio_filename = 'extracted_audio.wav'
        ffmpeg.input(video_filename).output(audio_filename, format='wav', acodec='pcm_s16le', ac=1, ar='16k').run(overwrite_output=True)
        os.remove(video_filename)
        os.remove(audio_filename)
        return audio_filename

    async def summarize_transcription(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.logger.info("Attempting to summarize transcription")
        if 'transcription' in context.user_data:
            transcription = context.user_data['transcription']
            summary = self.openai_handler.summary(transcription)
            self.logger.info(f"Summary successful: {summary}")
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Summary: {summary}")
        else:
            self.logger.warning("No transcription found in user data")
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Please transcribe an audio first with /transcribe")

    async def handle_audio(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.logger.info(f"Received audio file: {update.message.audio.file_id}")
        audio_file_id = update.message.audio.file_id
        if audio_file_id:
            context.user_data['audio_file_id'] = audio_file_id
            self.logger.info("Audio file ID saved in user data")
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Audio received. You can transcribe it with /transcribe")
        else:
            self.logger.warning("No audio file ID received")

    async def handle_audio_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.logger.info(f"Received an audio message: {update.message.audio.file_id}")
        audio_file_id = update.message.audio.file_id
        if audio_file_id:
            context.user_data['audio_file_id'] = audio_file_id
            self.logger.info(f"Audio file ID saved: {audio_file_id}")
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Audio received. You can transcribe it with /transcribe")
        else:
            self.logger.warning("No audio file ID found in message")
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Failed to receive audio. Please try again.")

