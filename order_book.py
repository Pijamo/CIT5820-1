
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from models import Base, Order

engine = create_engine('sqlite:///orders.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

def match(order, existing_order):
    if not existing_order.filled:
        if existing_order.sell_currency == order.buy_currency:
            if order.sell_currency == existing_order.buy_currency:
                if order.buy_amount / order.sell_amount <= existing_order.sell_amount / existing_order.buy_amount:
                    return True
    return False


def process_order(order_dict):
    buy_currency = order_dict['buy_currency']
    sell_currency = order_dict['sell_currency']
    buy_amount = order_dict['buy_amount']
    sell_amount = order_dict['sell_amount']
    sender_pk = order_dict['sender_pk']
    receiver_pk = order_dict['receiver_pk']

    if order_dict.get('creator_id', None):
        creator_id = order_dict.get('creator_id')
        order = Order(

            buy_currency=buy_currency,
            sell_currency=sell_currency,
            buy_amount=buy_amount,
            sell_amount=sell_amount,
            sender_pk=sender_pk,
            receiver_pk=receiver_pk,
            creator_id=creator_id
        )
    else:
        order = Order(

            buy_currency=buy_currency,
            sell_currency=sell_currency,
            buy_amount=buy_amount,
            sell_amount=sell_amount,
            sender_pk=sender_pk,
            receiver_pk=receiver_pk
        )

    session.add(order)
    session.commit()
    orders = session.query(Order).filter(Order.filled == None).all()

    for existing_order in orders:
        if match(order, existing_order):
            order.filled = datetime.now()
            existing_order.filled = datetime.now()
            order.counterparty_id = existing_order.id
            existing_order.counterparty_id = order.id
            session.commit()
            if order.buy_amount > existing_order.sell_amount:
                child = {}

                child['buy_currency'] = order.buy_currency
                child['sell_currency'] = order.sell_currency
                new_buy_amount = order.buy_amount - existing_order.sell_amount
                child['buy_amount'] = new_buy_amount
                child['sell_amount'] = 1.1 * (new_buy_amount * order.sell_amount / order.buy_amount)
                child['sender_pk'] = order.sender_pk
                child['receiver_pk'] = order.receiver_pk
                child['creator_id'] = order.id
                process_order(child)

            if existing_order.sell_amount > order.buy_amount:
                child = {}

                child['buy_currency'] = existing_order.buy_currency
                child['sell_currency'] = existing_order.sell_currency
                new_sell_amount = existing_order.sell_amount - order.buy_amount
                child['sell_amount'] = new_sell_amount
                child['buy_amount'] = 0.9 * (new_sell_amount * existing_order.buy_amount / existing_order.sell_amount)
                child['creator_id'] = existing_order.id
                child['sender_pk'] = existing_order.sender_pk
                child['receiver_pk'] = existing_order.receiver_pk
                process_order(child)



def match(order, existing_order):
    if order.filled == None and order.sell_currency == existing_order.buy_currency and order.buy_currency == existing_order.sell_currency and existing_order.sell_amount / existing_order.buy_amount >= order.buy_amount / order.sell_amount:
        return True
    return False
