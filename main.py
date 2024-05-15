from telebot import TeleBot
from telebot_token import TOKEN
import subprocess
import tempfile
import os


def opus_encode(file_bytes):
    with tempfile.NamedTemporaryFile(delete=False) as fp:
        fp.write(file_bytes)
        input_file = fp.name

    with tempfile.NamedTemporaryFile(delete=False, suffix='.ogg') as fp:
        output_file = fp.name

    subprocess.run(["ffmpeg", "-i", input_file, "-vn", "-c:a", "libopus", output_file, '-y'])

    with open(output_file, 'rb') as f:
        opus_bytes = f.read()

    os.unlink(input_file)
    os.unlink(output_file)

    return opus_bytes


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
