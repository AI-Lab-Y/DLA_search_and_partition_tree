import lea
from os import urandom
import numpy as np


word_size = 32
MASK_VAL = 2**word_size - 1


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


def verify_experimental_cor(n=10, nr=5, diff=(0x40, 0x0, 0x0, 0x0), mask=(0x40, 0x0, 0x0, 0x0), fixedKey=1):
    bound = round(np.log2(n) / 2) - 2

    if fixedKey == 1:
        t = 200
        res = np.zeros(t, dtype=float)
        for i in range(t):
            print('Test: {}'.format(i))
            cur_cor = one_time_experiment(n=n, nr=nr, diff=diff, mask=mask, fixedKey=fixedKey)
            cur_wight = -np.log2(np.abs(cur_cor))
            print('cur cor is {}, the cor weight is {}'.format(cur_cor, cur_wight))
            res[i] = cur_cor
        mean_val = -np.log2(np.abs(np.mean(res)))
        median_val = -np.log2(np.abs(np.median(res)))
        print('among the t experimental correlations,')
        print('the mean weight, median weight are {}, {}'.format(mean_val, median_val))
    else:
        cur_cor = one_time_experiment(n=n, nr=nr, diff=diff, mask=mask, fixedKey=fixedKey)
        cor_weight = -np.log2(np.abs(cur_cor))
        if cor_weight <= bound:
            print('cor is {}'.format(cur_cor))
            print('the cor weight is {}'.format(-np.log2(np.abs(cur_cor))))


# For ARX ciphers E, when E contains round keys,
# the probability of differentials under fixed keys is strong related to the master key.
# Then the correlation of DLAs has the same property too.
# thus, the setting n should be large to ensure each experimental correlation is valid.

n = 2**24
nr = 8
diff = (0x0, 0x0, 0x0, 1 << 31)
# indexs is the linear mask $\gamma _m$
indexs = [8, 41, 42, 73, 74]
val = 0
for i in indexs:
    val += 1 << i
m0, m1, m2, m3 = (val >> 96) & MASK_VAL, (val >> 64) & MASK_VAL, (val >> 32) & MASK_VAL, val & MASK_VAL
mask = (m0, m1, m2, m3)
print('diff is [{}], linear mask is {}'.format(31, indexs))
verify_experimental_cor(n=n, nr=nr, diff=diff, mask=mask, fixedKey=1)