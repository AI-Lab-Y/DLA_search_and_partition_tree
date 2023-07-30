import speck as sp
from os import urandom
import numpy as np


word_size = 16
blockSize = 32


def make_target_diff_data(n=10**7, diff=(0x40, 0x0), nr=5, fixedKey=1):
    p0l = np.frombuffer(urandom(n * 2), dtype=np.uint16)
    p0r = np.frombuffer(urandom(n * 2), dtype=np.uint16)
    p1l, p1r = p0l ^ diff[0], p0r ^ diff[1]
    if fixedKey == 1:
        key = np.frombuffer(urandom(8), dtype=np.uint16)
    else:
        key = np.frombuffer(urandom(8 * n), dtype=np.uint16).reshape(4, -1)
    ks = sp.expand_key(key, nr)
    c0l, c0r = sp.encrypt((p0l, p0r), ks)
    c1l, c1r = sp.encrypt((p1l, p1r), ks)
    return c0l, c0r, c1l, c1r


# the hamming weight of linear mask is 1
def find_biased_bits(n=10**7, nr=5, diff=(0x40, 0x0), fixedKey=1):
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


# # for one-bit input diff
# nr = 6
# bound = 8
# single_bit_DLA_cor_weight = []
# for i in range(blockSize):
#     if i < word_size:
#         diff = (0x0, 1 << i)
#     else:
#         diff = (1 << (i - word_size), 0x0)
#     print('diff is [{}]'.format(i))
#     cor_weight_arr = find_biased_bits(n=2**22, nr=nr, diff=diff, fixedKey=0)
#     for j in range(blockSize):
#         if cor_weight_arr[j] < bound:
#             print('bit index is {}, cor is {}'.format(j, cor_weight_arr[j]))
#     single_bit_DLA_cor_weight.append(cor_weight_arr)
# np.save('./{}r_single_bit_DLA_cor_weight.npy'.format(nr), single_bit_DLA_cor_weight)


# for two-consecutive-bits input diff
nr = 6
bound = 8
print('the current absolute correlation weight threshold is ', bound)

DLA_cor_weight = []
for i in range(1, blockSize):
    if i < word_size:
        diff = (0x0, (1 << i) + (1 << (i-1)))
    else:
        if i == word_size:
            diff = (1, 1 << (word_size - 1))
        else:
            diff = ((1 << (i - word_size)) + (1 << (i - 1 - word_size)), 0x0)
    print('diff is [{}, {}]'.format(i, i-1))
    cor_weight_arr = find_biased_bits(n=2**22, nr=nr, diff=diff, fixedKey=0)
    DLA_cor_weight.append(cor_weight_arr)
    strong_unbalanced_bits = [j for j in range(blockSize) if cor_weight_arr[j] < bound]
    # print('the absolute cor threshold is ', bound)
    print('the number of B_S is ', len(strong_unbalanced_bits))
    print('strong unbalanced bits are ', strong_unbalanced_bits)
np.save('./{}r_twoBitDiff_oneBitMask_cor_w.npy'.format(nr), DLA_cor_weight)
