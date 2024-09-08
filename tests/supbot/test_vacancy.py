from typing import Any

import pytest
from aiogram.fsm.state import State
from aiogram.fsm.storage.base import BaseStorage, StorageKey
from aiogram.methods import SendMessage
from aiogram.types import Chat, InputMediaDocument, InputMediaPhoto, InputMediaVideo
from faker import Faker
from pydantic_marshals.contains import assert_contains

from app.supbot import texts
from app.supbot.routers.vacancy_tgm import VacancyStates
from app.users.routes.forms_rst import VacancyFormSchema
from tests.common.mock_stack import MockStack
from tests.supbot.conftest import (
    EXPECTED_MAIN_MENU_KEYBOARD_MARKUP,
    MockedBot,
    WebhookUpdater,
)
from tests.supbot.factories import MessageFactory, UpdateFactory, UserFactory

NAVIGATION_KEYBOARD_MARKUP = {
    "keyboard": [
        [{"text": texts.BACK_BUTTON_TEXT}, {"text": texts.MAIN_MENU_BUTTON_TEXT}]
    ],
}
VACANCY_EPILOGUE_KEYBOARD_MARKUP = {
    "keyboard": [
        [
            {"text": texts.CONTINUE_IN_BOT_KEYBOARD_TEXT},
            {"text": texts.MAIN_MENU_BUTTON_TEXT},
        ]
    ],
}
CHOOSE_VACANCY_KEYBOARD_MARKUP = {
    "keyboard": [
        *[
            [{"text": specialization} for specialization in specialization_row]
            for specialization_row in texts.SPECIALIZATION_ROWS
        ],
        [{"text": texts.BACK_BUTTON_TEXT}, {"text": texts.MAIN_MENU_BUTTON_TEXT}],
    ],
}
SENDING_TELEGRAM_KEYBOARD_MARKUP = {
    "keyboard": [
        [{"text": texts.LEAVE_CURRENT_ACCOUNT_BUTTON_TEXT}],
        [{"text": texts.BACK_BUTTON_TEXT}, {"text": texts.MAIN_MENU_BUTTON_TEXT}],
    ],
}
SENDING_INFO_KEYBOARD_MARKUP = {
    "keyboard": [
        [{"text": texts.SKIP_BUTTON_TEXT}],
        [{"text": texts.BACK_BUTTON_TEXT}, {"text": texts.MAIN_MENU_BUTTON_TEXT}],
    ],
}


@pytest.mark.anyio()
async def test_starting_vacancy_form(
    webhook_updater: WebhookUpdater,
    mocked_bot: MockedBot,
    bot_storage: BaseStorage,
    bot_storage_key: StorageKey,
    tg_chat_id: int,
    tg_user_id: int,
) -> None:
    webhook_updater(
        UpdateFactory.build(
            message=MessageFactory.build(
                text="/vacancy",
                chat=Chat(id=tg_chat_id, type="private"),
                from_user=UserFactory.build(id=tg_user_id),
            ),
        )
    )

    assert await bot_storage.get_state(bot_storage_key) == VacancyStates.starting_form

    mocked_bot.assert_next_api_call(
        SendMessage,
        {
            "chat_id": tg_chat_id,
            "text": texts.STARTING_VACANCY_FORM_MESSAGE,
            "reply_markup": VACANCY_EPILOGUE_KEYBOARD_MARKUP,
        },
    )
    mocked_bot.assert_no_more_api_calls()


@pytest.mark.anyio()
@pytest.mark.parametrize(
    "current_state",
    [
        pytest.param(
            VacancyStates.starting_form,
            id="starting_form",
        ),
        pytest.param(VacancyStates.sending_specialization, id="sending_specialization"),
        pytest.param(VacancyStates.sending_name, id="sending_name"),
        pytest.param(VacancyStates.sending_telegram, id="sending_telegram"),
        pytest.param(VacancyStates.sending_resume, id="sending_resume"),
        pytest.param(VacancyStates.sending_comment, id="sending_comment"),
    ],
)
async def test_exiting_vacancy_form(
    webhook_updater: WebhookUpdater,
    mocked_bot: MockedBot,
    bot_storage: BaseStorage,
    bot_storage_key: StorageKey,
    tg_chat_id: int,
    tg_user_id: int,
    current_state: State,
) -> None:
    await bot_storage.set_state(bot_storage_key, current_state)

    webhook_updater(
        UpdateFactory.build(
            message=MessageFactory.build(
                text=texts.MAIN_MENU_BUTTON_TEXT,
                chat=Chat(id=tg_chat_id, type="private"),
                from_user=UserFactory.build(id=tg_user_id),
            ),
        )
    )

    assert await bot_storage.get_state(bot_storage_key) is None
    mocked_bot.assert_next_api_call(
        SendMessage,
        {
            "chat_id": tg_chat_id,
            "text": texts.MAIN_MENU_MESSAGE,
            "reply_markup": EXPECTED_MAIN_MENU_KEYBOARD_MARKUP,
        },
    )
    mocked_bot.assert_no_more_api_calls()


