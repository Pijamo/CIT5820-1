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
import sys

from models import Base, Order, Log
engine = create_engine('sqlite:///orders.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)

app = Flask(__name__)

@app.before_request
def create_session():
    g.session = scoped_session(DBSession)

@app.teardown_appcontext
def shutdown_session(response_or_exc):
    sys.stdout.flush()
    g.session.commit()
    g.session.remove()

""" Suggested helper methods """

def check_sig(payload,sig):
    pk = payload.get('pk')
    if payload.get('platform') == 'Ethereum':
        encoded_msg = eth_account.messages.encode_defunct(text=json.dumps(payload))
        return eth_account.Account.recover_message(encoded_msg, signature=sig) == pk
    else:
        return algosdk.util.verify_bytes(json.dumps(payload).encode('utf-8'), sig, pk)

def fill_order(order,txes):
    for existing_order in txes:
      if not existing_order.filled:
        if existing_order.sell_currency == order.buy_currency:
            if order.sell_currency == existing_order.buy_currency:
                if order.buy_amount / order.sell_amount <= existing_order.sell_amount / existing_order.buy_amount:
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
                    g.session.add(child)
                    g.session.commit()
                    fill_order(child,txes)
                    return True
                  else:
                    child = {}
                    child['buy_currency'] = existing_order.buy_currency
                    child['sell_currency'] = existing_order.sell_currency
                    new_sell_amount = existing_order.sell_amount - order.buy_amount
                    child['sell_amount'] = new_sell_amount
                    child['buy_amount'] = 0.9 * (new_sell_amount * existing_order.buy_amount / existing_order.sell_amount)
                    child['creator_id'] = existing_order.id
                    child['sender_pk'] = existing_order.sender_pk
                    child['receiver_pk'] = existing_order.
                    g.session.add(child)
                    g.session.commit()
                    fill_order(child,txes)
                    return True
    return False
  
def log_message(msg):
    # Takes input dictionary d and writes it to the Log table
    # Hint: use json.dumps or str() to get it in a nice string form
    msg = json.dumps(message_dict)

    # TODO: Add message to the Log table
    log = Log(message=msg)
    g.session.add(log)
    g.session.commit()
    return

""" End of helper methods """



@app.route('/trade', methods=['POST'])
def trade():
    print("In trade endpoint")
    if request.method == "POST":
        content = request.get_json(silent=True)
        print( f"content = {json.dumps(content)}" )
        columns = [ "sender_pk", "receiver_pk", "buy_currency", "sell_currency", "buy_amount", "sell_amount", "platform" ]
        fields = [ "sig", "payload" ]

        for field in fields:
            if not field in content.keys():
                print( f"{field} not received by Trade" )
                print( json.dumps(content) )
                log_message(content)
                return jsonify( False )
        
        for column in columns:
            if not column in content['payload'].keys():
                print( f"{column} not received by Trade" )
                print( json.dumps(content) )
                log_message(content)
                return jsonify( False )
            
        #Your code here
        #Note that you can access the database session using g.session

        # TODO: Check the signature
        sig = content.get('sig')
        payload = content.get('payload')

        if check_sig(payload, sig):
          
          # TODO: Add the order to the database
          payload = content['payload']
          buy_currency = payload['buy_currency']
          sell_currency = payload['sell_currency']
          sig = content['sig']
          payload = content['payload']
          receiver_pk = payload['receiver_pk']
          sender_pk = payload['sender_pk']
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
        
        # TODO: Fill the order
        orders = session.query(Order).filter(Order.filled == None).all()
        if fill_order(new_order, orders):
          return jsonify(True)
        else:
          return jsonify(False)



        
        # TODO: Be sure to return jsonify(True) or jsonify(False) depending on if the method was successful
        

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