'''
for a given difference $\varDelta _m$,
compute the correlation of $\varDelta _m \rightarrow \gamma _m = [i]$ for $i \in [0, n-1]$.
'''

import speck as sp
from os import urandom
import numpy as np


word_size = 32
blockSize = 64
MASK_VAL = 2**word_size - 1


def make_target_diff_data(n=10**7, diff=(0x40, 0x0), nr=5, fixedKey=1):
    p0l = np.frombuffer(urandom(n * 4), dtype=np.uint32)
    p0r = np.frombuffer(urandom(n * 4), dtype=np.uint32)
    p1l, p1r = p0l ^ diff[0], p0r ^ diff[1]
    if fixedKey == 1:
        key = np.frombuffer(urandom(12), dtype=np.uint32)
    else:
        key = np.frombuffer(urandom(12 * n), dtype=np.uint32).reshape(3, -1)
    ks = sp.expand_key(key, nr)
    c0l, c0r = sp.encrypt((p0l, p0r), ks)
    c1l, c1r = sp.encrypt((p1l, p1r), ks)
    return c0l, c0r, c1l, c1r


def one_time_experiment(n=10**7, nr=5, diff=(0x40, 0x0), fixedKey=1):
    cor_weight_arr = np.zeros(blockSize, dtype=np.float64)
    # for speck
    c0l, c0r, c1l, c1r = make_target_diff_data(n=n, diff=diff, nr=nr, fixedKey=fixedKey)
    for i in range(blockSize):
        mask = [0, 0]
        index = i // word_size
        offset = i % word_size
        mask[1 - index] |= 1 << offset
        t0l, t0r = c0l & mask[0], c0r & mask[1]
        t1l, t1r = c1l & mask[0], c1r & mask[1]
        tl, tr = t0l ^ t1l, t0r ^ t1r
        tmp = tl ^ tr
        cor = (np.sum(tmp == 0) * 2 - n) / n
        cor_weight_arr[i] = -np.log2(abs(cor))
    return cor_weight_arr


nr = 5
bound = 8       # absolute correlation threshold
print('the current absolute correlation weight threshold is ', bound)

single_bit_DLA_cor_weight = []
for i in range(blockSize):
    if i < word_size:
        diff = (0x0, 1 << i)
    else:
        diff = (1 << (i - word_size), 0x0)
    print('diff is ', diff)
    cor_weight_arr = one_time_experiment(n=2**22, nr=nr, diff=diff, fixedKey=0)
    single_bit_DLA_cor_weight.append(cor_weight_arr)
    strong_unbalanced_bits = [j for j in range(blockSize) if cor_weight_arr[j] < bound]
    # print('the absolute cor threshold is ', bound)
    print('the number of B_S is ', len(strong_unbalanced_bits))
    print('strong unbalanced bits are ', strong_unbalanced_bits)
np.save('./{}r_oneBitDiff_oneBitMask_cor_w.npy'.format(nr), single_bit_DLA_cor_weight)
