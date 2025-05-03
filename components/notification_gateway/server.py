import logging
import traceback
import queue
import threading
from aiohttp import web
from attrs import define
from components.notification_gateway.services.telegram_sender import TGSender
from components.notification_gateway.objects import NotificationSource, NotificationSubscriber
from telegram import Bot

logger = logging.getLogger(__name__)

web_app_key_queue_to_send = web.AppKey("telegram_sender", queue.Queue)

@define
class QueueMessage:
    source: NotificationSource
    message: str 

async def test_handler(request: web.Request):
    logger.info('I catch POST request')
    data = await request.json()
    try:
        q: queue.Queue = request.app[web_app_key_queue_to_send]
        q.put(QueueMessage(
            source=NotificationSource(name="hardcode any source", secret=""),
            message=f'I catched your message {data}',
        ))
        return web.Response(text="Message has been delivered")
    except Exception:
        logging.error(
            "failed to send notification from source", 
            traceback.format_exc(),
        )
        return web.Response(status=400, text="Message has not been delivered")

class NGServer:
    telegram_sender: TGSender
    messages_from_server_queue: queue.Queue
    PORT: int = 5054

    async def _queue_handler(self) -> None:
        msg: QueueMessage = self.messages_from_server_queue.get()
        await self.telegram_sender.send_to_telegram(
            msg.source, msg.message, [NotificationSubscriber(tg_id=354628382)],
        )


    def set_telegram_bot(self, telegram_bot: Bot):
        self.telegram_sender = TGSender(bot=telegram_bot)

    def _start_web_server(self, queue_to_send: queue.Queue):
        http_server_app = web.Application()
        http_server_app[web_app_key_queue_to_send] = queue_to_send 
        http_server_app.add_routes([web.post('/', test_handler)])

        logging.info('Starting server in standalone thread')
        web.run_app(http_server_app, port=self.PORT)


    def start(self, port=None) -> None:
        messages_from_server_queue: queue.Queue = queue.Queue()
        if port is not None:
            self.PORT = port
        threading.Thread(target=lambda: self._start_web_server(messages_from_server_queue)).start()

