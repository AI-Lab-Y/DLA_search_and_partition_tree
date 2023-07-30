
import present as pt
import numpy as np
from os import urandom

block_size = 64


def make_target_diff_data(n=10 ** 7, nr=3, diff_type=1, diff=0x9):
    x0 = np.frombuffer(urandom(n * 8), dtype=np.uint64)  # .reshape(-1, 1)
    if diff_type == 1:
        x1 = x0 ^ diff
    else:
        x1 = np.frombuffer(urandom(n * 8), dtype=np.uint64)  # .reshape(-1, 1)
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


def one_time_experiment(n=10**7, nr=5, diff=0x40):
    min_cor = np.sqrt(n) / n
    max_hw = -np.log2(min_cor)
    # for lea
    diff_data = make_target_diff_data(n=n, diff=diff, nr=nr)
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


nr = 5
bound = 4
cor_res = np.zeros((64, 64), dtype=np.float64)
for i in range(block_size):
    print('i is {}'.format(i))
    diff = 1 << i
    cor_res[i] = one_time_experiment(n=2**22, nr=nr, diff=diff)
    strong_unbalanced_bits = [j for j in range(block_size) if cor_res[i][j] < bound]
    print('the number of B_S is ', len(strong_unbalanced_bits))
    print('strong unbalanced bits are ', strong_unbalanced_bits)
np.save('./{}r_oneBitDiff_oneBitMask_cor_weight.npy'.format(nr), cor_res)
