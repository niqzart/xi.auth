from aiogram import Bot, Dispatcher, Router


class TelegramApp:
    def __init__(self) -> None:
        self.routers: list[Router] = []
        self._bot: Bot | None = None
        self._dispatcher: Dispatcher | None = None
        self._initialized: bool = False

    def include_router(self, router: Router) -> None:
        self.routers.append(router)

    def initialize(self, bot: Bot, dispatcher: Dispatcher) -> None:
        if self._initialized:
            return
        self._bot = bot
        self._dispatcher = dispatcher
        for router in self.routers:
            self._dispatcher.include_router(router)
        self._initialized = True

    @property
    def is_initialized(self) -> bool:
        return self._initialized

    @property
    def bot(self) -> Bot:
        if self._bot is None:
            raise EnvironmentError("Bot is not initialized")
        return self._bot

    @property
    def dispatcher(self) -> Dispatcher:
        if self._dispatcher is None:
            raise EnvironmentError("Dispatcher is not initialized")
        return self._dispatcher
