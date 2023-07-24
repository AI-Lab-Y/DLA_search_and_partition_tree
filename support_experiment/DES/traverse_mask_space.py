import numpy as np
from os import urandom
import des


word_size = 32
block_size = 64


def make_target_diff_data(n=10**7, nr=3, diff_type=1, diff=(0x40080000, 0x04000000)):
    x0l = np.frombuffer(urandom(n * 4), dtype=np.uint32)
    x0r = np.frombuffer(urandom(n * 4), dtype=np.uint32)
    if diff_type == 1:
        x1l = x0l ^ diff[0]
        x1r = x0r ^ diff[1]
    else:
        x1l = np.frombuffer(urandom(n * 4), dtype=np.uint32)
        x1r = np.frombuffer(urandom(n * 4), dtype=np.uint32)
    p0l = np.zeros((n, 32), dtype=np.uint8)
    p0r = np.zeros((n, 32), dtype=np.uint8)
    p1l = np.zeros((n, 32), dtype=np.uint8)
    p1r = np.zeros((n, 32), dtype=np.uint8)
    for i in range(32):
        off = 31 - i
        p0l[:, i] = (x0l >> off) & 1
        p0r[:, i] = (x0r >> off) & 1
        p1l[:, i] = (x1l >> off) & 1
        p1r[:, i] = (x1r >> off) & 1

    master_keys = np.frombuffer(urandom(n * 8), dtype=np.uint32).reshape(-1, 2)
    keys = np.zeros((n, 64), dtype=np.uint8)
    for i in range(32):
        keys[:, i] = (master_keys[:, 0] >> (31 - i)) & 1
        keys[:, 32 + i] = (master_keys[:, 1] >> (31 - i)) & 1
    subkeys = des.expand_key(keys, nr)

    c0l, c0r = des.encrypt(p0l, p0r, subkeys)
    c1l, c1r = des.encrypt(p1l, p1r, subkeys)
    dl, dr = c0l ^ c1l, c0r ^ c1r
    X = np.concatenate((dl, dr), axis=1)

    return X


def compute_cor(data=None, n=None):
    assert n == data.shape[0]
    tmp = np.zeros(n, dtype=np.uint16)
    for j in range(block_size):
        tmp += data[:, j]
    cor = (np.sum(tmp % 2 == 0) * 2 - n) / n
    cor_hw = -np.log2(np.abs(cor))

    return cor_hw


def main(diff=(0x9, 0x0), nr=5, n=2**18, cor_bound=4):
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
    pos = 6
    if pos < word_size:
        diff = (0x0, 1 << pos)
    else:
        diff = (1 << (pos - word_size), 0x0)
    nr = 4
    hw = 2
    n = 2**18
    cor_bound = 4
    res = main(diff=diff, nr=nr, n=n, cor_bound=cor_bound)
    np.save('./diff{}_{}r_hw{}_DLAs_with_high_cor.npy'.format(pos, nr, hw), res)