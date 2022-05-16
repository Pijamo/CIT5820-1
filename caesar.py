
def encrypt(key,plaintext):
    ciphertext = ""
    key = key % 26

    for ch in plaintext:
        if ch.isalpha():
            x = ord(ch) + key

            while x > ord('Z'):
                x -= 26
            while x < ord('A'):
                x += 26
            ciphertext += chr(x)

    return ciphertext


def decrypt(key , ciphertext):
    plaintext = ""
    key = key % 26

    for ch in ciphertext:
        if ch.isalpha():
            x = ord(ch) - key


            while x > ord('Z'):
                x -= 26
            while x < ord('A'):
                x += 26
            plaintext += chr(x)

    return plaintext


def main():
    x = encrypt(-87, 'BASE')
    y = decrypt(-87, x)


if __name__ == '__main__':
    main()
