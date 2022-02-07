from attrs import define


@define
class User:
    tg_id: int
    is_admin: bool
