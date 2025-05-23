import asyncio

from dependency_injector.containers import WiringConfiguration

from src.container import Container
from src.endpoint import start_endpoint_manager
from src.presentation.bot import start_telegram_bot


async def main(container):
    await start_endpoint_manager()
    await start_telegram_bot()
    await container.api_repository.close()


if __name__ == "__main__":
    container = Container()
    container.wiring_config = WiringConfiguration(packages=["src", ])
    container.wire()

    asyncio.run(main(container))