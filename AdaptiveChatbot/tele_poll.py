from aiogram import types
from aiogram.types import PollType, PollOption

option1 = '😃'
option2 = '😐'
option3 = '🙁'
option4 = '😍'
option5 = '5⭐️'

# rating = types.Poll(question="Please choose a rating", options=[option1, option2, option3, option4, option5], type=PollType.REGULAR, is_anonymous = False)


async def start_poll():
        await callback.message.answer_poll(question='How was my response? Please give me a rating 😊',
                                        options=['5⭐️', '4⭐️',
                                                '3⭐️', '2⭐️', '1⭐️'],
                                        type='regular',
                                        explanation='hi',
                                        is_anonymous=False)