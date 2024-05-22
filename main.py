from telebot import TeleBot, util
from telebot_token import TOKEN
import subprocess
import tempfile
import os

MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB


def opus_encode(file_bytes, volume_boost=False, bass_boost=False):
    with tempfile.NamedTemporaryFile(delete=False) as fp:
        fp.write(file_bytes)
        input_file = fp.name

    with tempfile.NamedTemporaryFile(delete=False, suffix='.ogg') as fp:
        output_file = fp.name

    volume = 1.5 if volume_boost else 1
    gain = 5 if bass_boost else 1
    subprocess.run(
        ["ffmpeg", "-i", input_file, "-vn", "-filter:a", f"volume={volume}, bass=gain={gain}",
         "-codec:a", "libopus", output_file, '-y'])

    with open(output_file, 'rb') as f:
        opus_bytes = f.read()

    os.unlink(input_file)
    os.unlink(output_file)

    return opus_bytes


def main():
    bot = TeleBot(TOKEN)
    voice_options_markup = util.quick_markup({'Volume boost': {'callback_data': 'volume_boost'},
                                              'Bass boost': {'callback_data': 'bass_boost'},
                                              'Add caption': {'callback_data': 'add_caption'}})

    def download_and_process_file(message, file_id, volume_boost=False, bass_boost=False):
        process_message = bot.reply_to(message, "Downloading...")
        file_info = bot.get_file(file_id)
        file_bytes = bot.download_file(file_info.file_path)

        bot.edit_message_text("Processing...", message.chat.id, process_message.message_id)
        ogg_file_bytes = opus_encode(file_bytes, volume_boost, bass_boost)

        bot.edit_message_text("Sending...", message.chat.id, process_message.message_id)
        bot.send_voice(message.chat.id, ogg_file_bytes, reply_to_message_id=message.message_id,
                       reply_markup=voice_options_markup)

        bot.delete_message(message.chat.id, process_message.message_id)

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

        download_and_process_file(message, file.file_id)

    @bot.callback_query_handler(func=lambda call: call.data == "add_caption")
    def handle_add_caption_callback(call):
        request_message = bot.send_message(call.message.chat.id, "Send the caption text",
                                           reply_to_message_id=call.message.message_id)
        bot.register_next_step_handler(call.message, process_caption_response, call.message,
                                       request_message.message_id)

    @bot.callback_query_handler(lambda call: call.data == "volume_boost")
    def handle_volume_boost_callback(call):
        download_and_process_file(call.message, call.message.voice.file_id, volume_boost=True)

    @bot.callback_query_handler(lambda call: call.data == "bass_boost")
    def handle_bass_boost_callback(call):
        download_and_process_file(call.message, call.message.voice.file_id, bass_boost=True)

    def process_caption_response(message, original_voice_message, request_message_id):
        bot.edit_message_caption(message.text, message.chat.id, original_voice_message.message_id,
                                 reply_markup=voice_options_markup)
        bot.delete_messages(message.chat.id, [request_message_id, message.message_id])

    bot.infinity_polling()


if __name__ == '__main__':
    main()
