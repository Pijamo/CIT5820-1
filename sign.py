from fastecdsa.curve import secp256k1
from fastecdsa.keys import export_key, gen_keypair

from fastecdsa import curve, ecdsa, keys, point
from hashlib import sha256

def sign(m):
	#generate public key
	#Your code here

	private_key, public_key = keys.gen_keypair(curve.secp256k1)
	r, s = ecdsa.sign(m, private_key)

	
	encrypted_message = []
	encrypted_message.append(r)
	encrypted_message.append(s)


	assert isinstance( public_key, point.Point )
	assert isinstance( r, int )
	assert isinstance( s, int )
	return( public_key, [r,s] )


def main():
	sign("m")


if __name__ == '__main__':
    main()