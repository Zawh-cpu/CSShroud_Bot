from aiohttp import web, web_request
from src.core import Mail
from src.presentation.plugin import send_mail

async def mail_notify(request: web_request.Request):
    mails = await request.json()
    if type(mails) is not list:
        return web.Response(status=400)


    for mail in map(lambda x: Mail(x), mails):
        print(mail)
        await send_mail(mail)

    return web.Response(text="OK")

class EndPointManager:
    def __init__(self, host="127.0.0.1", port=63268, allowed_host=tuple()):
        self.host = host
        self.port = port
        self.allowed_host = allowed_host

        print(host, port, allowed_host)

        self.app = web.Application(middlewares=[self.host_check_middleware])
        self.runner = None
        self.site = None

        self._setup_routes()

    def _setup_routes(self):
        if not self.app:
            return

        self.app.router.add_post("/api/v1/hook/mail", mail_notify)

    @web.middleware
    async def host_check_middleware(self, request, handler):
        peername = request.transport.get_extra_info("peername")
        if peername is None:
            return web.Response(status=403, text="Forbidden: cannot determine client IP")

        client_ip = peername[0]

        if client_ip not in self.allowed_host:
            return web.Response(status=403, text=f"Forbidden")

        return await handler(request)

    async def run(self):
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        self.site = web.TCPSite(self.runner, self.host, self.port)
        await self.site.start()
