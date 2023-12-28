from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext

# startup inline keyboard
start_up_keyboard = types.InlineKeyboardMarkup(row_width=1)
btn_bot = types.InlineKeyboardButton("Start Chatbot 🤖", callback_data="bot")
btn_feedback = types.InlineKeyboardButton("Leave a Feedback 👍", callback_data="feedback")
btn_contact = types.InlineKeyboardButton("Contact Us 📞", callback_data="contact")
start_up_keyboard = types.InlineKeyboardMarkup(row_width=1).add(btn_bot, btn_feedback, btn_contact)

# inline buttons
qna_keyboard = types.InlineKeyboardMarkup(row_width=2)
btn_review = types.InlineKeyboardButton("Review answer ⭐️", callback_data="btn_review")
btn_end_qna = types.InlineKeyboardButton("End chat 👋", callback_data="btn_end_qna")
qna_keyboard.add(btn_review, btn_end_qna)

# async def on_callback_query(callback: types.CallbackQuery, state: FSMContext):
#     if callback.data == "btn_review":
#         await state.set_state('feedback_comments') # set state
#         await callback.message.answer_chat_action("typing", callback.message.message_thread_id)
#         await callback.message.answer("Please select your rating")
#         await callback.message.answer_poll(question='How was my response? Please give me a rating 😊',
#                                            options=['5⭐️', '4⭐️',
#                                                     '3⭐️', '2⭐️', '1⭐️'],
#                                            type='regular',
#                                            explanation='hi',
#                                            is_anonymous=False)
#     if callback.data == "btn_end_qna":
#         await callback.message.answer_chat_action("typing", callback.message.from_id)
#         await ChatBot.main.set()
#         await bot.send_message(callback.from_user.id, "Exited QNA session, going into main session")
#     await callback.answer()