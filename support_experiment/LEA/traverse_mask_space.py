import lea
from os import urandom
import numpy as np


block_size = 128
word_size = 32


def make_target_diff_data(n=10**7, diff=(0x40, 0x0, 0x0, 0x0), nr=5, fixedKey=1, kl=128):
    p00 = np.frombuffer(urandom(n * 4), dtype=np.uint32)
    p01 = np.frombuffer(urandom(n * 4), dtype=np.uint32)
    p02 = np.frombuffer(urandom(n * 4), dtype=np.uint32)
    p03 = np.frombuffer(urandom(n * 4), dtype=np.uint32)
    p10, p11, p12, p13 = p00 ^ diff[0], p01 ^ diff[1], p02 ^ diff[2], p03 ^ diff[3]
    m = kl // 8
    if fixedKey == 1:
        key = np.frombuffer(urandom(m), dtype=np.uint32)
    else:
        key = np.frombuffer(urandom(m * n), dtype=np.uint32).reshape(m // 4, -1)
    ks = lea.expand_key(key, nr, key_bit_length=kl)
    c00, c01, c02, c03 = lea.encrypt((p00, p01, p02, p03), ks)
    c10, c11, c12, c13 = lea.encrypt((p10, p11, p12, p13), ks)
    d0, d1, d2, d3 = c00 ^ c10, c01 ^ c11, c02 ^ c12, c03 ^ c13

    return d0, d1, d2, d3


def compute_cor(data=None, n=None):
    d0, d1, d2, d3 = data[0], data[1], data[2], data[3]
    assert n == len(d0)
    tmp = np.zeros(n, dtype=np.uint32)
    for j in range(word_size):
        tmp += (d0 >> j) & 1
        tmp += (d1 >> j) & 1
        tmp += (d2 >> j) & 1
        tmp += (d3 >> j) & 1
    cor = (np.sum(tmp % 2 == 0) * 2 - n) / n
    cor_hw = -np.log2(np.abs(cor))
    return cor_hw


def main(diff=(0x0, 0x1, 0x0, 0x0), nr=8, n=2**22, cor_bound=4, fixedKey=0):
    basis = (1 << 32) - 1
    # traverse linear masks with hamming weight <= 2
    tuples = []
    for i in range(block_size):
        v = [i]
        tuples.append(v)
    for i in range(block_size):
        for j in range(i+1, block_size):
            v = [i, j]
            tuples.append(v)
    # create dataset
    d0, d1, d2, d3 = make_target_diff_data(n=n, diff=diff, nr=nr, fixedKey=fixedKey)

    # verify the correlation
    res = []
    for x in tuples:
        v = 0
        for i in x:
            v += 1 << i
        v0, v1, v2, v3 = (v >> 96) & basis, (v >> 64) & basis, (v >> 32) & basis, v & basis
        mask_d0, mask_d1, mask_d2, mask_d3 = d0 & v0, d1 & v1, d2 & v2, d3 & v3
        data = [mask_d0, mask_d1, mask_d2, mask_d3]
        cor_w = compute_cor(data=data, n=n)
        if cor_w < cor_bound:
            res.append(x)
            print('cur output linear mask is ', x)
            print('the cor weight is {}'.format(cor_w))

    return res


if __name__ == '__main__':
    pos = 110
    if pos < 32:
        diff = (0x0, 0x0, 0x0, 1 << pos)
    elif pos < 64:
        diff = (0x0, 0x0, 1 << (pos - 32), 0x0)
    elif pos < 96:
        diff = (0x0, 1 << (pos - 64), 0x0, 0x0)
    else:
        diff = (1 << (pos - 96), 0x0, 0x0, 0x0)
    print('diff is ', diff)
    nr = 8
    hw = 2
    n = 2 ** 20
    cor_bound = 4
    fixedKey = 0
    res = main(diff=diff, nr=nr, n=n, cor_bound=cor_bound, fixedKey=fixedKey)
    np.save('./diff{}_{}r_hw{}_DLAs_with_high_cor.npy'.format(pos, nr, hw), res)