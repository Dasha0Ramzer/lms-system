import stripe
from requests import session

from config.settings import STRIPE_API_KEY

stripe.api_key = STRIPE_API_KEY

LESSON_PRICE = 100000
COURSE_PRICE = 500000


def create_stripe_product(name):
    """Создает продукт в страйпе."""

    return stripe.Product.create(name=name)


def create_stripe_price(product):
    """Создает цену в страйпе."""

    return stripe.Price.create(
        currency="rub", unit_amount=product.get("amount"), product=product.get("id")
    )


def create_stripe_sessions(price):
    """Создает сессию в страйпе."""

    session = stripe.checkout.Session.create(
        success_url="https://127.0.0.1:8000/",
        line_items=[{"price": price.id, "quantity": 1}],
        mode="payment",
    )
    return session.id, session.url
