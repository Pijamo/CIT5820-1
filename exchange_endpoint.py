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
from web3 import Web3

# TODO: make sure you implement connect_to_algo, send_tokens_algo, and send_tokens_eth
from send_tokens import connect_to_algo, connect_to_eth, send_tokens_algo, send_tokens_eth

from models import Base, Order, TX

engine = create_engine('sqlite:///orders.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)

app = Flask(__name__)

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
    print(msg)
    # TODO: Add message to the Log table

    return


def get_algo_keys():
    # TODO: Generate or read (using the mnemonic secret)
    # the algorand public/private keys
    algo_sk, algo_pk = algosdk.account.generate_account()
    return algo_sk, algo_pk


def get_eth_keys(filename="eth_mnemonic.txt"):
    w3 = Web3()
    # TODO: Generate or read (using the mnemonic secret)
    # the ethereum public/private keys
    w3.eth.account.enable_unaudited_hdwallet_features()
    acct, mnemonic_secret = w3.eth.account.create_with_mnemonic()

    eth_pk = acct.address
    eth_sk = acct.key

    return eth_sk, eth_pk


def fill_order(order, txes=[]):
    # TODO:
    # Match orders (same as Exchange Server II)
    # Validate the order has a payment to back it (make sure the counterparty also made a payment)
    # Make sure that you end up executing all resulting transactions!

    # If your fill_order function is recursive, and you want to have fill_order return a list of transactions to be filled,
    # Then you can use the "txes" argument to pass the current list of txes down the recursion
    # Note: your fill_order function is *not* required to be recursive, and it is *not* required that it return a list of transactions,
    # but executing a group of transactions can be more efficient, and gets around the Ethereum nonce issue described in the instructions

    pass


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

    # TODO:
    #       1. Send tokens on the Algorand and eth testnets, appropriately
    #          We've provided the send_tokens_algo and send_tokens_eth skeleton methods in send_tokens.py
    #       2. Add all transactions to the TX table

    pass


""" End of Helper methods"""


@app.route('/address', methods=['POST'])
def address():
    if request.method == "POST":
        content = request.get_json(silent=True)
        print(content)
        if 'platform' not in content.keys():
            print(f"Error: no platform provided")
            return jsonify("Error: no platform provided")
        if not content['platform'] in ["Ethereum", "Algorand"]:
            print(f"Error: {content['platform']} is an invalid platform")
            return jsonify(f"Error: invalid platform provided: {content['platform']}")

        if content['platform'] == "Ethereum":
            # Your code here
            eth_sk, eth_pk = get_eth_keys()
            return jsonify(eth_pk)
        if content['platform'] == "Algorand":
            # Your code here
            algo_sk, algo_pk = get_algo_keys()
            return jsonify(algo_pk)


@app.route('/trade', methods=['POST'])
def trade():
    print("In trade", file=sys.stderr)
    connect_to_blockchains()
    # get_keys()
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
        return jsonify(False)

        # 1. Check the signature
        algo_sk, algo_pk = get_algo_keys()
        eth_sk, eth_pk = get_eth_keys()

        result = False

        if content['payload']['sell_currency'] == "Ethereum":
            payloadtxt = json.dumps(content['payload'])
            eth_encoded_msg = eth_account.messages.encode_defunct(text=payloadtxt)
            eth_sig_obj = content['payload']
            pk = eth_account.Account.recover_message(eth_encoded_msg, signature=content['sig'])

            if pk == content['payload']['sender_pk']:
                result = True
            else:
                result = False

        elif content['payload']['platform'] == "Algorand":
            payloadtxt = json.dumps(content['payload'])
            algo_sig_str = algosdk.util.sign_bytes(payloadtxt.encode('utf-8'), algo_sk)

            if algosdk.util.verify_bytes(payloadtxt.encode('utf-8'), content['sig'], content['payload']['sender_pk']):
                result = True
            else:
                result = False

        if result == False:
            print(json.dumps(content))
            return jsonify(False)

        # 2. Add the order to the table
        orderFields = ['sender_pk', 'receiver_pk', 'buy_currency', 'sell_currency', 'buy_amount', 'sell_amount',
                       'tx_id']
        newOrder = {}
        newOrder['sender_pk'] = content["payload"]["sender_pk"]
        newOrder['receiver_pk'] = content["payload"]["receiver_pk"]
        newOrder['buy_currency'] = content["payload"]["buy_currency"]
        newOrder['sell_currency'] = content["payload"]["sell_currency"]
        newOrder['buy_amount'] = content["payload"]["buy_amount"]
        newOrder['sell_amount'] = content["payload"]["sell_amount"]
        newOrder['tx_id'] = content["payload"]["tx_id"]
        order_obj = Order(**{f: newOrder[f] for f in orderFields})
        g.session.add(order_obj)
        g.session.commit

        # 3a. Check if the order is backed by a transaction equal to the sell_amount (this is new)
        if content['payload']['platform'] == "Ethereum":
            tx = g.w3.eth.get_transaction(content['payload']['tx_id'])
            if tx == []:
                return jsonify(False)
        # elif content['payload']['platform'] == "Algorand":
        #    client = connect_to_algo(connection_type = "indexer")
        #    tx = client.search_transactions(txid=content['payload']['tx_id'])
        #    if tx == []:
        #        return jsonify(False)

        # 3b. Fill the order (as in Exchange Server II) if the order is valid
        for orderToMatch in g.session.query(Order).filter(Order.filled == None):
            possibleOrder = g.session.query(Order).filter(Order.filled == None,
                                                          Order.buy_currency == orderToMatch.sell_currency,
                                                          Order.sell_currency == orderToMatch.buy_currency, \
                                                          (Order.sell_amount / Order.buy_amount) >= (
                                                                      orderToMatch.buy_amount / orderToMatch.sell_amount)).first()

        if possibleOrder != None and orderToMatch.filled == None:
            orderToMatch.filled = datetime.now()
            orderToMatch.counterparty_id = possibleOrder.id
            g.session.commit()
            # execute_txes(orderToMatch, orderToMatch.sell_currency)

            possibleOrder.filled = datetime.now()
            possibleOrder.counterparty_id = orderToMatch.id
            g.session.commit()
            # execute_txes(orderToMatch, orderToMatch.sell_currency)

            if orderToMatch.buy_amount > possibleOrder.sell_amount or orderToMatch.sell_amount > possibleOrder.buy_amount:
                newOrder = {}
                newOrder['sender_pk'] = orderToMatch.sender_pk
                newOrder['receiver_pk'] = orderToMatch.receiver_pk
                newOrder['buy_currency'] = orderToMatch.buy_currency
                newOrder['sell_currency'] = orderToMatch.sell_currency
                if orderToMatch.buy_amount > possibleOrder.sell_amount:
                    newOrder['buy_amount'] = orderToMatch.buy_amount - possibleOrder.sell_amount
                    newOrder['sell_amount'] = orderToMatch.sell_amount / orderToMatch.buy_amount * newOrder[
                        'buy_amount']
                elif orderToMatch.sell_amount > possibleOrder.buy_amount:
                    newOrder['sell_amount'] = orderToMatch.sell_amount - possibleOrder.buy_amount
                    newOrder['buy_amount'] = orderToMatch.buy_amount / orderToMatch.sell_amount * newOrder[
                        'sell_amount']
                newOrder['creator_id'] = orderToMatch.id

                orderFields = ['sender_pk', 'receiver_pk', 'buy_currency', 'sell_currency', 'buy_amount', 'sell_amount',
                               'creator_id']
                order_obj = Order(**{f: newOrder[f] for f in orderFields})
                g.session.add(order_obj)
                g.session.commit()

            if orderToMatch.buy_amount < possibleOrder.sell_amount or orderToMatch.sell_amount < possibleOrder.buy_amount:
                newOrder = {}
                newOrder['sender_pk'] = possibleOrder.sender_pk
                newOrder['receiver_pk'] = possibleOrder.receiver_pk
                newOrder['buy_currency'] = possibleOrder.buy_currency
                newOrder['sell_currency'] = possibleOrder.sell_currency
                if possibleOrder.sell_amount > orderToMatch.buy_amount:
                    newOrder['sell_amount'] = possibleOrder.sell_amount - possibleOrder.buy_amount
                    newOrder['buy_amount'] = possibleOrder.buy_amount / possibleOrder.sell_amount * newOrder[
                        'sell_amount']
                elif possibleOrder.buy_amount > orderToMatch.sell_amount:
                    newOrder['buy_amount'] = possibleOrder.buy_amount - possibleOrder.sell_amount
                    newOrder['sell_amount'] = possibleOrder.sell_amount / possibleOrder.buy_amount * newOrder[
                        'buy_amount']
                newOrder['creator_id'] = possibleOrder.id

                orderFields = ['sender_pk', 'receiver_pk', 'buy_currency', 'sell_currency', 'buy_amount', 'sell_amount',
                               'creator_id']
                order_obj = Order(**{f: newOrder[f] for f in orderFields})
                g.session.add(order_obj)
                g.session.commit()

        # 4. Execute the transactions

        # If all goes well, return jsonify(True). else return jsonify(False)
        return jsonify(True)


@app.route('/order_book')
def order_book():
    # Same as before
    data = g.session.query(Order)
    result = []
    for d in data:
        dic = {}
        dic['sender_pk'] = d.sender_pk
        dic['receiver_pk'] = d.receiver_pk
        dic['buy_currency'] = d.buy_currency
        dic['sell_currency'] = d.sell_currency
        dic['buy_amount'] = d.buy_amount
        dic['sell_amount'] = d.sell_amount
        dic['tx_id'] = d.tx_id
        result.append(dic)
    resultDict = {'data': result}
    return jsonify(result)


if __name__ == '__main__':
    app.run(port='5002')