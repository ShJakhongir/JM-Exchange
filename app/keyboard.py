from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton, 
                           InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

main = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text = '🧬Узнать курс', callback_data='change')],
    [InlineKeyboardButton(text = 'Наши отзывы', url = 'https://t.me/mukhammad_otzyvi')]

])


main_token = ["🌟Stars", "💎Ton", "Назад"]
async def reply_change_course():
    keyboard = InlineKeyboardBuilder()
    for changes in main_token:
        keyboard.add(InlineKeyboardButton(text=changes , callback_data=f'Actual_course_{changes}'))  #также можно сделать с inline 
    return keyboard.adjust(2).as_markup() 


command_exit = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text = "🔙Назад в меню", callback_data='Exit')]
])

command_exit_2 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text = "Купить сейчас", callback_data= 'buy_now')],
    [InlineKeyboardButton(text = "🔙Назад в меню", callback_data='Exit_2')]
]) 


payment_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="💳Оплатить по карте", callback_data="pay_card")],
    [InlineKeyboardButton(text = "Оплатить по СБП", callback_data= 'pay_sbp')],
    [InlineKeyboardButton(text = "🔙Назад", callback_data="pay_exit")]
])


paid_main = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text = "Ввести промокод", callback_data= 'promo')],
    [InlineKeyboardButton(text = "✅Оплачено!", callback_data='paid')]
])

manager_callback = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text = "🧑‍💻Связаться с менеджером", url = "https://t.me/matyshen")]
])


paid_main_two = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text = "✅Оплачено!", callback_data='paid_two')]
])
