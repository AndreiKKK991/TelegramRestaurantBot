import config
import telebot
from telebot import types
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class Booking(Base):
    __tablename__ = 'bookings'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    date_time = Column(DateTime, nullable=False)
    guests = Column(Integer, nullable=False)

engine = create_engine('sqlite:///restaurant.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

bot = telebot.TeleBot(config.token)

user_data = {}

MENU = {
    "🥗 Закуски":{
        "🍅Брускетта с томатами и базиликом": ("Bruscetta.jpg", "Брускетта с томатами и базиликом - 2000тг/шт"),
        "🐟Тартар из лосося с авокадо": ("Tartar.jpg", "Тартар из лосося с авокадо - 3600тг/шт"),
        "🧀Сырная тарелка (ассорти)": ("Chesse.jpg", "Сырная тарелка (ассорти) - 4250тг/шт"),
    },
    "🍝 Горячие блюда":{
        "🍝Паста карбонара": ("Pasta.jpg", "Паста карбонара - 3450тг/шт"),
        "🍄Ризотто с грибами и трюфельным маслом": ("Rizotto.jpg", "Ризотто с грибами и трюфельным маслом - 3850тг/шт"),
        "🥩Стейк рибай с соусом демиглас": ("Steak.jpg", "Стейк рибай с соусом демиглас - 7250тг/шт"),
    },
    "🍰 Десерты":{
        "🍰Тирамису": ("Teramisu.jpg", "Тирамису - 2100тг/шт"),
        "🥧Чизкейк Нью-Йорк": ("Kek.jpg", "Чизкейк Нью-Йорк - 2400тг/шт"),
        "🍨Мороженое (3 шарика на выбор)": ("Ice.jpg", "Мороженое (3 шарика на выбор) - 1750тг/шт"),
    },
    "🥤 Напитки":{
        "☕Капучино": ("Capuchino.jpg", "Капучино - 1100тг/шт"),
        "🍋Лимонад домашний": ("Limon.jpg", "Лимонад домашний - 1400тг/л"),
        "🍷Бокал вина (красное/белое)": ("Vino.jpg", "Бокал вина (красное/белое) - 2250тг/шт"),
    }
}

IMAGE_FOLDER = "C:/Users/WebUser/Desktop/Visual ST/TgRest/Photos/"

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет! Я бот для бронирования столиков в ресторане. Введите /book, чтобы забронировать столик.")


@bot.message_handler(commands=["help"])
def message_help(message):
    bot.send_message(message.chat.id, "/start - Начать\n" "/help - Все команды\n" "/schedule - Время работы\n" "/book - Начало бронирования\n" "/mybooking - Просмотреть текущие брони\n" "/cancel - Отменить бронь\n" "/menu - Посмотреть весь ассортимент\n" "/admin - Просмотреть все брони (только для админа)")


@bot.message_handler(commands=['schedule'])
def send_schedule(message):
    bot.send_message(message.chat.id, "Мы работаем:\nПН - 8:00 до 23:00\n"
                                                    "ВТ - 8:00 до 23:00\n"
                                                    "СР - 8:00 до 23:00\n"
                                                    "ЧТ - 8:00 до 23:00\n"
                                                    "ПТ - 8:00 до 23:00\n"
                                                    "СБ - Выходные\n"
                                                    "ВС - Выходные")


@bot.message_handler(commands=['book'])
def book(message):
    user_data[message.chat.id] = {}
    bot.send_message(message.chat.id, "Введите ваше имя:")
    bot.register_next_step_handler(message, get_name)

def get_name(message):
    user_data[message.chat.id]['name'] = message.text
    bot.send_message(message.chat.id, "Введите ваш номер телефона:")
    bot.register_next_step_handler(message, get_phone)

def get_phone(message):
    user_data[message.chat.id]['phone'] = message.text
    bot.send_message(message.chat.id, "Введите дату и время (в формате ГГГГ-ММ-ДД ЧЧ:ММ):")
    bot.register_next_step_handler(message, get_datetime)

def get_datetime(message):
    try:
        user_data[message.chat.id]['date_time'] = datetime.strptime(message.text, "%Y-%m-%d %H:%M")
        bot.send_message(message.chat.id, "Сколько гостей?")
        bot.register_next_step_handler(message, get_guests)
    except ValueError:
        bot.send_message(message.chat.id, "Неправильный формат даты. Введите снова (ГГГГ-ММ-ДД ЧЧ:MM).")
        bot.register_next_step_handler(message, get_datetime)

def get_guests(message):
    try:
        user_data[message.chat.id]['guests'] = int(message.text)
        data = user_data[message.chat.id]
        text = (f"Подтвердите бронь:\n"
            f"Имя: {data['name']}\n"
            f"Телефон: {data['phone']}\n"
            f"Дата и время: {data['date_time']}\n"
            f"Гостей: {data['guests']}\n\n"
            f"Введите 'Да' для подтверждения или 'Нет' для отмены.")
        markup = types.ReplyKeyboardMarkup(resize_keyboard = True, one_time_keyboard = True)
        markup.add("Да","Нет")
        bot.send_message(message.chat.id, text + "Подтвердить?", reply_markup=markup)
        bot.register_next_step_handler(message, confirm_booking)
    except ValueError:
        bot.send_message(message.chat.id, "Введите число гостей")
        bot.register_next_step_handler(message, get_guests)


def confirm_booking(message):
    if message.text.lower() == "да":
        session = Session()
        data = user_data[message.chat.id]
        booking = Booking(
            user_id=message.chat.id,
            name=data['name'],
            phone=data['phone'],
            date_time=data['date_time'],
            guests=data['guests']
        )
        session.add(booking)
        session.commit()
        session.close()
        bot.send_message(message.chat.id, "Бронирование завершено", reply_markup=types.ReplyKeyboardRemove())
    else:
        bot.send_message(message.chat.id, "Бронирование отменено", reply_markup=types.ReplyKeyboardRemove())


@bot.message_handler(commands=['mybooking'])
def my_booking(message):
    session = Session()
    booking = session.query(Booking).filter_by(user_id=message.chat.id).first()
    if booking:
        bot.send_message(message.chat.id, 
            f"Ваша бронь:\nИмя: {booking.name}\nТелефон: {booking.phone}\n"
            f"Дата и время: {booking.date_time}\nГостей: {booking.guests}")
    else:
        bot.send_message(message.chat.id, "У вас нет забронированных столиков")
    session.close()


@bot.message_handler(commands=['cancel'])
def cancel_booking(message):
    session = Session()
    booking = session.query(Booking).filter_by(user_id=message.chat.id).first()
    if booking:
        session.delete(booking)
        session.commit()
        bot.send_message(message.chat.id, "Ваша бронь отменена")
    else:
        bot.send_message(message.chat.id, "У вас нет забронированных столиков")
    session.close()


@bot.message_handler(commands=['admin'])
def admin_panel(message):
    session = Session()
    bookings = session.query(Booking).all()
    if bookings:
        text = "Список всех броней:\n\n"
        for b in bookings:
            text += f"ID: {b.id}, Имя: {b.name}, Тел: {b.phone}, Дата: {b.date_time}, Гостей: {b.guests}\n"
        bot.send_message(message.chat.id, text)
    else:
        bot.send_message(message.chat.id, "Сейчас нет активных броней")
    session.close()


@bot.message_handler(commands=["menu"])
def send_menu(message):
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    
    for category in MENU.keys():
        keyboard.add(types.KeyboardButton(category))

    bot.send_message(message.chat.id, "Выберите категорию:", reply_markup=keyboard)


@bot.message_handler(content_types=['text'])
def process_message(message):
    text = message.text.strip()
    
    if text in MENU:
        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        
        for item in MENU[text].keys():
            keyboard.add(types.KeyboardButton(item))

        bot.send_message(message.chat.id, f"Выберите товар из категории {text}:", reply_markup=keyboard)

    else:
        for category in MENU.values():
            if text in category:
                image_name, description = category[text]
                image_path = IMAGE_FOLDER + image_name

                with open(image_path, "rb") as file:
                    bot.send_photo(message.chat.id, file)

                bot.send_message(message.chat.id, description)
                return
            
    if message.text.lower() == "полное меню":
        file = open("C:/Users/WebUser/Desktop/Visual ST/TgRest/Menu/FullMenu.txt", "rb")
        bot.send_document(message.chat.id, file)
        bot.send_message(message.chat.id, "Вот полное меню")


if __name__ == "__main__":
    bot.infinity_polling()