import os
import telebot
from dotenv import load_dotenv
from database import crud
from database.database_connector import get_session

load_dotenv()
# BOT URL https://t.me/way_to_a_bot
bot = telebot.TeleBot(os.environ.get("TELEGRAM_BOT_TOKEN"))

statuses = dict()


@bot.message_handler(commands=["start"])
def start_message(message):
    statuses[message.from_user.id] = "question"
    bot.send_message(message.chat.id, "Нажмите 1 если хотите узнать информацию о задаче\n"
                                      "Нажмите 2 если хотите составить контест")


@bot.message_handler()
def start_message(message: telebot.types.Message):
    if message.from_user.id not in statuses:
        statuses[message.from_user.id] = "question"
        bot.send_message(message.chat.id, "Нажмите 1 если хотите узнать информацию о задаче\n"
                                          "Нажмите 2 если хотите составить контест")
        return
    session = next(get_session())
    status = statuses[message.from_user.id]
    if status == "question":
        text = message.text.strip()
        if text == "1":
            statuses[message.from_user.id] = "task_info"
            bot.send_message(message.chat.id, "Введите номер задачи")
        elif text == "2":
            statuses[message.from_user.id] = "create_contest"
            bot.send_message(message.chat.id, "Введите тему и сложность из списка через пробел")
            tags_str = ""
            for tag_index, tag in enumerate(crud.get_tags(session)):
                tags_str += f"\n{tag_index}:\t{tag[0]}"
            bot.send_message(message.chat.id, tags_str[1:])
            complexity_str = ""
            for complexity_index, complexity in enumerate(crud.get_complexity(session)):
                complexity_str += f"\n{complexity_index}:\t{complexity[0]}"
            bot.send_message(message.chat.id, complexity_str[1:])
        else:
            bot.send_message(message.chat.id, "Бот не смог распознать ответ")
            statuses[message.from_user.id] = "question"
            bot.send_message(message.chat.id, "Нажмите 1 если хотите узнать информацию о задаче\n"
                                              "Нажмите 2 если хотите составить контест")
            return
    elif status == "task_info":
        problem = crud.get_problem_by_id(session, message.text.strip())
        tags = crud.get_problem_tags(session, problem.id)
        if problem is None:
            bot.send_message(message.chat.id, "Кажется такой задачи не существует")
        else:
            bot.send_message(message.chat.id,
                             f"Название: {problem.name};\tКоличество решивших: {problem.solve_count};\t"
                             f"Сложность {problem.complexity};\t{'Использовалась' if problem.is_used else 'Не использовалась'}")
            bot.send_message(message.chat.id,
                             f"Задача на темы: {', '.join(tags)}")
        statuses[message.from_user.id] = "question"
        bot.send_message(message.chat.id, "Нажмите 1 если хотите узнать информацию о задаче\n"
                                          "Нажмите 2 если хотите составить контест")
    elif status == "create_contest":
        tag, complexity = message.text.split()
        try:
            tag = crud.get_tag_by_name(session, tag)
            complexity = int(complexity)
            if tag is None or crud.check_complexity(session, complexity) is None:
                raise ValueError
        except ValueError:
            bot.send_message(message.chat.id, "Бот не смог распознать ответ")
            statuses[message.from_user.id] = "question"
            bot.send_message(message.chat.id, "Нажмите 1 если хотите узнать информацию о задаче\n"
                                              "Нажмите 2 если хотите составить контест")
            return
        problems = crud.get_problems(session, tag, complexity)
        bot.send_message(message.chat.id, f"Задачи:\t{' '.join(problems)}")
        statuses[message.from_user.id] = "question"
        bot.send_message(message.chat.id, "Нажмите 1 если хотите узнать информацию о задаче\n"
                                          "Нажмите 2 если хотите составить контест")
    else:
        bot.send_message(message.chat.id, "Бот не смог распознать ответ")
        statuses[message.from_user.id] = "question"
        bot.send_message(message.chat.id, "Нажмите 1 если хотите узнать информацию о задаче\n"
                                          "Нажмите 2 если хотите составить контест")


if __name__ == '__main__':
    bot.polling()
