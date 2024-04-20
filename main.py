from telebot import TeleBot
from telebot_token import TOKEN
import subprocess


def main():
    bot = TeleBot(TOKEN)

    def opus_encode(file_bytes):
        process = subprocess.Popen(['ffmpeg', '-i', '-', '-f', 'opus', '-acodec', 'libopus', '-'],
                                   stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE)
        opus_file_file_bytes, _ = process.communicate(input=file_bytes)
        return opus_file_file_bytes

    # @bot.message_handler(commands=['test'])
    # def handle_test(message):
    #     test_file_name = "oIEmXEREIDAfAE4LQmBQiheYPBFNZBCDw9snIi.mp4"
    #     # test_ogg_file_name = "Anti_blink_03.opus"
    #
    #     with open(f"tmp/{test_file_name}", "rb") as f:
    #         test_file = f.read()
    #
    #     process = subprocess.Popen(['ffmpeg', '-i', '-', '-f', 'opus', '-acodec', 'libopus', '-'],
    #                                stdin=subprocess.PIPE,
    #                                stdout=subprocess.PIPE)
    #
    #     test_ogg_file, _ = process.communicate(input=test_file)
    #
    #     bot.send_voice(message.chat.id, test_ogg_file)

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
