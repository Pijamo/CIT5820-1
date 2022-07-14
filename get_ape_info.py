from web3 import Web3
from web3.contract import Contract
from web3.providers.rpc import HTTPProvider
import requests
import json
import time

bayc_address = "0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D"
contract_address = Web3.toChecksumAddress(bayc_address)

# You will need the ABI to connect to the contract
# The file 'abi.json' has the ABI for the bored ape contract
# In general, you can get contract ABIs from etherscan
# https://api.etherscan.io/api?module=contract&action=getabi&address=0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D
with open('/home/codio/workspace/abi.json', 'r') as f:
	abi = json.load(f)

############################
# Connect to an Ethereum node
token = "Mwb3juVAfI1g2RmA1JCGdYk-2_BmFrnLOtbomP1oDa4"
api_url = f"https://c2emjgrvmi7cabd41mpg.bdnodes.net?auth={token}"
provider = HTTPProvider(api_url)
web3 = Web3(provider)


def get_ape_info(apeID):

    token = "Mwb3juVAfI1g2RmA1JCGdYk-2_BmFrnLOtbomP1oDa4"
    api_url = f"https://c2emjgrvmi7cabd41mpg.bdnodes.net?auth={token}"
    provider = HTTPProvider(api_url)
    web3 = Web3(provider)

    assert isinstance(apeID, int), f"{apeID} is not an int"
    assert 1 <= apeID, f"{apeID} must be at least 1"

    data = {'owner': "", 'image': "", 'eyes': ""}

    # YOUR CODE HERE

    url = r"https://gateway.pinata.cloud/ipfs/QmeSjSinHpPnmXmspMjwiXyN6zS4E9zccariGR3jxcaWtq/"
    url_content = url + str(apeID)
    request = requests.get(url_content)
    data_1 = request.json()
    image = data_1['image']
    attributes = data_1['image']
    image = data_1['image']
    eyes = data_1['attributes'][3]['value']



    contract = web3.eth.contract(address=contract_address, abi=abi)
    owner = contract.functions.ownerOf(apeID).call()

    data['owner'] = owner
    data['image'] = image
    data['eyes'] = eyes


    assert isinstance(data, dict), f'get_ape_info{apeID} should return a dict'
    assert all([a in data.keys() for a in
                ['owner', 'image', 'eyes']]), f"return value should include the keys 'owner','image' and 'eyes'"
    print(data['owner'],data['image'],data['eyes'] )
    return data

def main():
    bayc_address = "0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D"
    get_ape_info(1)


if __name__ == '__main__':
    main()