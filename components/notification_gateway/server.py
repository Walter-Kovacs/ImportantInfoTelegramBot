import logging
import traceback
from aiohttp import web
from components.notification_gateway.services.telegram_sender import TGSender
from components.notification_gateway.objects import NotificationSource, NotificationSubscriber
from telegram import Bot

logger = logging.getLogger(__name__)

PORT = 5054

async def test_handler(request):
    logger.info('I catch POST request')
    data = await request.json()
    try:
        NGServer.telegram_sender.send_to_telegram(
            NotificationSource(name="hardcode any source", secret=""),
            f'I catched your message {data}'.encode(),
            [NotificationSubscriber(tg_id=354628382)],
        )
        return web.Response(text="Message has been delivered")
    except Exception:
        logging.error(
            "failed to send notification from source", 
            traceback.format_exc(),
        )
        return web.Response(status=400, text="Message has not been delivered")

class NGServer:
    telegram_sender: TGSender

    def start(self, telegram_bot: Bot):
        self.telegram_sender = TGSender(bot=telegram_bot)

        http_server_app = web.Application()
        http_server_app.add_routes([web.post('/', test_handler)])

        logging.info('Starting server in standalone thread')
        web.run_app(http_server_app, port=PORT)
