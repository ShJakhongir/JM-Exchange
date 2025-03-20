from aiogram import types, F, Router #Router для замены dp , чтобы программа знала где хендлеры
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.database.db import create_order
from app.database.db import init_db
from app.database.db import register_user
from app.database.db import get_user_count
import app.keyboard as kb
import aiohttp
import uuid

router = Router()
API_KEY = "Ug9Z67HybDWc4vcm7dABjitoicgf2xKF7YrGMFJ8tfNhViZPeNVCE36ife6FjkBN"

@router.message(CommandStart())
async def main_start(message: Message):
    init_db() #для отслеживание кол-во пользователей в боте
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    register_user(user_id, username, first_name, last_name)
    await message.reply(f"Приветствую {message.from_user.first_name}👋!\nНажмите кнопку ниже чтобы узнать актуальные курсы", 
                        reply_markup= kb.main)

@router.message(Command('user_count'))
async def cmd_user_count(message: types.Message):
    user_count = get_user_count()
    await message.answer(f"Количество пользователей в боте: {user_count}")

@router.callback_query(F.data == 'change')
async def change_main(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.edit_text('📍Выберите токен для уточнения курса', 
                                     reply_markup= await kb.reply_change_course())
    

async def get_price(symbol: str):
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}USDT"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            return float(data["price"])


class BuyTONState(StatesGroup):
    waiting_ton_quantity = State()

@router.callback_query(F.data == "Actual_course_💎Ton")
async def show_ton_course(callback: CallbackQuery,state: FSMContext):
    await callback.message.edit_text("🗳Введите количество TON, которые хотите купить" , reply_markup= kb.command_exit)
    await state.set_state(BuyTONState.waiting_ton_quantity)
    await state.update_data(callback_message=callback.message.message_id)

@router.message(BuyTONState.waiting_ton_quantity)
async def calculate_ton_price(message: types.Message, state: FSMContext):
    try:
        quantity_ton = float(message.text)
        price = await get_price('TON')
        if price > 0:
            result_ton = (((quantity_ton * price) + quantity_ton * price * 0.1) * 87 )

            await state.set_state(BuyTONState.waiting_ton_quantity)

            await state.update_data(
                quantity=quantity_ton,
                total=result_ton,
                currency="RUB",
                token="TON"
            )

            data = await state.get_data()
            print("Сохраненные данные Stars:", data)
            await message.answer(f"🔺За {quantity_ton} TON, вы заплатите: {result_ton:.2f} рублей",  reply_markup=kb.command_exit_2)
        else:
            await message.answer("Ошибка: курс TON недоступен", reply_markup=kb.command_exit)
    except ValueError:
        await message.answer("Пожалуйста, введите корректное число.", reply_markup=kb.command_exit)


#Price for stars 
class BuyStarsState(StatesGroup):
    waiting_for_quantity = State()

@router.callback_query(F.data == 'Actual_course_🌟Stars')
async def ask_quantity(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("🗳Введите количество Stars, которые хотите купить:",reply_markup=kb.command_exit)
    await state.set_state(BuyStarsState.waiting_for_quantity)
    await state.update_data(callback_message=callback.message.message_id)

@router.message(BuyStarsState.waiting_for_quantity)
async def calculate_price(message: types.Message, state: FSMContext):
    try:
        quantity = float(message.text)

        if 50 <= quantity < 500:
            result = (quantity / 50) * 85
        elif 500 <= quantity < 3000 :
            result = (quantity / 50) * 82.5
        elif quantity >= 3000 :
            result = (quantity / 50) * 80
        else:
            await message.answer("Ошибка: курс Stars недоступен. Минимальная кол-во 50 звёзд", reply_markup=kb.command_exit)
            return 
        
        await state.set_state(BuyStarsState.waiting_for_quantity)

        await state.update_data(
            quantity=quantity,
            total=result,
            currency="RUB",
            token="Stars"
        )

        data = await state.get_data()
        print("Сохраненные данные Stars:", data)

        await message.answer(f"🔺За {quantity} Stars, вы заплатите: {result:.2f} рублей", reply_markup=kb.command_exit_2)

    except ValueError:
        await message.answer("Пожалуйста, введите корректное число.", reply_markup=kb.command_exit)


@router.callback_query(F.data == 'buy_now')
async def buy_now(callback: CallbackQuery, state: FSMContext):
   await callback.message.edit_text("Выберите способ оплаты:", reply_markup=kb.payment_keyboard)
   await callback.answer('')
   

#Оплата по карте
@router.callback_query(F.data == 'pay_card')
async def process_pay_card(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data() 
    print("Данные перед оплатой картой:", data)

    if not data:
        await callback.answer("Ошибка: нет данных о заказе. Попробуй заново.", show_alert=True)
        return

    user_id = callback.from_user.id
    quantity = data.get("quantity")
    total = data.get("total")
    currency = data.get("currency")
    token = data.get("token")

    if not quantity or not total:
        await callback.answer("Ошибка: данных недостаточно. Попробуй заново.", show_alert=True)
        return

    order_id = str(uuid.uuid4()).split('-')[0]

    create_order(
        user_id=user_id,
        order_id=order_id,
        amount=total  
    )

    CARD_NUMBER = "2202 2009 0516 7118"
    CARD_NAME = "Тахмина Ш"

    payment_text = (
        f"✅ Заказ оформлен!\n\n"
        f"Вы покупаете: {quantity} {token}\n"
        f"К оплате: {total:.4f} {currency}\n\n"
        f"💳 Реквизиты для оплаты:\n"
        f"Карта Сбербанк: `{CARD_NUMBER}`\n\n"
        f"Получатель: {CARD_NAME}\n\n"
        f"❗️ Обязательно укажите комментарий к переводу:\n"
        f"`{order_id}`\n\n"
        f"⚠️ Без комментария или с неверным номером заказа перевод не будет обработан!"
       
    )
    await callback.message.edit_text(payment_text, parse_mode= "Markdown", reply_markup=kb.paid_main)
    await callback.answer()

@router.callback_query(F.data == 'paid')
async def paid_call(callback: CallbackQuery):
    await callback.message.answer('🧾Отправьте чек оплаты нашему менеджеру\nМенеджер сразу с вами свяжется и подтвердит оплату❗️', reply_markup=kb.manager_callback)

@router.callback_query(F.data == "Actual_course_Назад")
async def exit_command(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.edit_text(f"✨Нажми кнопку ниже чтобы узнать актуальные курсы", 
                                     reply_markup=kb.main)
    

@router.callback_query(F.data == "Exit")
async def exit_command(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.edit_text('📍Выберите токен для уточнения курса', 
                                     reply_markup= await kb.reply_change_course())
    

@router.callback_query(F.data == "Exit_2")
async def exit_command(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.edit_text('📍Выберите токен для уточнения курса', 
                                     reply_markup= await kb.reply_change_course())
    

@router.callback_query(F.data == "pay_exit")
async def exit_command(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.edit_text('📍Выберите токен для уточнения курса', 
                                     reply_markup= await kb.reply_change_course())
    


