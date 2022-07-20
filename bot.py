import telebot
import mysql.connector
import json, time
from datetime import datetime
from config import TOKEN, PASSWORD_MYSQL
from telebot import types
from double_game import *

bot = telebot.TeleBot(TOKEN)

# Подключаемся к MySql
mydb = mysql.connector.connect(
    host="localhost",
    user="admin",
    password=PASSWORD_MYSQL,
    port="3306",
    database="telegram_users_data"
)

print(mydb)

cur = mydb.cursor(buffered=True)


# Кстати buffered=True очень важно на самом деле, потому что без этого, когда я пытался записать данные в BD,
# была ошибка — mysql.connector.errors.InternalError: Unread result found
# вот как мне это объяснили: buffered= True говорит, что cursor должен считывать результат каждый раз, когда он свежий,
# иначе с помощью метода fetchone(), cursor не будет считывать одни и те же данные снова и снова


# Создаем базу данных
# cur.execute("CREATE DATABASE telegram_users_data")

# Создаем таблицу users --------------- P.s. Это была 1 вариация таблицы, потом я поменял.
# cur.execute('CREATE TABLE users (id INT AUTO_INCREMENT PRIMARY KEY, user_id INT UNIQUE, '
#             'first_name VARCHAR(255), last_name VARCHAR(255))')

# Добавим запись в таблицу users
# sql = 'INSERT INTO users (user_id, first_name, last_name) VALUES (%s, %s, %s)'
# val = (1, 'Dmitrii', 'Usachev')
# cur.execute(sql, val)
# mydb.commit()
#
# print(cur.rowcount, 'Запись добавлена')

# Удалим данные с таблицы, для тестиков :)
# cur.execute('DELETE FROM users')
# mydb.commit()


# Дропнем таблицу, ибо я решил сделать регистрацию с email и password'ом.
# cur.execute('DROP TABLE users')
# mydb.commit()

# создадим новую таблицу в БД
# cur.execute('CREATE TABLE users (id INT AUTO_INCREMENT PRIMARY KEY, user_id BIGINT UNIQUE, '
#             'email VARCHAR(255) UNIQUE, password VARCHAR(255))')
# mydb.commit()

# Короче, мы можем ловить большие юзер_айдишники(оказывается у int'а есть предел и поэтому он не может принимать
# большие значения). Такими махинациями мы увеличили предел. 2147483647 — максимальное значение для INT —
# — отсюда и ошибка
# cur.execute('''ALTER TABLE users MODIFY user_id BIGINT''')  # BIGINT я изменил, когда создаём таблицу
# mydb.commit()

# user_data = dict()
# user_list = list()

# читаем наш json'чик
def read_json_file():
    with open('user_box.json', encoding='utf-8') as r:
        data = json.load(r)
        print(data)
    return data


# для более удобной работы
class User:
    def __int__(self):
        self.user_id = ''
        self.email = ''
        self.password = ''
        self.user_money = None
        self.json_file = None


user_data = User()


# Старт бота
@bot.message_handler(commands=['start', 'help'])
def start(message):
    keyboard = types.InlineKeyboardMarkup()

    key_registration = types.InlineKeyboardButton(text='Регистрация📨', callback_data='registration')
    keyboard.add(key_registration)

    key_login = types.InlineKeyboardButton(text='Вход в аккаунт📧', callback_data='login')
    keyboard.add(key_login)

    send_text = '[+] Вас приветствует игро-бот🎮.\n' \
                '[+] Пройдите регистрацию или зайдите в аккаунт!'

    bot.send_message(message.chat.id, text=send_text, reply_markup=keyboard)


# получаем почту пользователя и идём дальше
def give_email(message):
    msg_text = message.text

    query = "SELECT email FROM users WHERE email = %s"
    cur.execute(query, (msg_text,))
    row = cur.fetchone()
    print(row)
    if row is None:
        try:
            if "@" in msg_text and "[]!#$%^&*()_+=-?:;№<>,/`~\ " not in msg_text:
                user_data.email = msg_text
                msg = bot.send_message(message.chat.id, '[+] Теперь - придумайте пароль.')
                bot.register_next_step_handler(msg, password_by_email)
            else:
                msg = bot.send_message(message.chat.id, '[+] Не правильно написали почту.\n'
                                                        '\n'
                                                        '[+] Попробуйте еще раз!')
                bot.register_next_step_handler(msg, start)
        #         Да знаю что except Exception, это ужасно, но понял я это уже в конце проекта, когда ловил кучу,
        #         не понятных ошибок
        except Exception as e:
            bot.reply_to(message, 'ошибочка')
    else:
        msg = bot.reply_to(message, '[!] Данный email, уже зарегистрирован.\n'
                                    '\n'
                                    '[!] Попробуйте еще раз!')
        bot.register_next_step_handler(msg, give_email)


