from flask import Flask, request, g
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from flask import jsonify
import json
import eth_account
import algosdk
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import load_only
from datetime import datetime
import math
import sys
import traceback
import send_tokens
from algosdk import mnemonic
from algosdk import account
from web3 import Web3

# TODO: make sure you implement connect_to_algo, send_tokens_algo, and send_tokens_eth
from send_tokens import connect_to_algo, connect_to_eth, send_tokens_algo, send_tokens_eth

from models import Base, Order, TX, Log

engine = create_engine('sqlite:///orders.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)

app = Flask(__name__)

eth_sk, eth_pk = 0, 0
algo_sk, algo_pk = 0, 0

""" Pre-defined methods (do not need to change) """


@app.before_request
def create_session():
    g.session = scoped_session(DBSession)


@app.teardown_appcontext
def shutdown_session(response_or_exc):
    sys.stdout.flush()
    g.session.commit()
    g.session.remove()


def connect_to_blockchains():
    try:
        # If g.acl has not been defined yet, then trying to query it fails
        acl_flag = False
        g.acl
    except AttributeError as ae:
        acl_flag = True

    try:
        if acl_flag or not g.acl.status():
            # Define Algorand client for the application
            g.acl = connect_to_algo()
    except Exception as e:
        print("Trying to connect to algorand client again")
        print(traceback.format_exc())
        g.acl = connect_to_algo()

    try:
        icl_flag = False
        g.icl
    except AttributeError as ae:
        icl_flag = True

    try:
        if icl_flag or not g.icl.health():
            # Define the index client
            g.icl = connect_to_algo(connection_type='indexer')
    except Exception as e:
        print("Trying to connect to algorand indexer client again")
        print(traceback.format_exc())
        g.icl = connect_to_algo(connection_type='indexer')

    try:
        w3_flag = False
        g.w3
    except AttributeError as ae:
        w3_flag = True

    try:
        if w3_flag or not g.w3.isConnected():
            g.w3 = connect_to_eth()
    except Exception as e:
        print("Trying to connect to web3 again")
        print(traceback.format_exc())
        g.w3 = connect_to_eth()


""" End of pre-defined methods """

""" Helper Methods (skeleton code for you to implement) """


def log_message(message_dict):
    msg = json.dumps(message_dict)

    # TODO: Add message to the Log table
    log_obj = Log(logtime=datetime.now(), message=msg)
    g.session.add(log_obj)
    g.session.commit()
    return


def get_algo_keys():
    # TODO: Generate or read (using the mnemonic secret)
    # the algorand public/private keys
    mnemonic_secret = "This is for CIT five eighty two"
    algo_sk = mnemonic.to_private_key(mnemonic_secret)
    algo_pk = mnemonic.to_public_key(mnemonic_secret)
    return algo_sk, algo_pk


def get_eth_keys(filename="eth_mnemonic.txt"):
    w3 = Web3()

    # TODO: Generate or read (using the mnemonic secret)
    # the ethereum public/private keys
    w3.eth.account.enable_unaudited_hdwallet_features()
    acct, mnemonic_secret = w3.eth.account.create_with_mnemonic()
    acct = w3.eth.account.from_mnemonic(mnemonic_secret)
    eth_pk = acct._address
    eth_sk = acct._private_key
    return eth_sk, eth_pk


def fill_order(order, txes):
    for existing_order in txes:
        if not existing_order.filled:
            if existing_order.sell_currency == order.buy_currency:
                if order.sell_currency == existing_order.buy_currency:
                    if order.buy_amount / order.sell_amount <= existing_order.sell_amount / existing_order.buy_amount:
                        order.filled = datetime.now()
                        existing_order.filled = datetime.now()
                        order.counterparty_id = existing_order.id
                        existing_order.counterparty_id = order.id
                        g.session.commit()
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

                            child_order = Order(
                                buy_currency=order.buy_currency,
                                sell_currency=order.sell_currency,
                                buy_amount=new_buy_amount,
                                sell_amount=1.1 * (new_buy_amount * order.sell_amount / order.buy_amount),
                                sender_pk=order.sender_pk,
                                receiver_pk=order.receiver_pk,
                                creator_id=order.id
                            )

                            g.session.add(child_order)

                            g.session.commit()
                            txes = g.session.query(Order).filter(Order.filled == None).all()
                            fill_order(child_order, txes)
                            return True
                        else:
                            child = {}
                            child['buy_currency'] = existing_order.buy_currency
                            child['sell_currency'] = existing_order.sell_currency
                            new_sell_amount = existing_order.sell_amount - order.buy_amount
                            child['sell_amount'] = new_sell_amount
                            child['buy_amount'] = 0.9 * (
                                        new_sell_amount * existing_order.buy_amount / existing_order.sell_amount)
                            child['creator_id'] = existing_order.id
                            child['sender_pk'] = existing_order.sender_pk
                            child['receiver_pk'] = existing_order.receiver_pk

                            child_order = Order(
                                buy_currency=existing_order.buy_currency,
                                sell_currency=existing_order.sell_currency,
                                buy_amount=0.9 * (
                                            new_sell_amount * existing_order.buy_amount / existing_order.sell_amount),
                                sell_amount=existing_order.sell_amount - order.buy_amount,
                                sender_pk=existing_order.sender_pk,
                                receiver_pk=existing_order.receiver_pk,
                                creator_id=existing_order.id
                            )

                            g.session.add(child_order)
                            g.session.commit()
                            txes = g.session.query(Order).filter(Order.filled == None).all()
                            fill_order(child_order, txes)
                            return True
    return False


def execute_txes(txes):
    if txes is None:
        return True
    if len(txes) == 0:
        return True
    print(f"Trying to execute {len(txes)} transactions")
    print(f"IDs = {[tx['order_id'] for tx in txes]}")
    eth_sk, eth_pk = get_eth_keys()
    algo_sk, algo_pk = get_algo_keys()

    if not all(tx['platform'] in ["Algorand", "Ethereum"] for tx in txes):
        print("Error: execute_txes got an invalid platform!")
        print(tx['platform'] for tx in txes)

    algo_txes = [tx for tx in txes if tx['platform'] == "Algorand"]
    eth_txes = [tx for tx in txes if tx['platform'] == "Ethereum"]

    w3 = Web3()

    # TODO:
    #       1. Send tokens on the Algorand and eth testnets, appropriately
    #          We've provided the send_tokens_algo and send_tokens_eth skeleton methods in send_tokens.py
    #       2. Add all transactions to the TX table
    send_tokens_algo(g.acl, algo_sk, algo_txes)
    send_tokens_eth(g.w3, eth_sk, eth_txes)

    g.session.add_all(algo_txes)
    g.session.add_all(eth_txes)
    g.session.commit()


""" End of Helper methods"""


@app.route('/address', methods=['POST'])
def address():
    if request.method == "POST":
        content = request.get_json(silent=True)
        payload = content.get('payload')
        platform = content.get('platform')
        if platform == None:
            platform = payload.get('platform')

        if platform == "Ethereum":
            # Your code here
            eth_sk, eth_pk = get_eth_keys()
            # print(eth_pk, jsonify(eth_pk))
            return jsonify(eth_pk)
        if platform == "Algorand":
            # Your code here
            algo_sk, algo_pk = get_algo_keys()
            return jsonify(algo_pk)


@app.route('/trade', methods=['POST'])
def trade():
    print("In trade", file=sys.stderr)
    connect_to_blockchains()
    # get_keys()

    # get algo keys
    algo_sk, algo_pk = get_algo_keys()
    # get eth keys
    eth_sk, eth_pk = get_eth_keys()

    if request.method == "POST":
        content = request.get_json(silent=True)
        columns = ["buy_currency", "sell_currency", "buy_amount", "sell_amount", "platform", "tx_id", "receiver_pk"]
        fields = ["sig", "payload"]
        error = False
        for field in fields:
            if not field in content.keys():
                print(f"{field} not received by Trade")
                error = True
        if error:
            print(json.dumps(content))
            return jsonify(False)

        error = False
        for column in columns:
            if not column in content['payload'].keys():
                print(f"{column} not received by Trade")
                error = True
        if error:
            print(json.dumps(content))
            return jsonify(False)

        # Your code here

        # 1. Check the signature
        sig = content.get('sig')
        payload = content.get('payload')

        # 2. Add the order to the table
        if check_sig(payload, sig):
            print('signature matched')
            # TODO: Add the order to the database
            # order = Order(sender_pk = payload.get('sender_pk'),
            #             receiver_pk = payload.get('receiver_pk'),
            #             buy_currency = payload.get('buy_currency'),
            #             sell_currency = payload.get('sell_currency'),
            #             buy_amount = payload.get('buy_amount'),
            #             sell_amount = payload.get('sell_amount'),
            #             tx_id = payload.get('tx_id'),
            #             )
            # g.session.add(order)
            # g.session.commit()
            # TODO: Fill the order

            order_dict = {'sender_pk': payload.get('sender_pk'),
                          'receiver_pk': payload.get('receiver_pk'),
                          'buy_currency': payload.get('buy_currency'),
                          'sell_currency': payload.get('sell_currency'),
                          'buy_amount': payload.get('buy_amount'),
                          'sell_amount': payload.get('sell_amount'),
                          'tx_id': payload.get('tx_id')}
            # 3a. Check if the order is backed by a transaction equal to the sell_amount (this is new)
            print('transaction_id: ' + order_dict['tx_id'])
            if order_dict['sell_currency'] == 'Algorand':
                tx = g.icl.search_transactions(txid=order_dict['tx_id'])
                assert tx.amount == order_dict['sell_amount']
                tx_amount = tx.amount
                print('printing algorand tx')
                print(tx)
            elif order_dict['sell_currency'] == 'Ethereum':
                tx = g.w3.eth.get_transaction(order_dict['tx_id'])
                assert tx.value == order_dict['sell_amount']
                tx_amount = tx.value
                print('printing ethereum tx')
                print(tx)
            # if(order_dict['sell_amount'] == tx.order.sell_amount and order_dict['sender_pk'] == tx.order.sender_pk and tx.platform == tx.order.sell_currency ):
            if (tx_amount == order_dict['sell_amount']):
                print('trying to fill order')

                try:
                    fill_order(order_dict)
                    return jsonify(True)
                except Exception as e:
                    import traceback
                    print(traceback.format_exc())
                    print(e)

                    # print('trying to execute order now')
                #
                # try:
                #    execute_txes(tx)
                # except Exception as e:
                #  import traceback
                #  print(traceback.format_exc())
                #  print(e)

            else:
                return jsonify(False)

        # 3b. Fill the order (as in Exchange Server II) if the order is valid

        # 4. Execute the transactions

        # If all goes well, return jsonify(True). else return jsonify(False)
        else:
            log_message(payload)
            return jsonify(False)

@app.route('/order_book')
def order_book():
    #Your code here
    #Note that you can access the database session using g.session
    order_dict = {'data': []}
    orders = g.session.query(Order)
    for order in orders:
      dic = {}
      dic['buy_currency'] = order.buy_currency
      dic['sell_currency'] = order.sell_currency
      dic['buy_amount'] = order.buy_amount
      dic['sell_amount'] = order.sell_amount
      dic['sender_pk'] = order.sender_pk
      dic['receiver_pk'] = order.receiver_pk
      dic['signature'] = order.signature
      order_dict['data'].append(dic)
    return json.dumps(order_dict)


if __name__ == '__main__':
    app.run(port='5002')