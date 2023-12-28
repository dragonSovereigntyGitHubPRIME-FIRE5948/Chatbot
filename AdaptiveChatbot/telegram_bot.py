import os
from dotenv import load_dotenv
import time
import tempfile
from pydub import AudioSegment
from pathlib import Path
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Button, Row, Column
from aiogram_dialog.widgets.text import Const
from aiogram_dialog import Dialog
from aiogram_dialog import DialogRegistry
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode
from aiogram.types import CallbackQuery
import tele_inline_keyboard as KeyboardUtils
import tele_poll as PollUtils
import email_utils
import llm_utils
import openai
import config
import firebase_utils
import openai_utils

# Inner Class: States
class ChatBot(StatesGroup):
    Main = State()  
    ChatBot = State()
    SendEmail = State()
    SendFeedback = State()
    feedback_comments = State()
    feedback_rating = State()

class FeedbackForm(StatesGroup):
    FeedbackEmail = State()
    FeedbackUnanswered = State()
    FeedbackMessage = State()
    FeedbackRating = State()
    FeedbackComplete = State()

WELCOME_MESSAGE = """
Hello! My name is AdaptiveChatbot.

I can answer your queries on AdaptiveBizapp's software. How may I help you today? 😄
"""

bot = Bot(token=config.tele_token)
openai.api_key = config.marcus_openai_api

dp = Dispatcher(
    bot, 
    storage=MemoryStorage()
)

# init llm_utils object
chat_bot = llm_utils.chat_bot()
# init firebase db
fb = firebase_utils.FirebaseDB()

# Welcome Message [/start]
@dp.message_handler(state='*', commands=['start'])
async def welcome_handler(message: types.Message):
    # send welcome message
    ChatBot.Main.set()
    await message.answer_chat_action("typing", message.from_id)
    await message.reply(WELCOME_MESSAGE, reply_markup=KeyboardUtils.start_up_keyboard)

# Handler [state=Main]
@dp.message_handler(state=ChatBot.Main)
async def welcome_handler(message: types.Message):
    await message.answer_chat_action("typing", message.from_id)
    await message.reply("Please choose an option", reply_markup=KeyboardUtils.start_up_keyboard)

# Inline Keyboard Handler: start_up_keyboard
@dp.callback_query_handler(text=["bot", "feedback", "contact"], state="*")
async def on_callback_query(callback: types.CallbackQuery):
    # chatbot
    if callback.data == "bot":
        await callback.message.answer_chat_action("typing", callback.message.from_id)
        time.sleep(1)
        ChatBot.ChatBot.set()
        await bot.send_message(callback.from_user.id, "Please feel free to ask me anything regarding AdaptiveBizapp, I would be more than happy to help")
    # feedback
    if callback.data == "feedback":
        # set state
        await FeedbackForm.FeedbackUnanswered.set()
        await callback.message.answer_chat_action("typing", callback.message.from_id)
        time.sleep(1)
        await bot.send_message(callback.from_user.id, "Please enter your email.")
    # contact
    if callback.data == "contact":
        await callback.message.answer_chat_action("typing", callback.message.from_id)
        time.sleep(1)
        await email_utils.send_email()
        await bot.send_message(callback.from_user.id, "Email Sent")
    await callback.answer()

# Feedback State #
# unanswered
@dp.message_handler(state=FeedbackForm.FeedbackUnanswered, content_types=types.ContentTypes.TEXT)
async def enter_my_email(message: types.Message, state: FSMContext):
    await FeedbackForm.next()
    # get email
    async with state.proxy() as data:
        data['FeedbackEmail'] = message.text

    await message.answer_chat_action("typing", message.message_thread_id)
    await message.answer("Please the question(s) which you didn't like the response of.")
# feedback
@dp.message_handler(state=FeedbackForm.FeedbackMessage, content_types=types.ContentTypes.TEXT)
async def enter_my_email(message: types.Message, state: FSMContext):
    # get unanswered
    await FeedbackForm.next()
    async with state.proxy() as data:
        data['FeedbackUnanswered'] = message.text
    await message.answer_chat_action("typing", message.message_thread_id)
    await message.answer("Please enter your feedback.")
# rating
@dp.message_handler(state=FeedbackForm.FeedbackRating, content_types=types.ContentTypes.TEXT)
async def enter_my_email(message: types.Message, state: FSMContext):
    await FeedbackForm.next()
    async with state.proxy() as data:
        data['FeedbackMessage'] = message.text
    await message.answer_chat_action("typing", message.message_thread_id)
    await message.answer("Please enter your rating.")
