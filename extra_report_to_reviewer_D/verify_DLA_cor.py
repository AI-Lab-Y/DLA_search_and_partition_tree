import lea
from os import urandom
import numpy as np


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
    return c00, c01, c02, c03, c10, c11, c12, c13


def one_time_experiment(n=10**7, nr=5, diff=(0x40, 0x0, 0x0, 0x0), mask=(0x40, 0x0, 0x0, 0x0), fixedKey=1):
    # for lea
    c00, c01, c02, c03, c10, c11, c12, c13 = make_target_diff_data(n=n, diff=diff,
                                                                   nr=nr, fixedKey=fixedKey)
    t00, t01, t02, t03 = c00 & mask[0], c01 & mask[1], c02 & mask[2], c03 & mask[3]
    t10, t11, t12, t13 = c10 & mask[0], c11 & mask[1], c12 & mask[2], c13 & mask[3]
    tmp = np.zeros(n, dtype=np.uint32)
    for j in range(word_size):
        tmp += (t00 >> j) & 1
        tmp += (t01 >> j) & 1
        tmp += (t02 >> j) & 1
        tmp += (t03 >> j) & 1
        tmp += (t10 >> j) & 1
        tmp += (t11 >> j) & 1
        tmp += (t12 >> j) & 1
        tmp += (t13 >> j) & 1
    cur_cor = (np.sum(tmp % 2 == 0) * 2 - n) / n
    return cur_cor


def one_time_experiment_with_bs(n=10**7, nr=5, diff=(0x40, 0x0, 0x0, 0x0), mask=(0x40, 0x0, 0x0, 0x0)):
    # for lea
    c00, c01, c02, c03, c10, c11, c12, c13 = make_target_diff_data(n=n, diff=diff,
                                                                   nr=nr, fixedKey=0)
    t00, t01, t02, t03 = c00 & mask[0], c01 & mask[1], c02 & mask[2], c03 & mask[3]
    t10, t11, t12, t13 = c10 & mask[0], c11 & mask[1], c12 & mask[2], c13 & mask[3]
    tmp = np.zeros(n, dtype=np.uint32)
    for j in range(word_size):
        tmp += (t00 >> j) & 1
        tmp += (t01 >> j) & 1
        tmp += (t02 >> j) & 1
        tmp += (t03 >> j) & 1
        tmp += (t10 >> j) & 1
        tmp += (t11 >> j) & 1
        tmp += (t12 >> j) & 1
        tmp += (t13 >> j) & 1
    cur_cnt = np.sum(tmp % 2 == 0)
    return cur_cnt


def verify_experimental_cor(n=10, nr=5, diff=(0x40, 0x0, 0x0, 0x0), mask=(0x40, 0x0, 0x0, 0x0), fixedKey=1):
    bound = round(np.log2(n) / 2) - 2

    if fixedKey == 1:
        t = 100
        res = np.zeros(t, dtype=float)
        for i in range(100):
            print('Test: {}'.format(i))
            cur_cor = one_time_experiment(n=n, nr=nr, diff=diff, mask=mask, fixedKey=fixedKey)
            print('cur cor is {}'.format(cur_cor))
            res[i] = cur_cor
        mean_val = -np.log2(np.abs(np.mean(res)))
        std_val = -np.log2(np.std(res))
        if mean_val <= bound:
            print('The mean and std of experimental cor are {} and {}'.format(mean_val, std_val))
    else:
        cur_cor = one_time_experiment(n=n, nr=nr, diff=diff, mask=mask, fixedKey=fixedKey)
        cor_weight = -np.log2(np.abs(cur_cor))
        if cor_weight <= bound:
            print('cor is {}'.format(cur_cor))
            print('the cor weight is {}'.format(-np.log2(np.abs(cur_cor))))
        else:
            print('the cor weight exceeds the bound.')


def verify_cor_with_multi_batchs(n=10, bs=2**26, nr=5, diff=(0x40, 0x0, 0x0, 0x0), mask=(0x40, 0x0, 0x0, 0x0)):
    bound = round(np.log2(n) / 2) - 2
    batch_num = n // bs
    res = 0
    for i in range(batch_num):
        res += one_time_experiment_with_bs(n=bs, nr=nr, diff=diff, mask=mask)
    cur_cor = (res * 2 - n) / n
    cor_weight = -np.log2(np.abs(cur_cor))
    if cor_weight <= bound:
        print('cor is {}'.format(cur_cor))
        print('the cor weight is {}'.format(-np.log2(np.abs(cur_cor))))
    else:
        print('the cor weight exceeds the bound.')


gamma_m_cor_w_set = np.load('./gamma_m_set.npy', allow_pickle=True)


basis = (1 << 32) - 1
diff = (0x0, 0x0, 0x0, 1 << 31)
nr = 8
cnt = 0
for sample in gamma_m_cor_w_set[::-1]:
    cnt += 1
    gamma_m, cor_w = sample[0], sample[1]
    v = 0
    for i in gamma_m:
        v += 1 << i
    v0, v1, v2, v3 = (v >> 96) & basis, (v >> 64) & basis, (v >> 32) & basis, v & basis
    mask = (v0, v1, v2, v3)

    # set the minimum data complexity
    cor_w_bound_of_Em = 6 + (10 - cor_w) * 2
    n = 2 ** (cor_w_bound_of_Em * 2 + 3 * 2)

    print('Test {}:'.format(cnt))
    print('cur linear mask $\gamma _m$ is {}'.format(gamma_m))
    print('the cor weight of the linear hull \gamma _m --> \gamma _out is ', cor_w)
    # the cor weight of the baseline DLA (see the last row of Table 4) is 6.04 + 10 * 2
    print('the cor weight of the DLA of E_m should not exceed the bound ', cor_w_bound_of_Em)

    print('the data complexity used to evaluate DLA of E_m is 2^{}'.format(np.log2(n) // 1))

    # when the data complexity is too high, evaluate the cor with multiple batches
    bs = 2**28      # adjust bs according to your computer memory
    if n > bs:
        verify_cor_with_multi_batchs(n=n, bs=bs, nr=nr, diff=diff, mask=mask)
    else:
        verify_experimental_cor(n=n, nr=nr, diff=diff, mask=mask, fixedKey=0)