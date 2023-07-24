import numpy as np
import des
from os import urandom


word_size = 32
block_size = 64


def make_target_diff_samples(n=10**7, nr=3, diff_type=1, diff=(0x40080000, 0x04000000)):
    x0l = np.frombuffer(urandom(n * 4), dtype=np.uint32)  # .reshape(-1, 1)
    x0r = np.frombuffer(urandom(n * 4), dtype=np.uint32)  # .reshape(-1, 1)
    if diff_type == 1:
        x1l = x0l ^ diff[0]
        x1r = x0r ^ diff[1]
    else:
        x1l = np.frombuffer(urandom(n * 4), dtype=np.uint32)  # .reshape(-1, 1)
        x1r = np.frombuffer(urandom(n * 4), dtype=np.uint32)  # .reshape(-1, 1)
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


def one_time_experiment(n=10**7, nr=5, diff=(0x40, 0x0)):
    min_cor = np.sqrt(n) / n
    max_hw = -np.log2(min_cor)
    # for des
    diff_data = make_target_diff_samples(n=n, nr=nr, diff_type=1, diff=diff)
    res = np.zeros(block_size, dtype=np.float64)
    for i in range(block_size):
        tmp_d = diff_data[:, block_size - 1 - i]
        cur_cor = (np.sum(tmp_d == 0) * 2 - n) / n
        if abs(cur_cor) >= min_cor * 3:
            res[i] = -np.log2(abs(cur_cor))
        else:
            res[i] = max_hw
    print('diff is ', diff)
    # print('single bit cor is ', res)
    return res


nr = 4
cor_res = np.zeros((64, 64), dtype=np.float64)
for i in range(block_size):
    print('i is {}'.format(i))
    if i < word_size:
        diff = (0, 1 << i)
    else:
        diff = (1 << (i - word_size), 0)
    cor_res[i] = one_time_experiment(n=2**22, nr=nr, diff=diff)
    strong_unbalanced_bits = [j for j in range(block_size) if cor_res[i][j] < 4]
    print('the number of B_S is ', len(strong_unbalanced_bits))
    print('strong unbalanced bits are ', strong_unbalanced_bits)
np.save('./{}r_oneBitDiff_oneBitMask_cor_weight.npy'.format(nr), cor_res)