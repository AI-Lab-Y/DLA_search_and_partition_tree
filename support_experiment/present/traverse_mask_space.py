import numpy as np
from os import urandom
import present as pt


block_size = 64


def make_target_diff_data(n=10 ** 7, nr=3, diff_type=1, diff=0x9):
    x0 = np.frombuffer(urandom(n * 8), dtype=np.uint64)
    if diff_type == 1:
        x1 = x0 ^ diff
    else:
        x1 = np.frombuffer(urandom(n * 8), dtype=np.uint64)
    p0 = np.zeros((n, 64), dtype=np.uint8)
    p1 = np.zeros((n, 64), dtype=np.uint8)
    for i in range(64):
        off = 63 - i
        p0[:, i] = (x0 >> off) & 1
        p1[:, i] = (x1 >> off) & 1

    master_keys = np.frombuffer(urandom(n * 80), dtype=np.uint8).reshape(-1, 80) & 1
    subkeys = pt.expand_key(master_keys, nr)
    c0 = pt.encrypt(p0, subkeys)
    c1 = pt.encrypt(p1, subkeys)
    X = c0 ^ c1
    return X


def compute_cor(data=None, n=None):
    assert n == data.shape[0]
    tmp = np.zeros(n, dtype=np.uint16)
    for j in range(block_size):
        tmp += data[:, j]
    cor = (np.sum(tmp % 2 == 0) * 2 - n) / n
    cor_hw = -np.log2(np.abs(cor))
    return cor_hw


def main(diff=0x9, nr=5, n=2**18, cor_bound=4):
    # traverse linear masks with hamming weight <= 2
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
    # create dataset
    data = make_target_diff_data(n=n, diff=diff, nr=nr)
    # verify the correlation
    res = []
    for x in tuples:
        mask = np.zeros(block_size, dtype=np.uint8)
        for i in x:
            mask[block_size - 1 - i] = 1
        mask_data = data * mask
        cor_hw = compute_cor(data=mask_data, n=n)
        if cor_hw < cor_bound:
            res.append(x)
            print('cur output linear mask is ', x)
            print('the cor weight is {}'.format(cor_hw))

    return res


if __name__ == '__main__':
    pos = 28
    diff = 1 << pos
    nr = 5
    hw = 2
    n = 2**18
    cor_bound = 4
    res = main(diff=diff, nr=nr, n=n, cor_bound=cor_bound)
    np.save('./diff{}_{}r_hw{}_DLAs_with_high_cor.npy'.format(pos, nr, hw), res)