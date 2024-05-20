from telebot import TeleBot, util
from telebot_token import TOKEN
import subprocess
import tempfile
import os

MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB
user_data = dict()


def opus_encode(file_bytes):
    with tempfile.NamedTemporaryFile(delete=False) as fp:
        fp.write(file_bytes)
        input_file = fp.name

    with tempfile.NamedTemporaryFile(delete=False, suffix='.ogg') as fp:
        output_file = fp.name

    subprocess.run(
        ["ffmpeg", "-i", input_file, "-vn", "-filter:a", "volume=1, bass=gain=1",
         "-codec:a", "libopus", output_file, '-y'])

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

    @bot.message_handler(content_types=['audio', 'video', 'voice'])
    def handle_audio_video_file(message):
        file = message.audio or message.video or message.voice

        if file.file_size > MAX_FILE_SIZE:
            file_size_error_message = "File is too large\n" \
                                      "The file size should be less than 20 MB"
            bot.send_message(message.chat.id, file_size_error_message, reply_to_message_id=message.message_id)
            return

        file_id = file.file_id
        file_info = bot.get_file(file_id)
        file_bytes = bot.download_file(file_info.file_path)
        ogg_file_bytes = opus_encode(file_bytes)

        user_data[message.chat.id] = ogg_file_bytes
        print("number of users:", len(user_data))

        markup = util.quick_markup({'Bass boost': {'callback_data': 'bass_boost'},
                                    'Add caption': {'callback_data': 'add_caption'}})

        bot.send_voice(message.chat.id, ogg_file_bytes, reply_to_message_id=message.message_id, reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: True)
    def handle_callback_query(call):
        if call.data == "add_caption":
            request_message = bot.send_message(call.message.chat.id, "Send the caption text",
                                               reply_to_message_id=call.message.message_id)
            bot.register_next_step_handler(call.message, process_add_caption, request_message.message_id,
                                           call.message.message_id)
        elif call.data == "bass_boost":
            bot.send_message(call.message.chat.id, "Bass boosting is in development",
                             reply_to_message_id=call.message.message_id)

    def process_add_caption(message, request_message_id, voice_message_id):
        ogg_file_bytes = user_data.get(message.chat.id)

        bot.send_voice(message.chat.id, ogg_file_bytes, caption=message.text, reply_to_message_id=voice_message_id)
        bot.delete_message(message.chat.id, request_message_id)
        bot.delete_message(message.chat.id, message.message_id)

    bot.infinity_polling()


if __name__ == '__main__':
    main()
