from aiogram.types import BotCommand, KeyboardButton

BOT_COMMANDS: list[BotCommand] = [
    BotCommand(command="/echo", description="Тестовая команда"),
    BotCommand(command="/support", description="Обращение в поддержку"),
    BotCommand(command="/vacancy", description="Наши вакансии"),
]

START_MESSAGE = """
Привет!
Я xi.supbot!
"""

MAIN_MENU_BUTTON_TEXT = "📋 Главное меню"

START_SUPPORT_MESSAGE = """
Пожалуйста, опишите вашу проблему
"""

WAIT_SUPPORT_MESSAGE = """
Ваше обращение направлено в поддержку
Совсем скоро с вами свяжутся
Ожидайте...
"""

EXIT_SUPPORT_MESSAGE = """
Обращение успешно закрыто
"""

BASE_URL = "https://www.t.me"

BACK_BUTTON_TEXT = "Назад"
SKIP_BUTTON_TEXT = "Пропустить"

# Vacancy Form Start
XI_EFFECT_VACANCY_FORM_URL = "https://vacancy.xieffect.ru/vacancy"
EXIT_VACANCY_FORM_MESSAGE = "Будем ждать вас снова!"
STARTING_VACANCY_FORM_MESSAGE = f"""
Вы можете выбрать интересующую вакансию
через бота или по ссылке {XI_EFFECT_VACANCY_FORM_URL}
"""
CHOOSE_VACANCY_MESSAGE = "Выберите вакансию или введите свою"
SEND_NAME_MESSAGE = "Как к вам можно обращаться?"
SEND_TELEGRAM_MESSAGE = "Ваш телеграм для обратной связи"
SEND_RESUME_MESSAGE = "Ссылка на ваше резюме"
SEND_INFO_MESSAGE = "Почти готово. Можете оставить для нас сообщение :)"
VACANCY_FORM_FINAL_MESSAGE = "Спасибо! Мы обязательно рассмотрим ваш отклик и ответим."

CONTINUE_IN_BOT_KEYBOARD_TEXT = "Продолжить через бота"
VACANCY_FORM_EPILOGUE_KEYBOARD_MARKUP: list[list[KeyboardButton]] = [
    [
        KeyboardButton(text=CONTINUE_IN_BOT_KEYBOARD_TEXT),
        KeyboardButton(text=MAIN_MENU_BUTTON_TEXT),
    ],
]

NAVIGATION_KEYBOARD_MARKUP: list[list[KeyboardButton]] = [
    [KeyboardButton(text=BACK_BUTTON_TEXT), KeyboardButton(text=MAIN_MENU_BUTTON_TEXT)]
]

NAVIGATION_KEYBOARD_MARKUP_WITH_SKIP: list[list[KeyboardButton]] = [
    [KeyboardButton(text=SKIP_BUTTON_TEXT)],
    *NAVIGATION_KEYBOARD_MARKUP,
]

VACANCIES = [
    "Frontend разработчик",
    "Backend разработчик",
    "Графический дизайнер",
    "Product manager",
    "SMM-специалист",
]
CHOOSE_VACANCY_KEYBOARD_MARKUP: list[list[KeyboardButton]] = [
    *[[KeyboardButton(text=VACANCY)] for VACANCY in VACANCIES],
    *NAVIGATION_KEYBOARD_MARKUP,
]

LEAVE_CURRENT_ACCOUNT_BUTTON_TEXT = "Оставить свой текущий аккаунт"
SEND_TELEGRAM_KEYBOARD_MARKUP: list[list[KeyboardButton]] = [
    [KeyboardButton(text=LEAVE_CURRENT_ACCOUNT_BUTTON_TEXT)],
    *NAVIGATION_KEYBOARD_MARKUP,
]
# Vacancy Form End
