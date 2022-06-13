import requests
import json


def pin_to_ipfs(data):
	assert isinstance(data, dict), f"Error pin_to_ipfs expects a dictionary"
	# YOUR CODE HERE
	project_id = "2AWyCmr3uu5OI49xkqD9mfYKt8h"
	project_secret = "0686be404d2357bfdbb700bcd02fcb07"
	json_file = json.dumps(data)

	response = requests.post('https://ipfs.infura.io:5001/api/v0/add', files={'file': json_file}, auth=(project_id, project_secret))

	decoded_response = response.json()

	return decoded_response["Hash"]


def get_from_ipfs(cid, content_type="json"):
	assert isinstance(cid, str), f"get_from_ipfs accepts a cid in the form of a string"
	# YOUR CODE HERE

	url = r"https://gateway.pinata.cloud/ipfs/"
	url_content = url + cid
	request = requests.get(url_content)
	data = request.json()

	assert isinstance(data, dict), f"get_from_ipfs should return a dict"
	return data


def main():
	x = dict()
	x["key1"] = "this is a test"
	x["key2"] = 10
	cid = pin_to_ipfs(x)
	get_from_ipfs(cid)



if __name__ == "__main__":
	main()
