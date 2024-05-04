from telebot import TeleBot
from telebot_token import TOKEN
import subprocess


def opus_encode(file_bytes):
    process = subprocess.Popen(['ffmpeg', '-i', '-', '-f', 'opus', '-'],
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE)
    opus_file_file_bytes, _ = process.communicate(input=file_bytes)
    return opus_file_file_bytes


def main():
    bot = TeleBot(TOKEN)

    @bot.message_handler(commands=['start', 'help'])
    def handle_start_help(message):
        start_message = f"Hi, {message.from_user.first_name}.\n" \
                        f"I can convert audio or video into a voice message.\n" \
                        f"Send audio or video.\n" \
                        f"Glory to @slayer_of_time"
        bot.send_message(message.chat.id, start_message)

    @bot.message_handler(content_types=['audio', 'video'])
    def handle_audio_video_file(message):
        if message.audio:
            file_id = message.audio.file_id
        elif message.video:
            file_id = message.video.file_id

        file_info = bot.get_file(file_id)
        file_bytes = bot.download_file(file_info.file_path)

        ogg_file_bytes = opus_encode(file_bytes)
        bot.send_voice(message.chat.id, ogg_file_bytes, reply_to_message_id=message.message_id)

    bot.infinity_polling()


if __name__ == '__main__':
    main()