@pytest.mark.anyio()
async def test_sending_continue_in_bot(
    webhook_updater: WebhookUpdater,
    mocked_bot: MockedBot,
    bot_storage: BaseStorage,
    bot_storage_key: StorageKey,
    tg_chat_id: int,
    tg_user_id: int,
) -> None:
    await bot_storage.set_state(bot_storage_key, VacancyStates.starting_form)

    webhook_updater(
        UpdateFactory.build(
            message=MessageFactory.build(
                text=texts.CONTINUE_IN_BOT_KEYBOARD_TEXT,
                chat=Chat(id=tg_chat_id, type="private"),
                from_user=UserFactory.build(id=tg_user_id),
            ),
        )
    )

    assert (
        await bot_storage.get_state(bot_storage_key)
        == VacancyStates.sending_specialization
    )

    mocked_bot.assert_next_api_call(
        SendMessage,
        {
            "chat_id": tg_chat_id,
            "text": texts.CHOOSE_VACANCY_MESSAGE,
            "reply_markup": CHOOSE_VACANCY_KEYBOARD_MARKUP,
        },
    )
    mocked_bot.assert_no_more_api_calls()


@pytest.mark.anyio()
async def test_sending_specialization(
    faker: Faker,
    webhook_updater: WebhookUpdater,
    mocked_bot: MockedBot,
    bot_storage: BaseStorage,
    bot_storage_key: StorageKey,
    tg_chat_id: int,
    tg_user_id: int,
) -> None:
    await bot_storage.set_state(bot_storage_key, VacancyStates.sending_specialization)
    position: str = faker.sentence(nb_words=2)

    webhook_updater(
        UpdateFactory.build(
            message=MessageFactory.build(
                text=position,
                chat=Chat(id=tg_chat_id, type="private"),
                from_user=UserFactory.build(id=tg_user_id),
            ),
        )
    )

    assert await bot_storage.get_state(bot_storage_key) == VacancyStates.sending_name
    assert await bot_storage.get_data(bot_storage_key) == {"position": position}
    mocked_bot.assert_next_api_call(
        SendMessage,
        {
            "chat_id": tg_chat_id,
            "text": texts.SEND_NAME_MESSAGE,
            "reply_markup": NAVIGATION_KEYBOARD_MARKUP,
        },
    )
    mocked_bot.assert_no_more_api_calls()


@pytest.mark.anyio()
async def test_sending_name(
    faker: Faker,
    webhook_updater: WebhookUpdater,
    mocked_bot: MockedBot,
    bot_storage: BaseStorage,
    bot_storage_key: StorageKey,
    tg_chat_id: int,
    tg_user_id: int,
) -> None:
    await bot_storage.set_state(bot_storage_key, VacancyStates.sending_name)
    name: str = faker.name()

    webhook_updater(
        UpdateFactory.build(
            message=MessageFactory.build(
                text=name,
                chat=Chat(id=tg_chat_id, type="private"),
                from_user=UserFactory.build(id=tg_user_id),
            ),
        )
    )

    assert (
        await bot_storage.get_state(bot_storage_key) == VacancyStates.sending_telegram
    )
    assert await bot_storage.get_data(bot_storage_key) == {"name": name}
    mocked_bot.assert_next_api_call(
        SendMessage,
        {
            "chat_id": tg_chat_id,
            "text": texts.SEND_TELEGRAM_MESSAGE,
            "reply_markup": SENDING_TELEGRAM_KEYBOARD_MARKUP,
        },
    )
    mocked_bot.assert_no_more_api_calls()


