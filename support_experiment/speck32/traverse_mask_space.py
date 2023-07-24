import speck as sp
from os import urandom
import numpy as np


block_size = 32
word_size = 16


def make_target_diff_data(n=10**7, diff=(0x40, 0x0), nr=5, fixedKey=1):
    p00 = np.frombuffer(urandom(n * 2), dtype=np.uint16)
    p01 = np.frombuffer(urandom(n * 2), dtype=np.uint16)
    p10, p11 = p00 ^ diff[0], p01 ^ diff[1]
    if fixedKey == 1:
        key = np.frombuffer(urandom(8), dtype=np.uint16).reshape(4, -1)
    else:
        key = np.frombuffer(urandom(8*n), dtype=np.uint16).reshape(4, -1)
    ks = sp.expand_key(key, nr)
    c00, c01 = sp.encrypt((p00, p01), ks)
    c10, c11 = sp.encrypt((p10, p11), ks)
    return c00, c01, c10, c11


def compute_cor(data=None, n=None):
    d0, d1 = data[0], data[1]
    assert n == len(d0)
    tmp = np.zeros(n, dtype=np.uint16)
    for j in range(word_size):
        tmp += (d0 >> j) & 1
        tmp += (d1 >> j) & 1
    cor = (np.sum(tmp % 2 == 0) * 2 - n) / n
    cor_hw = -np.log2(np.abs(cor))
    return cor_hw


def main(diff=(0x0, 0x1), nr=8, n=2**22, cor_bound=4, fixedKey=0):
    basis = (1 << 16) - 1
    # traverse linear masks with hamming weight <= 4
    tuples = []
    # hamming weight 1
    for i in range(block_size):
        v = [i]
        tuples.append(v)
    # hamming weight 2
    for i in range(block_size):
        for j in range(i+1, block_size):
            v = [i, j]
            tuples.append(v)
    # hamming weight 3
    for i1 in range(block_size):
        for i2 in range(i1 + 1, block_size):
            for i3 in range(i2 + 1, block_size):
                v = [i1, i2, i3]
                tuples.append(v)
    # # hamming weight 4
    # for i1 in range(block_size):
    #     for i2 in range(i1 + 1, block_size):
    #         for i3 in range(i2 + 1, block_size):
    #             for i4 in range(i3 + 1, block_size):
    #                 v = [i1, i2, i3, i4]
    #                 tuples.append(v)
    # create dataset
    c00, c01, c10, c11 = make_target_diff_data(n=n, diff=diff, nr=nr, fixedKey=fixedKey)
    # verify the correlation
    res = []
    for x in tuples:
        v = 0
        for i in x:
            v += 1 << i
        v0, v1 = (v >> 16) & basis, v & basis
        d0, d1 = (c00 ^ c10) & v0, (c01 ^ c11) & v1
        data = [d0, d1]
        cor_hw = compute_cor(data=data, n=n)
        if cor_hw < cor_bound:
            tp = [v >> 16, v & (2**16 - 1)]
            res.append(x)
            print('cur output linear mask is ', x)
            print('the cor weight is {}'.format(cor_hw))

    return res


if __name__ == '__main__':
    pos = 22
    if pos < word_size:
        diff = (0x0, 1 << pos)
    else:
        diff = (1 << (pos - word_size), 0x0)
    nr = 5
    hw = 3
    n = 2**18
    cor_bound = 4
    fixedKey = 0
    res = main(diff=diff, nr=nr, n=n, cor_bound=cor_bound, fixedKey=fixedKey)
    np.save('./diff{}_{}r_hw{}_DLAs_with_high_cor.npy'.format(pos, nr, hw), res)