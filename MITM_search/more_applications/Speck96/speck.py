import numpy as np
from os import urandom


def WORD_SIZE():
    return(48)


def ALPHA():
    return(8)


def BETA():
    return(3)


MASK_VAL = 2 ** WORD_SIZE() - 1


def shuffle_together(l):
    state = np.random.get_state()
    for x in l:
        np.random.set_state(state)
        np.random.shuffle(x)


def rol(x, k):
    x = x & 0x0000ffffffffffff      # set 48~63 bits to 0
    return(((x << k) & MASK_VAL) | (x >> (WORD_SIZE() - k)))


def ror(x, k):
    x = x & 0x0000ffffffffffff      # set 48~63 bits to 0
    return((x >> k) | ((x << (WORD_SIZE() - k)) & MASK_VAL))


def enc_one_round(p, k):
    c0, c1 = p[0], p[1]
    c0 = ror(c0, ALPHA())
    c0 = (c0 + c1) & MASK_VAL
    c0 = c0 ^ k
    c1 = rol(c1, BETA())
    c1 = c1 ^ c0
    return(c0, c1)


def dec_one_round(c,k):
    c0, c1 = c[0], c[1]
    c1 = c1 ^ c0
    c1 = ror(c1, BETA())
    c0 = c0 ^ k
    c0 = (c0 - c1) & MASK_VAL
    c0 = rol(c0, ALPHA())
    return(c0, c1)


def expand_key(k, t):
    ks = [0 for i in range(t)]
    ks[0] = k[len(k)-1]
    l = list(reversed(k[:len(k)-1]))
    for i in range(t-1):
        l[0], ks[i+1] = enc_one_round((l[0], ks[i]), i)
    return(ks)


def encrypt(p, ks):
    x, y = p[0], p[1]
    for k in ks:
        x, y = enc_one_round((x, y), k)
    return(x, y)


def decrypt(c, ks):
    x, y = c[0], c[1]
    for k in reversed(ks):
        x, y = dec_one_round((x, y), k)
    return(x,y)


def check_testvector():
    key = (0x0d0c0b0a0908, 0x050403020100)
    pt = (0x65776f68202c, 0x656761737520)
    ks = expand_key(key, 28)
    ct = encrypt(pt, ks)
    if (ct == (0x9e4d09ab7178, 0x62bdde8f79aa)):
        print("Testvector verified.")
        return(True)
    else:
        print("Testvector not verified.")
        return(False)


# convert_to_binary takes as input an array of ciphertext pairs
# where the first row of the array contains the lefthand side of the ciphertexts,
# the second row contains the righthand side of the ciphertexts,
# the third row contains the lefthand side of the second ciphertexts,
# and so on
# it returns an array of bit vectors containing the same data
def convert_to_binary(arr):
    X = np.zeros((4 * WORD_SIZE(), len(arr[0])), dtype=np.uint8)
    for i in range(4 * WORD_SIZE()):
        index = i // WORD_SIZE()
        offset = WORD_SIZE() - (i % WORD_SIZE()) - 1
        X[i] = (arr[index] >> offset) & 1
    X = X.transpose()
    return(X)


if __name__ == '__main__':
    check_testvector()
