import hashlib
import os
import string
import random


def hash_preimage(target_string):
    if not all( [x in '01' for x in target_string ] ):
        print( "Input should be a string of bits" )
        return

    while True:
        str1 = ''.join(random.choice(string.ascii_letters) for i in range(random.randint(1, 10)))
        m = hashlib.sha256(str1.encode('utf-8')).hexdigest()

        x = bin(int(m, base=16))[2:]  # 0b is appended by bin function
        trailing_bits = x[-len(target_string):]
        if trailing_bits == target_string:
            return str1


def main():
    str1 = hash_preimage("111111111111111111111")
    print(str1)
    m = hashlib.sha256(str1.encode('utf-8')).hexdigest()
    m = bin(int(m, base=16))[2:]
    print(m)
if __name__ == '__main__':
    main()