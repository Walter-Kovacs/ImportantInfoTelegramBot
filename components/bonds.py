from datetime import datetime


def yield_to_maturity(
        face_value: float,
        coupon_rate: float,
        maturity_year: int,
        maturity_month: int,
        maturity_day: int,
        price: float
) -> float:

    today = datetime.today()
    maturity_date = datetime(maturity_year, maturity_month, maturity_day)

    maturity = (maturity_date - today).days / 365.25
    profit = maturity * face_value * coupon_rate / 100 + (face_value - price)

    return round(profit / maturity * 100 / price, 2)
