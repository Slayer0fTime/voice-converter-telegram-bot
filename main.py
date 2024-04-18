from telebot import TeleBot


def main():
    bot = TeleBot("7094916800:AAFRKWLn6F1uJ1N9h6fZ7LGPRjTsqa_Sl8U")

    @bot.message_handler(commands=['start', 'help'])
    def start(message):
        start_message = f"Hi, {message.from_user.first_name}.\n" \
                        f"I can convert audio or video into a voice message.\n" \
                        f"Send audio or video.\n" \
                        f"Glory to @slayer_of_time"
        bot.send_message(message.chat.id, start_message)

    @bot.message_handler(content_types=['audio', 'video'])
    def handle_audio(message):
        if message.audio:
            file_id = message.audio.file_id
        elif message.video:
            file_id = message.video.file_id

        file_info = bot.get_file(file_id)
        file_path = file_info.file_path
        audio_bytes = bot.download_file(file_path)

        bot.send_voice(message.chat.id, audio_bytes, reply_to_message_id=message.message_id)

    bot.infinity_polling()


if __name__ == '__main__':
    main()