@pytest.mark.anyio()
@pytest.mark.parametrize(
    "is_account_provided",
    [
        pytest.param(
            False,
            id="current_account",
        ),
        pytest.param(True, id="provide_account"),
    ],
)
async def test_sending_telegram(
    faker: Faker,
    webhook_updater: WebhookUpdater,
    mocked_bot: MockedBot,
    bot_storage: BaseStorage,
    bot_storage_key: StorageKey,
    tg_chat_id: int,
    tg_user_id: int,
    is_account_provided: bool,
) -> None:
    username: str = faker.word()
    text: str = (
        faker.word() if is_account_provided else texts.LEAVE_CURRENT_ACCOUNT_BUTTON_TEXT
    )

    await bot_storage.set_state(bot_storage_key, VacancyStates.sending_telegram)

    webhook_updater(
        UpdateFactory.build(
            message=MessageFactory.build(
                text=text,
                chat=Chat(id=tg_chat_id, type="private"),
                from_user=UserFactory.build(id=tg_user_id, username=username),
            ),
        )
    )

    assert await bot_storage.get_state(bot_storage_key) == VacancyStates.sending_resume
    assert_contains(
        await bot_storage.get_data(bot_storage_key),
        {
            "telegram": (
                text if is_account_provided else f"{texts.TELEGRAM_BASE_URL}/{username}"
            )
        },
    )

    mocked_bot.assert_next_api_call(
        SendMessage,
        {
            "chat_id": tg_chat_id,
            "text": texts.SEND_RESUME_MESSAGE,
            "reply_markup": NAVIGATION_KEYBOARD_MARKUP,
        },
    )
    mocked_bot.assert_no_more_api_calls()


@pytest.mark.anyio()
async def test_sending_resume(
    faker: Faker,
    webhook_updater: WebhookUpdater,
    mocked_bot: MockedBot,
    bot_storage: BaseStorage,
    bot_storage_key: StorageKey,
    tg_chat_id: int,
    tg_user_id: int,
) -> None:
    await bot_storage.set_state(bot_storage_key, VacancyStates.sending_resume)
    resume: str = faker.url()

    webhook_updater(
        UpdateFactory.build(
            message=MessageFactory.build(
                text=resume,
                chat=Chat(id=tg_chat_id, type="private"),
                from_user=UserFactory.build(id=tg_user_id),
            ),
        )
    )

    assert await bot_storage.get_state(bot_storage_key) == VacancyStates.sending_comment
    assert await bot_storage.get_data(bot_storage_key) == {"link": resume}
    mocked_bot.assert_next_api_call(
        SendMessage,
        {
            "chat_id": tg_chat_id,
            "text": texts.SEND_INFO_MESSAGE,
            "reply_markup": SENDING_INFO_KEYBOARD_MARKUP,
        },
    )

    mocked_bot.assert_no_more_api_calls()


@pytest.mark.anyio()
@pytest.mark.parametrize(
    "is_comment_provided",
    [
        pytest.param(False, id="no_comment"),
        pytest.param(True, id="with_comment"),
    ],
)
async def test_sending_comment(
    faker: Faker,
    mock_stack: MockStack,
    webhook_updater: WebhookUpdater,
    mocked_bot: MockedBot,
    bot_storage: BaseStorage,
    bot_storage_key: StorageKey,
    tg_chat_id: int,
    tg_user_id: int,
    is_comment_provided: str,
) -> None:
    vacancy_endpoint_mock = mock_stack.enter_async_mock(
        "app.supbot.routers.vacancy_tgm.apply_for_vacancy"
    )
    data: dict[str, Any] = {
        "name": faker.name(),
        "position": faker.sentence(nb_words=2),
        "telegram": faker.url(),
        "link": faker.url(),
    }
    if is_comment_provided:
        data["message"] = faker.sentence(nb_words=5)
    await bot_storage.update_data(bot_storage_key, data)
    await bot_storage.set_state(bot_storage_key, VacancyStates.sending_comment)

    webhook_updater(
        UpdateFactory.build(
            message=MessageFactory.build(
                text=data["message"] if is_comment_provided else texts.SKIP_BUTTON_TEXT,
                chat=Chat(id=tg_chat_id, type="private"),
                from_user=UserFactory.build(id=tg_user_id),
            ),
        )
    )

    assert await bot_storage.get_state(bot_storage_key) is None
    assert await bot_storage.get_data(bot_storage_key) == {}
    mocked_bot.assert_next_api_call(
        SendMessage,
        {
            "chat_id": tg_chat_id,
            "text": texts.VACANCY_FORM_FINAL_MESSAGE,
            "reply_markup": EXPECTED_MAIN_MENU_KEYBOARD_MARKUP,
        },
    )
    mocked_bot.assert_no_more_api_calls()
    vacancy_endpoint_mock.assert_called_once_with(VacancyFormSchema(**data))


