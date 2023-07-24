import lea
from os import urandom
import numpy as np


word_size = 32
block_size = 128


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


def one_time_experiment(n=10**7, nr=5, diff=(0x40, 0x0, 0x0, 0x0), fixedKey=1):
    min_cor = np.sqrt(n) / n
    max_hw = -np.log2(min_cor)
    # for lea
    d0, d1, d2, d3 = make_target_diff_data(n=n, diff=diff, nr=nr, fixedKey=fixedKey)
    diff_data = [d0, d1, d2, d3]
    res = np.zeros(word_size * 4, dtype=np.float64)
    for i in range(word_size * 4):
        index = i // word_size
        offset = i % word_size
        tmp_d = diff_data[3 - index] & (1 << offset)
        cur_cor = (np.sum(tmp_d == 0) * 2 - n) / n
        if abs(cur_cor) >= min_cor * 3:
            res[i] = -np.log2(abs(cur_cor))
        else:
            res[i] = max_hw

    return res


# nr = 8
# cor_res = np.zeros((128, 128), dtype=np.float64)
# for i in range(1, 128):
#     print('i is {}'.format(i))
#     if i < 32:
#         diff = (0x0, 0x0, 0x0, (1 << i) + (1 << (i-1)))
#     elif i < 64:
#         if i == 32:
#             diff = (0x0, 0x0, 1, 1 << 31)
#         else:
#             diff = (0x0, 0x0, (1 << (i - 32)) + (1 << (i - 1 - 32)), 0x0)
#     elif i < 96:
#         if i == 64:
#             diff = (0x0, 1, 1 << 31, 0x0)
#         else:
#             diff = (0x0, (1 << (i-64)) + (1 << (i-1-64)), 0x0, 0x0)
#     else:
#         if i == 96:
#             diff = (1, 1 << 31, 0x0, 0x0)
#         else:
#             diff = ((1 << (i-96)) + (1 << (i-1-96)), 0x0, 0x0, 0x0)
#     cor_res[i] = one_time_experiment(n=2**24, nr=nr, diff=diff, fixedKey=0)
# np.save('./{}r_twoBitDiff_oneBitMask_cor_weight.npy'.format(nr), cor_res)


nr = 8
cor_res = np.zeros((128, 128), dtype=np.float64)
for i in range(block_size):
    print('i is ', i)
    if i < 32:
        diff = (0x0, 0x0, 0x0, 1 << i)
    elif i < 64:
        diff = (0x0, 0x0, 1 << (i - 32), 0x0)
    elif i < 96:
        diff = (0x0, 1 << (i - 64), 0x0, 0x0)
    else:
        diff = (1 << (i - 96), 0x0, 0x0, 0x0)
    print('diff is ', diff)
    cor_res[i] = one_time_experiment(n=2 ** 22, nr=nr, diff=diff, fixedKey=0)
    strong_unbalanced_bits = [j for j in range(block_size) if cor_res[i][j] < 4]
    print('the number of B_S is ', len(strong_unbalanced_bits))
    print('strong unbalanced bits are ', strong_unbalanced_bits)
np.save('./{}r_oneBitDiff_oneBitMask_cor_weight_v2.npy'.format(nr), cor_res)
