from attrs import define

@define
class NotificationSource:
    _secret: str
    name: str

    def authenficate(self, secret: str) -> bool:
        if secret == self._secret:
            return True
        return False

    def __str__(self) -> str:
        return f"Notification Source [{self.name}]"

@define 
class NotificationSubscriber:
    tg_id: int
