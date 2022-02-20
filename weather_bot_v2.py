import datetime
import requests
from token_gamesales_bot import token
from weather_api_key import api_key
import telebot
import random


class Weather:
    def __init__(self, message):
        self.__api_key = api_key
        self.data = self.get_data(message)
        self.image = None

    def get_data(self, msg):
        r = requests.get(
            f"http://api.openweathermap.org/data/2.5/find?q={msg}&appid={self.__api_key}&lang=ru&units=metric")
        data = r.json()
        return data

    @property
    def weather_data(self):
        try:
            return self.show_weather()
        except:
            return self.wrong_input()

    def show_weather(self):
        feels_like = self.data["list"][0]["main"]["feels_like"]
        name = self.data["list"][0]["name"]
        temp = self.data["list"][0]["main"]["temp"]
        description = self.data["list"][0]["weather"][0]["description"].capitalize()
        time_ = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        ans = f"***{time_}*** \nВ городе {name} температура {temp}С°, ощущается как {feels_like}С°,\n{description}"
        self.weather_image()
        return ans

    def wrong_input(self):
        list_of_answers = ["Нет такого города. Иль чет типа того. \nПопробуй заново",
                           "Эээ... Ну, тут, как бы, нужно указать название города.\n Давай еще раз",
                           "Ну и что ты ввел?! Кто мог так назвать город?! \nЛадно, давай еще раз. Только смотри, что пишешь",
                           "Ты серьезно?! Писать разучился?! \nНАПИШИ НАЗВАНИЕ ГОРОДА",
                           "Три, два, раз - с детства с рифмой я дружу. \nА ты не отвлекайся. Давай заново"]
        list_of_imgs = ["try_again.png", "try_again1.jpg", "try_again2.png", "try_again3.jpg", "try_again4.jpg"]
        image = random.choice(list_of_imgs)
        img = open(image, "rb")
        self.image = img.read()
        img.close()
        answer = random.choice(list_of_answers)
        return answer


    def weather_image(self):
        weather_images = {
            "Clouds": "cloudy_.jpg",
            "Snow": "snowy.jpg",
            "Rain": "rainy_day.jpg",
            "Thunderstorm": "thunder.jpg",
            "Clear": "sunny-day.jpg",
            "Fog": "Fog.jpg",
            "Mist": "Fog.jpg"
        }
        if self.data["list"][0]["weather"][0]["main"] in weather_images:
            img = open(weather_images[self.data["list"][0]["weather"][0]["main"]], "rb")
            self.image = img.read()
            img.close()


class ExchangeRate:
    def __init__(self, currencies: list):
        self.__data = self.data_parse()
        self.currencies = currencies

    def data_parse(self):
        currency = requests.get("https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json")
        data = currency.json()
        return data

    @property
    def exchange_rate(self):
        currencies_list = []
        for i in self.__data:
            if i["cc"] in self.currencies:
                idx = self.__data.index(i)
                text = self.__data[idx]["txt"]
                rate = self.__data[idx]["rate"]
                date = self.__data[idx]["exchangedate"]
                curr_rate = f"{text} / UAH: {rate}, {date}"
                currencies_list.append(curr_rate)
        what_to_send = "\n".join(currencies_list) + "\n" + 3 * "\U0001F601"
        return what_to_send


bot = telebot.TeleBot(token)


@bot.message_handler(commands=["start"])
def start_msg(message):
    bot.send_message(message.chat.id, "Здарова. Город напиши, а там поговорим...")


@bot.message_handler(content_types=["text"])
def send_data_to_bot(message):
    msg = message.text
    weather = Weather(msg)
    bot.send_message(message.chat.id, weather.weather_data)
    bot.send_photo(message.chat.id, weather.image)
    currency = ExchangeRate(["USD", "EUR", "PLN"])
    bot.send_message(message.chat.id, currency.exchange_rate)


if __name__ == '__main__':
    bot.polling()