# получаем пароль и идем дальше
def password_by_email(message):
    user_id = message.from_user.id  # id пользователя
    password = message.text
    user_data.password, user_data.user_id = password, user_id
    add_data_users_in_db(message)


# Конечная регистрация пользователя, с записью в json его почты, времени создания и его начальном балансе
def add_data_users_in_db(message):
    sql = 'INSERT INTO users (user_id, email, password) VALUES (%s, %s, %s)'
    val = (user_data.user_id, user_data.email, user_data.password)
    cur.execute(sql, val)
    mydb.commit()

    time_create = str(datetime.now())

    user_data.user_money = 1000
    create_json_data = {
        'users': {user_data.email: {'information': {'money': user_data.user_money, 'time_create': time_create}}}}
    add_json_data = {user_data.email: {'information': {'money': user_data.user_money, 'time_create': time_create}}}
    try:
        with open('user_box.json', encoding='utf-8') as r:
            data = json.load(r)
            print(data)
            data['users'].update(add_json_data)
            with open('user_box.json', 'w', encoding='utf-8') as outfile:
                json.dump(data, outfile, indent=2, ensure_ascii=False)

        r.close(), outfile.close()
    except UnboundLocalError:
        with open('user_box.json', 'w', encoding='utf-8') as outfile:
            json.dump(create_json_data, outfile, indent=2, ensure_ascii=False)
            outfile.close()

    print(f'итоговый json:\n{data}')

    cur.execute("SELECT MAX(id) FROM users")
    max_id = cur.fetchone()

    print(max_id[0], 'Данные записаны!')
    bot.send_message(message.chat.id, '[!] Вы, успешно зарегистрированы!✅')


# Авторизация пользователя
def check_user(message):
    try:
        msg_text = message.text
        msg_text = msg_text.split(' ')
        query = "SELECT email, password FROM users WHERE email = %s"
        cur.execute(query, (msg_text[0],))
        row = cur.fetchone()
        if row is not None:
            if row[1] == msg_text[1]:
                keyboard = types.InlineKeyboardMarkup()

                key_profile = types.InlineKeyboardButton(text='Профиль💼', callback_data='profile')
                keyboard.add(key_profile)

                key_game_double = types.InlineKeyboardButton(text='Double🎲', callback_data='double_game')
                keyboard.add(key_game_double)

                user_data.email = msg_text[0]

                bot.send_message(message.chat.id, '[+] Авторизация прошла успешно.', reply_markup=keyboard)

            else:
                bot.reply_to(message, '[!] Проверьте, правильно ли вы написали почту/пароль!')
        elif row is None:
            bot.reply_to(message, '[!] Данная почта не зарегистрирована.')

    except IndexError:
        bot.reply_to(message, '[!] Проверьте, правильно ли вы написали почту/пароль')


