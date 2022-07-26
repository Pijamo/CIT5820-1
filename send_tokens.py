#!/usr/bin/python3
import algosdk
from algosdk import account
from algosdk.v2client import algod
from algosdk.v2client import indexer
from algosdk import account, mnemonic
from algosdk.future import transaction

#Connect to Algorand node maintained by PureStake
algod_address = "https://testnet-algorand.api.purestake.io/ps2"
algod_token = "B3SU4KcVKi94Jap2VXkK83xx38bsv95K5UZm2lab"
#algod_token = 'IwMysN3FSZ8zGVaQnoUIJ9RXolbQ5nRY62JRqF2H'
headers = {
   "X-API-Key": algod_token,
}

acl = algod.AlgodClient(algod_token, algod_address, headers)
min_balance = 100000 #https://developer.algorand.org/docs/features/accounts/#minimum-balance
def send_tokens(receiver_pk, tx_amount):
    """"
    acl: algorand client
    sender_sk: private key of sender
    txes: list of transactions
    """

    # TODO: You might want to adjust the first/last valid rounds in the suggested_params
    #       See guide for details

    # TODO: For each transaction, do the following:
    #       - Create the Payment transaction
    #       - Sign the transaction

    # TODO: Return a list of transaction id's
    params = acl.suggested_params()

    gen = params.gen
    gh = params.gh
    first_valid_round = params.first
    last_valid_round = params.last
    fee = params.min_fee
    send_amount = 1

    mnemonic_phrase = "day lecture object wedding slot spider sort sleep fuel input transfer immense uphold blossom discover already consider service arrow tunnel eager peasant gasp absent tray"
    sender_account_address = "ZFLTFLXTOB3F2ZIONLPOTJQJP6R4T3LHHH5ODTOBZX6M2XTQ5RQXQUXUQI"
    sender_sk = "wMEfMI8P5kbzOcvvKl3OGWd3YNwnB3oJcRmofqKIBqzJVzKu83B2XWUOat7ppgl/o8ntZzn64c3BzfzNXnDsYQ=="
    account_private_key = mnemonic.to_private_key(mnemonic_phrase)
    account_public_key = account.address_from_private_key(account_private_key)

    sender_pk = account.address_from_private_key(sender_sk)
    existing_account = account_public_key

    tx = transaction.PaymentTxn(sender_pk, params, receiver_pk, tx_amount)
    signed_tx = tx.sign(account_private_key)

    txid = None
            # TODO: Send the transaction to the testnet
    try:
        acl.send_transaction(signed_tx)
        txid = acl.send_transaction(signed_tx)

    except Exception as e:
        print(e)



    return account_public_key, txid


# Function from Algorand Inc.
def wait_for_confirmation(client, txid):
    """
    Utility function to wait until the transaction is
    confirmed before proceeding.
    """
    last_round = client.status().get('last-round')
    txinfo = client.pending_transaction_info(txid)
    while not (txinfo.get('confirmed-round') and txinfo.get('confirmed-round') > 0):
        print("Waiting for confirmation")
        last_round += 1
        client.status_after_block(last_round)
        txinfo = client.pending_transaction_info(txid)
    print("Transaction {} confirmed in round {}.".format(txid, txinfo.get('confirmed-round')))
    return txinfo


def main():
    private_key, account_address = account.generate_account()
    account_public_key = account.address_from_private_key(private_key)
    send_tokens(account_public_key, 1)



if __name__ == '__main__':
    main()