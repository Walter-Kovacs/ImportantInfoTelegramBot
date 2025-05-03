import asyncio
from attrs import define
from typing import List
from components.notification_gateway.objects import NotificationSource, NotificationSubscriber

from telegram import Bot

@define
class TGSender:
    bot: Bot 

    async def send_to_telegram(
            self, source: NotificationSource, notification: str, 
            receivers: List[NotificationSubscriber],
    ):
        async with asyncio.TaskGroup() as tg:
            for receiver in receivers:
                msg_text = f"Sender: {source}\n\n" + notification 
                tg.create_task(
                    self.bot.send_message(receiver.tg_id, msg_text)
                )
