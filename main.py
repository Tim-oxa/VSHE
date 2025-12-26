from aiogram import Bot, Dispatcher
from aiogram.types import *
from remnawave_api import remna
from remnawave.exceptions import NotFoundError
from remnawave.models.users import CreateUserRequestDto
from datetime import timedelta
from config import *
import asyncio
from webapp import run_webapp


bot = Bot(BOT_TOKEN)
dp = Dispatcher()


@dp.message()
async def on_message(message: Message):
    try:
        remna_user = await remna.users.get_user_by_username(f"p{message.from_user.id}")
    except NotFoundError:
        remna_user = await remna.users.create_user(CreateUserRequestDto(
            username=f"p{message.from_user.id}",
            expire_at=message.date + timedelta(hours=3),
            traffic_limit_bytes=(1024 ** 3) * 1,
            active_internal_squads=[REMNA_SQUAD]
        ))
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Подключить прокси", url=remna_user.subscription_url)],
        [InlineKeyboardButton(text="Посмотреть логи", web_app=WebAppInfo(url=WEBAPP_URL+"/"+remna_user.short_uuid))]
    ])
    await message.answer(
        "Привет! 👋 Подключись к прокси и попробуй зайти на любой сайт, а потом посмотри логи/информацию, которые удалось по тебе собрать.",
        reply_markup=kb
    )


async def main():
    await asyncio.gather(
        dp.start_polling(bot),
        run_webapp()
    )


if __name__ == "__main__":
    asyncio.run(main())
