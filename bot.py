import requests
import simplekml
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# Ваш API-ключ Яндекс.Карт
YANDEX_API_KEY = "fa502190-c271-4718-a72a-ec6a3f0adad5"
# Токен вашего Telegram-бота
TELEGRAM_BOT_TOKEN = "7557058696:AAEXJkcN16mDMfcQN_kIzWtnME3vyIdceqw"

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Привет! Отправьте мне название города, и я создам KML файл с его границами.')

def get_city_boundaries(update: Update, context: CallbackContext) -> None:
    city_name = ' '.join(context.args)
    if not city_name:
        update.message.reply_text('Пожалуйста, укажите название города.')
        return

    url = f"https://geocode-maps.yandex.ru/1.x/?apikey={YANDEX_API_KEY}&geocode={city_name}&format=json"
    response = requests.get(url)
    data = response.json()

    try:
        coordinates = data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['boundedBy']['Envelope']
        lower_corner = coordinates['lowerCorner'].split()
        upper_corner = coordinates['upperCorner'].split()

        kml = simplekml.Kml()
        pol = kml.newpolygon(name=f"Границы города {city_name}")
        pol.outerboundaryis = [
            (float(lower_corner[0]), float(lower_corner[1])),
            (float(upper_corner[0]), float(lower_corner[1])),
            (float(upper_corner[0]), float(upper_corner[1])),
            (float(lower_corner[0]), float(upper_corner[1])),
            (float(lower_corner[0]), float(lower_corner[1]))
        ]

        kml_file = f"{city_name}_boundaries.kml"
        kml.save(kml_file)

        with open(kml_file, 'rb') as file:
            update.message.reply_document(file, filename=kml_file)

    except (IndexError, KeyError):
        update.message.reply_text('Не удалось найти границы для указанного города. Попробуйте другой город.')

def main() -> None:
    updater = Updater(TELEGRAM_BOT_TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("getcity", get_city_boundaries))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
