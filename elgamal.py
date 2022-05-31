import random
from params import p
from params import g


def keygen():
    q = (p - 1) / 2
    a = random.randint(1, q)

    pk = pow(g, a, p)

    sk = a
    return pk, sk


def encrypt(pk, m):
    r = random.randint(1, p - 1)
    c1 = pow(g, r, p)
    c2 = (m * pow(pk, r, p)) % p
    return [c1, c2]


def decrypt(sk, c):
    m = (c[1] * pow(c[0], p - 1 - sk, p)) % p
    return m


def main():
    keygen()


if __name__ == '__main__':
    main()
