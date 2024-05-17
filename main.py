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
        start_message = f"Hi, {message.from_user.first_name}\n" \
                        "I can convert audio or video into a voice message\n" \
                        "You can send me one or more audio or video files at once\n" \
                        "With sonic sorcery, @slayer_of_time"
        bot.send_message(message.chat.id, start_message)

    @bot.message_handler(content_types=['audio', 'video'])
    def handle_audio_video_file(message):
        file = message.audio or message.video
        file_id = file.file_id
        file_size = file.file_size

        if file_size > 20 * 1024 * 1024:
            file_size_error_message = "File is too large\n" \
                                      "The file size should be less than 20 MB"
            bot.send_message(message.chat.id, file_size_error_message, reply_to_message_id=message.message_id)
            return

        file_info = bot.get_file(file_id)
        file_bytes = bot.download_file(file_info.file_path)
        ogg_file_bytes = opus_encode(file_bytes)
        bot.send_voice(message.chat.id, ogg_file_bytes, reply_to_message_id=message.message_id)

    bot.infinity_polling()


if __name__ == '__main__':
    main()
