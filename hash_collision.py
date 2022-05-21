import hashlib
import os
import random
import string

def hash_collision(k):
    if not isinstance(k, int):
        print("hash_collision expects an integer")
        return (b'\x00', b'\x00')
    if k < 0:
        print("Specify a positive number of bits")
        return (b'\x00', b'\x00')

    # Collision finding code goes here

    dic = dict()

    while True:
        str1 = ''.join(random.choice(string.ascii_letters) for i in range(random.randint(1, 10)))
        m = hashlib.sha256(str1.encode('utf-8')).hexdigest()

        x = bin(int(m, base=16))[2:]   #0b is appended by bin function
        key = x[-k:]

        if key in dic:
            if dic[key] != str1:
                return str1.encode('utf-8'), dic[key].encode('utf-8')
        else:
            dic[key] = str1


def main():

    #print(x[-8:])
    #y = str(x)

    #print(y)
    k=16
    x,y = hash_collision(k)
    print(x,y)

    test1 = hashlib.sha256(x).hexdigest()
    test2 = hashlib.sha256(y).hexdigest()
    test1hex = bin(int(test1, base=16))
    test2hex = bin(int(test2, base=16))
    print(test1hex[-k:])
    print(test2hex[-k:])


if __name__ == '__main__':
    main()
