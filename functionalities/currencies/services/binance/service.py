from binance.spot import Spot

client = Spot()


class ServiceError(Exception):
    pass
