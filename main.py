import sqlite3
import telebot
import config


# Инициализация бота с токеном
bot = telebot.TeleBot(config.TOKEN)

# Подключение к базе данных
conn = sqlite3.connect('todo.db', check_same_thread=False)
cursor = conn.cursor()

# Создание таблицы задач в базе данных
cursor.execute('''CREATE TABLE IF NOT EXISTS tasks
                  (id INTEGER PRIMARY KEY AUTOINCREMENT,
                   task_id INTEGER,
                   chat_id INTEGER,
                   task_text TEXT, 
                   reminder_time DATETIME)''')
conn.commit()


# Обработка команды /start
@bot.message_handler(commands=['start'])
def start(message):
    global chat_id_p
    bot.reply_to(message, "Привет! Я бот To Do List. Напиши /newtask для добавления новой задачи.")
    chat_id_p = message.chat.id

# Обработка команды /newtask
@bot.message_handler(commands=['newtask'])
def new_task(message):
    global chat_id_p
    bot.reply_to(message, "Напиши новую задачу:")
    bot.register_next_step_handler(message, add_task)
    chat_id_p = message.chat.id

# Функция добавления новой задачи
def add_task(message):
    global task_id_mes
    task_id_mes = ''
    task_text = message.text
    cursor.execute("SELECT MAX(task_id) FROM tasks WHERE chat_id = ?", (chat_id_p,))
    last_id = cursor.fetchone()[0] or 0
    cursor.execute("INSERT INTO tasks (chat_id, task_text, task_id) VALUES (?,?,?)", (chat_id_p, task_text, last_id + 1))
    conn.commit()
    bot.reply_to(message, "Задача добавлена.")

# Обработка команды /showtasks
@bot.message_handler(commands=['showtasks'])
def student_list_def (message):
    global chat_id_p
    chat_id_p = message.chat.id
    db = sqlite3.connect('todo.db',check_same_thread=False)
    c = db.cursor()

    cursor.execute("SELECT MAX(task_id) FROM tasks WHERE chat_id = ?", (chat_id_p,))
    last_id = cursor.fetchone()[0] or 0
    if last_id == 0:
        bot.send_message(message.chat.id, "В вашем списке задач нет задач");
        db.close()
    else:
        bot.send_message(message.chat.id, "Ваш список задач");
        c.execute("SELECT task_id,task_text FROM tasks WHERE chat_id = ?", (chat_id_p,))
        conn.commit()
        rows = c.fetchall()
        result_str = '\n'.join(map(str, rows))
        result_str = result_str.replace('(','')
        result_str = result_str.replace(')', '')
        result_str = result_str.replace("'", '')
        result_str = result_str.replace('"', '')
        bot.send_message(message.chat.id, result_str)
        db.close()

# Обработка команды /deletetask
@bot.message_handler(commands=['deletetask'])
def delete_task(message):
    bot.reply_to(message, "Напиши номер задачи, которую нужно удалить:")
    bot.register_next_step_handler(message, remove_task)

# Функция удаления задачи
def remove_task(message):
    global chat_id_p
    chat_id_p = message.chat.id
    task_id_mes= message.text
    cursor.execute("SELECT MAX(task_id) FROM tasks WHERE chat_id = ?", (chat_id_p,))
    last_id = cursor.fetchone()[0] or 0

    if  task_id_mes.isdigit():
        task_id_mes = int(task_id_mes)
        last_id = int(last_id)
        if task_id_mes == 0 or last_id < task_id_mes or task_id_mes < 0:
            bot.reply_to(message, "Такой задачи нет. Напиши /deletetask если хотет удалить задачу.")
        else:
            cursor.execute("DELETE FROM tasks WHERE task_id=?", (task_id_mes,))
            cursor.execute("UPDATE tasks SET task_id = task_id - 1 WHERE task_id > ?", (task_id_mes,) )
            conn.commit()
            bot.reply_to(message, "Задача удалена.")
    else:
        bot.reply_to(message, "Вы ввели не число. Напиши /deletetask если хотет удалить задачу.")


bot.polling()