# реализуем игру - double 🎲
def double_game(message):
    keyboard = types.InlineKeyboardMarkup()

    key_game_double = types.InlineKeyboardButton(text='Double🎲', callback_data='double_game')
    keyboard.add(key_game_double)

    try:
        random_number = return_number()
        print(random_number)
        with open('user_box.json', encoding='utf-8') as r:
            data = json.load(r)
            info_money = data['users'][user_data.email]["information"]["money"]
        msg_by_user = list(map(int, message.text.split(' ')))
        if msg_by_user[0] > info_money:
            big_money_msg = bot.send_message(message.chat.id, '[!] Вы ввели сумму больше, чем ваш баланс!')
            bot.register_next_step_handler(big_money_msg, double_game)
        elif msg_by_user[0] == random_number:
            # with open('user_box.json', encoding='utf-8') as r:
            #     data = json.load(r)
            new_money = data['users'][user_data.email]["information"]["money"] + msg_by_user[0] * msg_by_user[1]
            print(data)
            data['users'][user_data.email]["information"]["money"] = new_money
            with open('user_box.json', 'w', encoding='utf-8') as outfile:
                json.dump(data, outfile, indent=2, ensure_ascii=False)

            bot.send_message(message.chat.id, '[+] Ваша ставка зашла!')

            photo = open(f'photo_for_double/{random_number}.jpg', 'rb')
            bot.send_photo(message.chat.id, photo)
        else:
            with open('user_box.json', encoding='utf-8') as r:
                data = json.load(r)
                new_money = data['users'][user_data.email]["information"]["money"] - msg_by_user[1]
                print(data)
                data['users'][user_data.email]["information"]["money"] = new_money
                with open('user_box.json', 'w', encoding='utf-8') as outfile:
                    json.dump(data, outfile, indent=2, ensure_ascii=False)

            bot.send_message(message.chat.id, '[+] Ваша ставка не зашла!')
            bot.send_message(message.chat.id, f'[+] Выпало число: {random_number}')

            photo = open(f'photo_for_double/{random_number}.jpg', 'rb')
            bot.send_photo(message.chat.id, photo)
    except ValueError:
        msg = bot.send_message(message.chat.id, '[!] Вы не правильно ввели значения!')
        bot.register_next_step_handler(msg, double_game)
    finally:
        money = data['users'][user_data.email]["information"]["money"]
        if money <= 0:
            data['users'][user_data.email]["information"]["money"] = 100
            money = data['users'][user_data.email]["information"]["money"]
            with open('user_box.json', 'w', encoding='utf-8') as outfile:
                json.dump(data, outfile, indent=2, ensure_ascii=False)
            bot.send_message(message.chat.id, f'[!] Ваш баланс был 0 или ниже 0, но вам накинули соточку😉: {money}',
                             reply_markup=keyboard)
        else:
            bot.send_message(message.chat.id, f'[!] Ваш баланс: {money}', reply_markup=keyboard)
        outfile.close(), r.close()


# Кнопка стоп(Но, к сожалению она не работает как мне хочется P.s. И да я это не исправил...)
@bot.message_handler(commands=['stop'])
def stop_work_command(message):
    bot.send_message(message.chat.id, '[-] Вы остановили мою работу.⛔\n'
                                      '[+] Что-бы заново воспользоваться мной - нажмите на /start')


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == 'registration':
        msg = bot.send_message(call.message.chat.id, '[+] Вы выбрали регистрацию.\n'
                                                     '\n'
                                                     'Напишите ваш email.')
        bot.register_next_step_handler(msg, give_email)

    elif call.data == 'login':
        msg = bot.send_message(call.message.chat.id, '[!] Вы выбрали зайти в аккаунт.\n'
                                                     '\n'
                                                     'Напишите ваш email и пароль.\n'
                                                     '⬇Пример⬇\n'
                                                     'olya@mail.ru 123456789')
        bot.register_next_step_handler(msg, check_user)

    elif call.data == 'profile':
        user_data.json_file = read_json_file()
        info = f'[+] Money💸: {user_data.json_file["users"][user_data.email]["information"]["money"]}\n' \
               f'[+] Время создания🕔: {user_data.json_file["users"][user_data.email]["information"]["time_create"]}'
        print(info)

        bot.send_message(call.message.chat.id,
                         f'[+] Ваш профиль:\n{info}')
    elif call.data == 'double_game':
        user_data.json_file = read_json_file()
        info_money = f'[+] Ваш баланс: {user_data.json_file["users"][user_data.email]["information"]["money"]}'
        msg = bot.send_message(call.message.chat.id, f'{info_money}\n'
                                                     f'[!] Что-бы играть введите х который думаете(2, 3, 5, 50) '
                                                     f'и сумму ставки\n'
                                                     f'Пример:\n'
                                                     f'2 500\n'
                                                     f'[!] В случае выигрыша, та ставку которую вы поставили '
                                                     f'умножается на x и прибавляется к вашему балансу. Удачи!')
        bot.register_next_step_handler(msg, double_game)


bot.enable_save_next_step_handlers(delay=2)

bot.load_next_step_handlers()

if __name__ == '__main__':
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            time.sleep(3)
            print(e)
