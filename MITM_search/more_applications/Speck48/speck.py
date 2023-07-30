import numpy as np
from os import urandom

def WORD_SIZE():
    return 24

def ALPHA():
    return 8

def BETA():
    return 3

MASK_VAL = 2**WORD_SIZE() - 1

def rol(x, k):
    x = x & MASK_VAL
    return (((x << k) & MASK_VAL) | (x >> (WORD_SIZE() - k)))

def ror(x, k):
    x = x & MASK_VAL
    return ((x >> k) | ((x << (WORD_SIZE() - k)) & MASK_VAL))

def enc_one_round(p, k):
    c0, c1 = p[0], p[1]
    c0 = ror(c0, ALPHA())
    c0 = (c0 + c1) & MASK_VAL
    c0 = c0 ^ k
    c1 = rol(c1, BETA())
    c1 = c1 ^ c0
    return (c0,c1)

def dec_one_round(c,k):
    c0, c1 = c[0], c[1]
    c1 = c1 ^ c0
    c1 = ror(c1, BETA())
    c0 = c0 ^ k
    c0 = (c0 - c1) & MASK_VAL
    c0 = rol(c0, ALPHA())
    return (c0, c1)


def expand_key(k, t):
    ks = [0 for i in range(t)]
    ks[0] = k[len(k) - 1]
    l = list(reversed(k[:len(k) - 1]))
    tmp = len(l)
    for i in range(t - 1):
        l[i % tmp], ks[i + 1] = enc_one_round((l[i % tmp], ks[i]), i)
    return ks


def encrypt(p, ks):
    x, y = p[0], p[1]
    for k in ks:
        x, y = enc_one_round((x,y), k)
    return (x, y)


def decrypt(c, ks):
    x, y = c[0], c[1]
    for k in reversed(ks):
        x, y = dec_one_round((x,y), k)
    return (x,y)


def check_testvector():
    key = (0x121110, 0x0a0908, 0x020100)
    pt = (0x20796c, 0x6c6172)
    ks = expand_key(key, 22)
    ct = encrypt(pt, ks)
    if ct == (0xc049a5, 0x385adc):
        print('Testvector for speck48/72 verified.')
    else:
        print('Testvector for speck48/72 not verified.')
        return False

    key = (0x1a1918, 0x121110, 0x0a0908, 0x020100)
    pt = (0x6d2073, 0x696874)
    ks = expand_key(key, 23)
    ct = encrypt(pt, ks)
    if ct == (0x735e10, 0xb6445d):
        print('Testvector for speck48/96 verified.')
    else:
        print('Testvector for speck48/96 not verified.')
        return False

    n = 10**6
    pt = np.frombuffer(urandom(8 * n), dtype=np.uint32).reshape(2, n) & MASK_VAL
    key = np.frombuffer(urandom(12 * n), dtype=np.uint32).reshape(3, n) & MASK_VAL
    ks = expand_key(key, 22)
    ct = encrypt(pt, ks)
    pt_tmp = decrypt(ct, ks)
    if np.sum(pt[0] == pt_tmp[0]) == n and np.sum(pt[1] == pt_tmp[1]) == n:
        print('Testdecryption verified.')
    else:
        print('Testdecryption not verified.')
        return False

    return True


def convert_to_binary(arr):
    X = np.zeros((len(arr) * WORD_SIZE(), len(arr[0])), dtype=np.uint8)
    for i in range(len(arr) * WORD_SIZE()):
        index = i // WORD_SIZE()
        offset = WORD_SIZE() - (i % WORD_SIZE()) - 1
        X[i] = (arr[index] >> offset) & 1
    X = X.transpose()
    return X


if __name__ == '__main__':
    check_testvector()