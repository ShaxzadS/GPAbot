import telebot

# Замените "YOUR_TOKEN" на ваш токен бота
token = "7084608381:AAFH4w3wwefTE52NsGsauklttZaml7MGhWw"
bot = telebot.TeleBot(token)

# Словарь для хранения информации о предметах и оценках для каждого пользователя
user_data = {}

# Список возможных оценок
grades_list = ['A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-', 'F']
def send_welcome(message):
    bot.reply_to(message, "Привет! Я бот для расчета GPA. Чтобы начать, нажмите на кнопку ниже.")

    # Create a keyboard for sending commands /subjects and /calculate
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2)
    subjects_button = telebot.types.KeyboardButton('/subjects')
    calculate_button = telebot.types.KeyboardButton('/calculate')
    markup.add(subjects_button, calculate_button)
    bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)

@bot.message_handler(commands=['subjects'])
def handle_command1(message):
    chat_id = message.chat.id
    user_data[chat_id] = {'current_index': 0, 'subjects': []}  # Initialize the list of subjects for the current user
    msg = bot.reply_to(message, "Введите количество предметов:")
    bot.register_next_step_handler(msg, process_subjects_count)

def process_subjects_count(message):
    chat_id = message.chat.id
    try:
        subjects_count = int(message.text)
        if subjects_count > 0:
            user_data[chat_id]['subjects'] = [{'subject': None, 'credits': None, 'grade': None} for _ in range(subjects_count)]
            msg = bot.send_message(chat_id, "Введите предмет:")
            bot.register_next_step_handler(msg, process_subject)
        else:
            bot.send_message(chat_id, "Количество предметов должно быть положительным числом. Попробуйте снова.")
    except ValueError:
        bot.send_message(chat_id, "Пожалуйста, введите число.")



def process_subject(message):
    chat_id = message.chat.id
    current_index = user_data[chat_id]['current_index']
    user_data[chat_id]['subjects'][current_index]['subject'] = message.text

    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, row_width=3)
    buttons = [telebot.types.KeyboardButton(grade) for grade in grades_list]
    markup.add(*buttons)
    msg = bot.send_message(chat_id, "Выберите оценку для этого предмета:", reply_markup=markup)
    bot.register_next_step_handler(msg, process_grade)

def process_grade(message):
    chat_id = message.chat.id
    current_index = user_data[chat_id]['current_index']
    grade = message.text
    if grade.upper() in grades_list:
        user_data[chat_id]['subjects'][current_index]['grade'] = grade.upper()
        msg = bot.send_message(chat_id, "Введите количество кредитов для этого предмета:")
        bot.register_next_step_handler(msg, process_credits)
    else:
        msg = bot.send_message(chat_id, "Пожалуйста, выберите оценку из предложенных кнопок.")
        bot.register_next_step_handler(msg, process_grade)



def process_credits(message):
    chat_id = message.chat.id
    current_index = user_data[chat_id]['current_index']
    try:
        credits = int(message.text)
        if credits > 0:
            user_data[chat_id]['subjects'][current_index]['credits'] = credits
            user_data[chat_id]['current_index'] += 1  # Move to the next subject
            if user_data[chat_id]['current_index'] < len(user_data[chat_id]['subjects']):
                msg = bot.send_message(chat_id, "Введите следующий предмет:")
                bot.register_next_step_handler(msg, process_subject)
            else:
                msg = bot.send_message(chat_id, "Все предметы введены. Для расчета GPA нажмите на кнопку /calculate.")
        else:
            bot.send_message(chat_id, "Количество кредитов должно быть положительным числом. Попробуйте снова.")
    except ValueError:
        bot.send_message(chat_id, "Пожалуйста, введите число.")


@bot.message_handler(commands=['calculate'])
def handle_command2(message):
    chat_id = message.chat.id
    if chat_id in user_data and 'subjects' in user_data[chat_id]:
        print(user_data[chat_id]['subjects'])  # Debug: Check the structure before calculation
        gpa = calculate_gpa(user_data[chat_id]['subjects'])
        bot.send_message(chat_id, f"Ваш общий GPA: {gpa:.2f}")
        user_data.pop(chat_id)  # Clear user data after GPA calculation
    else:
        bot.send_message(chat_id, "Вы еще не ввели данные о предметах. Нажмите на кнопку /subjects для начала.")


def calculate_gpa(subjects):
    total_points = 0
    total_credits = 0
    for subject in subjects:
        grade = subject['grade']
        credits = subject['credits']
        if grade == 'A':
            gpa = 4.0
        elif grade == 'A-':
            gpa = 3.7
        elif grade == 'B+':
            gpa = 3.3
        elif grade == 'B':
            gpa = 3.0
        elif grade == 'B-':
            gpa = 2.7
        elif grade == 'C+':
            gpa = 2.3
        elif grade == 'C':
            gpa = 2.0
        elif grade == 'C-':
            gpa = 1.7
        elif grade == 'D+':
            gpa = 1.3
        elif grade == 'D':
            gpa = 1.0
        elif grade == 'D-':
            gpa = 0.7
        elif grade == 'F':
            gpa = 0.0
        else:
            return None  # Если введена некорректная оценка, вернем None
        total_points += gpa * credits
        total_credits += credits

    if total_credits == 0:
        return 0.0
    else:
        return total_points / total_credits


bot.polling()
