import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, FSInputFile
from aiogram.utils.keyboard import ReplyKeyboardBuilder
import asyncio

API_TOKEN = "8204853417:AAGxkxgh1vDXujxCJtVOWDuEVbOEWYNqNqQ"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


class QuizStates(StatesGroup):
    playing = State()

QUIZ_DATA = [
    ("Спартанцы сбрасывали со скалы физически слабых новорожденных.", False),
    ("Греческие женщины могли быть полноправными гражданками и участвовать в голосовании.", False),
    ("Александр Македонский завоевал Персидскую империю.", True),
    ("В Древней Греции уже существовали общественные туалеты со сливом.", True),
    ("Троянская война была всего лишь мифом и не имела реальной исторической основы.", False),
    ("Древние греки использовали оливковое масло не только в пищу, но и как средство для гигиены тела.", True),
    ("Знаменитый храм Парфенон в Афинах изначально был раскрашен в яркие цвета.", True),
    ("Сократ был приговорен к смерти путем распятия.", False),
    ("Олимпийские игры проводились так долго, что на время их проведения прекращались все войны.", True),
    ("Древние греки не знали сахара и использовали для подслащивания пищи пчелиный мед.", True)
]


def get_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="✅ Правда"))
    builder.add(KeyboardButton(text="❌ Ложь"))
    builder.add(KeyboardButton(text="⏭ Пропустить вопрос"))
    builder.add(KeyboardButton(text="⏹ Завершить"))
    builder.adjust(2, 2)
    return builder.as_markup(resize_keyboard=True)


@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    hello_img = FSInputFile("hello.png")
    caption = "Меня зовут Ариша, и сегодня я предлагаю пройти тебе мой сложный тест и проверить свои знания в античной истории"
    await message.answer_photo(photo=hello_img, caption=caption)

    await state.set_state(QuizStates.playing)
    await state.update_data(current_question=0, score=0)

    question, _ = QUIZ_DATA[0]
    await message.answer(f"Вопрос 1/10:\n{question}", reply_markup=get_keyboard())


@dp.message(QuizStates.playing)
async def handle_answer(message: types.Message, state: FSMContext):
    data = await state.get_data()
    current_idx = data.get('current_question', 0)

    if message.text == "⏹ Завершить":
        await finish_quiz(message, state)
        return

    if current_idx >= len(QUIZ_DATA):
        await finish_quiz(message, state)
        return

    question_text, correct_answer = QUIZ_DATA[current_idx]
    score = data.get('score', 0)
    is_correct = False

    if message.text == "⏭ Пропустить вопрос":
        feedback = "⏭ Вопрос пропущен."
    elif message.text == "✅ Правда":
        if correct_answer:
            score += 1
            is_correct = True
            feedback = "✅ Верно!"
        else:
            feedback = "❌ Неверно!"
    elif message.text == "❌ Ложь":
        if not correct_answer:
            score += 1
            is_correct = True
            feedback = "✅ Верно!"
        else:
            feedback = "❌ Неверно!"
    else:
        feedback = "Пожалуйста, используйте кнопки для ответа."
        await message.answer(feedback, reply_markup=get_keyboard())
        return

    current_idx += 1
    await state.update_data(current_question=current_idx, score=score)

    await message.answer(feedback)

    if current_idx < len(QUIZ_DATA):
        next_question, _ = QUIZ_DATA[current_idx]
        await message.answer(f"Вопрос {current_idx + 1}/10:\n{next_question}", reply_markup=get_keyboard())
    else:
        await finish_quiz(message, state)


async def finish_quiz(message: types.Message, state: FSMContext):
    data = await state.get_data()
    score = data.get('score', 0)
    total = len(QUIZ_DATA)

    percentage = (score / total) * 100
    result_text = f"Квиз завершён!\nВаш результат: {score}/{total} ({percentage:.0f}%)\n\n"

    if percentage == 100:
        result_text += "🌟 Станьте моим правителем"
    elif percentage >= 70:
        result_text += "🎭 Достойный результат, сегодня без плетей"
    elif percentage >= 40:
        result_text += "🏛️ Неплохо, но в Спарте вас бы убили.."
    else:
        result_text += "🐢 Слабо..."

    await message.answer(result_text, reply_markup=ReplyKeyboardRemove())
    await state.clear()


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())