@pytest.mark.anyio()
@pytest.mark.parametrize(
    ("current_state", "expected_message", "expected_keyboard"),
    [
        pytest.param(
            VacancyStates.sending_specialization,
            texts.STARTING_VACANCY_FORM_MESSAGE,
            VACANCY_EPILOGUE_KEYBOARD_MARKUP,
            id="sending_specialization",
        ),
        pytest.param(
            VacancyStates.sending_name,
            texts.CHOOSE_VACANCY_MESSAGE,
            CHOOSE_VACANCY_KEYBOARD_MARKUP,
            id="sending_name",
        ),
        pytest.param(
            VacancyStates.sending_telegram,
            texts.SEND_NAME_MESSAGE,
            NAVIGATION_KEYBOARD_MARKUP,
            id="sending_telegram",
        ),
        pytest.param(
            VacancyStates.sending_resume,
            texts.SEND_TELEGRAM_MESSAGE,
            SENDING_TELEGRAM_KEYBOARD_MARKUP,
            id="sending_resume",
        ),
        pytest.param(
            VacancyStates.sending_comment,
            texts.SEND_RESUME_MESSAGE,
            NAVIGATION_KEYBOARD_MARKUP,
            id="sending_comment",
        ),
    ],
)
async def test_going_back(
    webhook_updater: WebhookUpdater,
    mocked_bot: MockedBot,
    bot_storage: BaseStorage,
    bot_storage_key: StorageKey,
    tg_chat_id: int,
    tg_user_id: int,
    current_state: State,
    expected_message: str,
    expected_keyboard: dict[str, Any],
) -> None:
    await bot_storage.set_state(bot_storage_key, current_state)

    webhook_updater(
        UpdateFactory.build(
            message=MessageFactory.build(
                text=texts.BACK_BUTTON_TEXT,
                chat=Chat(id=tg_chat_id, type="private"),
                from_user=UserFactory.build(id=tg_user_id),
            ),
        )
    )

    mocked_bot.assert_next_api_call(
        SendMessage,
        {
            "chat_id": tg_chat_id,
            "text": expected_message,
            "reply_markup": expected_keyboard,
        },
    )
    mocked_bot.assert_no_more_api_calls()


@pytest.mark.anyio()
@pytest.mark.parametrize(
    "current_state",
    [
        pytest.param(VacancyStates.starting_form, id="starting_form"),
        pytest.param(VacancyStates.sending_specialization, id="sending_specialization"),
        pytest.param(VacancyStates.sending_name, id="sending_name"),
        pytest.param(VacancyStates.sending_telegram, id="sending_telegram"),
        pytest.param(VacancyStates.sending_resume, id="sending_resume"),
        pytest.param(VacancyStates.sending_comment, id="sending_comment"),
    ],
)
@pytest.mark.parametrize(
    "input_media_cls",
    [
        pytest.param(InputMediaDocument, id="document"),
        pytest.param(InputMediaPhoto, id="photo"),
        pytest.param(InputMediaVideo, id="video"),
    ],
)
async def test_handling_unsupported_message(
    faker: Faker,
    webhook_updater: WebhookUpdater,
    mocked_bot: MockedBot,
    bot_storage: BaseStorage,
    bot_storage_key: StorageKey,
    tg_chat_id: int,
    tg_user_id: int,
    current_state: State,
    input_media_cls: type[InputMediaDocument | InputMediaPhoto | InputMediaVideo],
) -> None:
    await bot_storage.set_state(bot_storage_key, current_state)

    webhook_updater(
        UpdateFactory.build(
            message=MessageFactory.build(
                media=input_media_cls(media=faker.url()),
                chat=Chat(id=tg_chat_id, type="private"),
                from_user=UserFactory.build(id=tg_user_id),
            )
        )
    )

    assert await bot_storage.get_state(bot_storage_key) == current_state

    mocked_bot.assert_next_api_call(
        SendMessage,
        {"chat_id": tg_chat_id, "text": texts.VACANCY_INVALID_INPUT_TYPE_MESSAGE},
    )
    mocked_bot.assert_no_more_api_calls()
