import speck as sp
from os import urandom
import numpy as np


word_size = 24
MASK_VAL = 2**word_size - 1


def make_target_diff_data(n=10**7, diff=(0x40, 0x0), nr=5, fixedKey=1):
    p0l = np.frombuffer(urandom(n * 4), dtype=np.uint32) & MASK_VAL
    p0r = np.frombuffer(urandom(n * 4), dtype=np.uint32) & MASK_VAL
    p1l, p1r = p0l ^ diff[0], p0r ^ diff[1]
    if fixedKey == 1:
        key = np.frombuffer(urandom(12), dtype=np.uint32).reshape(3, -1)
    else:
        key = np.frombuffer(urandom(12 * n), dtype=np.uint32).reshape(3, -1)
    ks = sp.expand_key(key, nr)
    c0l, c0r = sp.encrypt((p0l, p0r), ks)
    c1l, c1r = sp.encrypt((p1l, p1r), ks)
    return c0l, c0r, c1l, c1r


def one_time_experiment(n=10**7, nr=5, diff=(0x40, 0x0), mask=(0x40, 0x0), fixedKey=1):
    c0l, c0r, c1l, c1r = make_target_diff_data(n=n, diff=diff, nr=nr, fixedKey=fixedKey)
    t0l, t0r = c0l & mask[0], c0r & mask[1]
    t1l, t1r = c1l & mask[0], c1r & mask[1]
    tmp = np.zeros(n, dtype=np.uint32)
    for j in range(word_size):
        tmp = tmp + ((t0l >> j) & 1)
        tmp = tmp + ((t0r >> j) & 1)
        tmp = tmp + ((t1l >> j) & 1)
        tmp = tmp + ((t1r >> j) & 1)
    cur_cor = (np.sum(tmp % 2 == 0) * 2 - n) / n
    return cur_cor


def verify_experimental_cor(n=10**7, nr=5, diff=(0x40, 0x0), mask=(0x40, 0x0), fixedKey=1):
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
        print('The mean and median of experimental cor are {} and {}'.format(mean_val, median_val))
    else:
        cur_cor = one_time_experiment(n=n, nr=nr, diff=diff, mask=mask, fixedKey=fixedKey)
        print('cor is {}'.format(cur_cor))
        print('the cor weight is {}'.format(-np.log2(np.abs(cur_cor))))


# For ARX ciphers E, when E contains round keys,
# the probability of differentials under fixed keys is strong related to the master key.
# Then the correlation of DLAs has the same property too.
# thus, the setting n should be large to ensure each experimental correlation is valid.

nr = 6 + 0
pos = 39
if pos < word_size:
    diff = (0, 1 << pos)
else:
    diff = (1 << (pos - word_size), 0)
# indexs is the linear mask $\gamma _m$
indexs = [2]
val = 0
for i in indexs:
    val += 1 << i
v0, v1 = (val >> word_size) & MASK_VAL, val & MASK_VAL
mask = (v0, v1)
print('diff is [{}], linear mask is {}'.format(pos, indexs))
verify_experimental_cor(n=2**24, nr=nr, diff=diff, mask=mask, fixedKey=1)