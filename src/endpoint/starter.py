from dependency_injector.wiring import inject, Provide
from src.infrastructure.config import Config
from src.container import Container

from .endpoint_manager import EndPointManager

@inject
async def start_endpoint_manager(config: Config = Provide[Container.config]):
    print("EP-MANAGER >> STARTED")
    service_manager = EndPointManager(host=config.ENDPOINT.HOST, port=config.ENDPOINT.PORT, allowed_host=config.ENDPOINT.ALLOWED_HOST)

    await service_manager.run()
