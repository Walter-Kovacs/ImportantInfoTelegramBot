def echo(msg: str) -> str:
    return msg


def decline_game_request(msg: str) -> str:
    msg_lower = msg.lower()
    if msg_lower.find("цивилизацию") != -1 or msg_lower.find("циву") != -1:
        return "Цивилизация - это не модно. Вот Don't Starve - другое дело!"
    else:
        return "Похоже, что сейчас никто не готов играть :("