# complete
@dp.message_handler(state=FeedbackForm.FeedbackComplete, content_types=types.ContentTypes.TEXT)
async def enter_my_email(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['FeedbackRating'] = int(message.text)

    await message.answer_chat_action("typing", message.message_thread_id)

    # firebase
    feedback_id = fb.set_feedback(
        email=data['FeedbackEmail'],
        unanswered=data['FeedbackUnanswered'],
        feedback=data['FeedbackMessage'],
        rating=data['FeedbackRating']
    )

    # email sent to user
    email_utils.send_email(
        subject="Received: Feedback "+str(feedback_id),
        recipient=data['FeedbackEmail'],
        content=f"""
            Thank you for your feedback.

            Questions not Answered: {data['FeedbackUnanswered']}
            Feedback: {data['FeedbackMessage']}
            Rating: {data['FeedbackRating']}

            We have received it and will get back to you ASAP, please hang tight!
        """,
    )

    await message.answer("Thank you for your feedback! Your feedback has been submitted successfully. 😄")
    await message.answer("How else may I help you?", reply_markup=KeyboardUtils.start_up_keyboard)
    await ChatBot.Main.set()
    # Finish conversation
    await state.finish()

###########
# ChatBot #
###########

# chat
######change
# @dp.message_handler(state=ChatBot.ChatBot, content_types=types.ContentTypes.TEXT)
@dp.message_handler(state='*', content_types=types.ContentTypes.TEXT)
async def qna_message_handler(message: types.Message):
    
    # validate_input = openai_utils.check_moderation(message.text)

    # if validate_input == True:
        try:
            # query the doc index
            # await bot.send_chat_action(chat_id=chat_id, action=telegram.constants.ChatAction.TYPING)
            await message.answer_chat_action("typing", message.message_thread_id)
            reply = chat_bot.chat(message.text)
            await message.answer(reply, 
                                #  reply_markup=KeyboardUtils.qna_keyboard
                                )
        except Exception as e:
            await message.answer("I apologise, but there were some errors with your message 🥲. Please retry!")
            raise Exception(f"Text Message: {e}")
    # else:
        # await message.answer_chat_action("typing", message.message_thread_id)
        # reply = chat_bot.chat("I apologise, but it seems like you might have some inputs that goes against our policies 😲. Please retry!")

# callback onclick inline button
@dp.callback_query_handler(text=["btn_review", "btn_end_qna"], state=ChatBot.ChatBot)
async def on_callback_query(callback: types.CallbackQuery):
    if callback.data == "btn_review":
        await ChatBot.feedback_comments.set()  # set state
        await callback.message.answer_chat_action("typing", callback.message.message_thread_id)
        time.sleep(1)
        await callback.message.answer("Please select your rating")
        await callback.message.reply_poll(question=PollUtils.rating.question, options=PollUtils.rating.options, type=PollUtils.rating.type, is_anonymous=PollUtils.rating.is_anonymous)
    if callback.data == "btn_end_qna":
        await callback.message.answer_chat_action("typing", callback.message.from_id)
        await ChatBot.Main.set()
        await bot.send_message(callback.from_user.id, "Exited QNA session, going into main session")
    await callback.answer()

# voice
@dp.message_handler(state='*', content_types=types.ContentTypes.VOICE | types.ContentType.AUDIO)
async def voice_message_handler(voice_message: types.Message):
    # print(voice_message.voice.values)
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_dir = Path(tmp_dir)
        voice_ogg_path = tmp_dir / "voice.ogg"
        # get file
        voice_file = await bot.get_file(voice_message.voice.file_id)
        # get file path
        file_path = voice_file.file_path
        # download file
        await bot.download_file(file_path, voice_ogg_path)
        # convert to mp3
        voice_mp3_path = tmp_dir / "voice.mp3"
        # AudioSegment.converter = '/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/site-packages/pydub' 
        AudioSegment.from_file(voice_ogg_path).export(voice_mp3_path, format="mp3")
        # transcribe
        with open(voice_mp3_path, "rb") as f:
            # transcribed_text = await openai_utils.transcribe_audio(f)
            transcript = openai.Audio.transcribe("whisper-1", f)

            if transcript is None:
                transcript = ""
        
        reply = chat_bot.chat(transcript)
        await voice_message.answer_chat_action("typing", voice_message.message_thread_id)
        await voice_message.reply(reply, 
                                #   reply_markup=KeyboardUtils.qna_keyboard
                                  )
# unhappy

# Handler for message types that are not covered
@dp.message_handler(state='*', content_types=types.ContentTypes.ANY )
async def bad_input_handler(message: types.Message):
    try:
        await message.answer_chat_action("typing", message.message_thread_id)
        await message.answer("I apolgise, but I am unable to recognise this type of message 😅. Please retry!")
    except Exception as e:
        await message.answer("I apologise, but there were some errors with your message 🥲. Please retry!")
        raise Exception(f"Message: {e}")

# @dp.message_handler(state=ChatBot.review_rating)
# async def gpt(message: types.Message):
#     # await state.set_state("")
#     await ChatBot.review_comments.set()

@dp.message_handler(state=ChatBot.feedback_comments)
async def gpt(message: types.Message):
    # set state here
    await message.answer_chat_action("typing", message.message_thread_id)
    await message.answer("Please enter your comments")


@dp.poll_answer_handler()
async def poll_answer(poll_answer: types.PollAnswer):
    # this handler starts after user choosed any answer
    answer_ids = poll_answer.option_ids[0]  # list of answers
    user_id = poll_answer.user.id
    poll_id = poll_answer.poll_id
    await bot.send_message(user_id, "thankyoiu")


@dp.message_handler(state='*', commands=['finish'])
async def cancel_handler(message: types.Message, state: FSMContext):
    """Allow user to cancel action via /cancel command"""
    # current_state = await state.get_state()
    # if current_state is None:
    #     # User is not in any state, ignoring
    #     return

    # Cancel state and inform user about it
    await state.finish()
    await message.reply('Cancelled.')

if __name__ == "__main__":
    # register_handlers_client(dp)
    executor.start_polling(dp, skip_updates=True)
