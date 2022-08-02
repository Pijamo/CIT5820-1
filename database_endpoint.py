from flask import Flask, request, g
from flask_restful import Resource, Api
from sqlalchemy import create_engine, select, MetaData, Table
from flask import jsonify
import json
import eth_account
import algosdk
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import load_only

from models import Base, Order, Log

engine = create_engine('sqlite:///orders.db')
DBSession = sessionmaker(bind=engine)

app = Flask(__name__)


# These decorators allow you to use g.session to access the database inside the request code
@app.before_request
def create_session():
    g.session = scoped_session(
        DBSession)  # g is an "application global" https://flask.palletsprojects.com/en/1.1.x/api/#application-globals


@app.teardown_appcontext
def shutdown_session(response_or_exc):
    g.session.commit()
    g.session.remove()


"""
-------- Helper methods (feel free to add your own!) -------
"""


def order_obj_to_dict(order_obj):
    d = {}
    d['sender_pk'] = order_obj.sender_pk
    d['receiver_pk'] = order_obj.receiver_pk
    d['buy_currency'] = order_obj.buy_currency
    d['sell_currency'] = order_obj.sell_currency
    d['buy_amount'] = order_obj.buy_amount
    d['sell_amount'] = order_obj.sell_amount
    d['signature'] = order_obj.signature
    return d


def log_message(d):
    # Takes input dictionary d and writes it to the Log table
    new_log = Log(message=json.dumps(d))
    g.session.add(new_log)
    g.session.commit()


"""
---------------- Endpoints ----------------
"""


@app.route('/trade', methods=['POST'])
def trade():
    if request.method == "POST":
        content = request.get_json(silent=True)
        print(f"content = {json.dumps(content)}")
        columns = [
            "sender_pk",
            "receiver_pk",
            "buy_currency",
            "sell_currency",
            "buy_amount",
            "sell_amount",
            "platform"
        ]
        fields = ["sig", "payload"]
        error = False
        for field in fields:
            if not field in content.keys():
                print(f"{field} not received by Trade")
                log_message(content)
                return jsonify(False)

        error = False
        for column in columns:
            if not column in content['payload'].keys():
                print(f"{column} not received by Trade")
                error = True
        if error:
            print(json.dumps(content))
            log_message(content)
            return jsonify(False)

        # Your code here
        # Note that you can access the database session using g.session
        sig = content['sig']
        payload = content['payload']
        receiver_pk = payload['receiver_pk']
        sender_pk = payload['sender_pk']
        buy_currency = payload['buy_currency']
        sell_currency = payload['sell_currency']
        buy_amount = payload['buy_amount']
        sell_amount = payload['sell_amount']
        platform = payload['platform']

        if platform == 'Ethereum':
            encoded_msg = eth_account.messages.encode_defunct(text=json.dumps(payload))
            response = eth_account.Account.recover_message(encoded_msg, signature=sig) == sender_pk
        else:
            response = algosdk.util.verify_bytes(json.dumps(payload).encode('utf-8'), sig, sender_pk)

        if response:  # verified
            new_order = Order(
                receiver_pk=receiver_pk,
                sender_pk=sender_pk,
                buy_currency=buy_currency,
                sell_currency=sell_currency,
                buy_amount=buy_amount,
                sell_amount=sell_amount,
                signature=sig,
            )
            g.session.add(new_order)
            g.session.commit()
            return jsonify(True)
        else:  # fail to verify
            log_message(payload)
            return jsonify(False)
    else:
        return jsonify(True)


@app.route('/order_book')
def order_book():
    # Your code here
    # Note that you can access the database session using g.session
    order_dict = {'data': []}
    orders = g.session.query(Order)
    for order in orders:
        order_dict['data'].append(order_obj_to_dict(order))
    return json.dumps(order_dict)


if __name__ == '__main__':
    app.run(port='5002')