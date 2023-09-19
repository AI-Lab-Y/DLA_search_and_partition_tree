import lea
from os import urandom
import numpy as np


word_size = 32
blockSize = 128


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


# the hamming weight of linear mask is 1
def find_biased_bits(n=10**7, nr=5, diff=(0x40, 0x0, 0x0, 0x0), fixedKey=1):
    cor_weight_arr = np.zeros(blockSize, dtype=np.float64)
    # for lea
    c00, c01, c02, c03, c10, c11, c12, c13 = make_target_diff_data(n=n, diff=diff,
                                                                   nr=nr, fixedKey=fixedKey)
    for i in range(blockSize):
        mask = [0, 0, 0, 0]
        index = i // word_size
        offset = i % word_size
        mask[3 - index] |= 1 << offset
        t00, t01, t02, t03 = c00 & mask[0], c01 & mask[1], c02 & mask[2], c03 & mask[3]
        t10, t11, t12, t13 = c10 & mask[0], c11 & mask[1], c12 & mask[2], c13 & mask[3]
        t0, t1, t2, t3 = t00 ^ t10, t01 ^ t11, t02 ^ t12, t03 ^ t13
        tmp = t0 ^ t1 ^ t2 ^ t3
        cor = (np.sum(tmp == 0) * 2 - n) / n
        cor_weight_arr[i] = -np.log2(abs(cor))
    return cor_weight_arr

nr = 8
bound = 8       # absolute correlation threshold
print('the current absolute correlation weight threshold is ', bound)

# single_bit_DLA_cor_weight = []
# for i in range(blockSize):
#     if i < 32:
#         diff = (0x0, 0x0, 0x0, 1 << i)
#     elif i < 64:
#         diff = (0x0, 0x0, 1 << (i - 32), 0x0)
#     elif i < 96:
#         diff = (0x0, 1 << (i - 64), 0x0, 0x0)
#     else:
#         diff = (1 << (i - 96), 0x0, 0x0, 0x0)
#     print('diff is [{}]'.format(i))
#     cor_weight_arr = find_biased_bits(n=2**22, nr=nr, diff=diff, fixedKey=0)
#     single_bit_DLA_cor_weight.append(cor_weight_arr)
#     strong_unbalanced_bits = [j for j in range(blockSize) if cor_weight_arr[j] < bound]
#     print('the number of B_S is ', len(strong_unbalanced_bits))
#     print('strong unbalanced bits are ', strong_unbalanced_bits)
# np.save('./{}r_oneBitDiff_oneBitMask_cor_w.npy'.format(nr), single_bit_DLA_cor_weight)


two_bit_DLA_cor_weight = []
for i in range(1, blockSize):
    if i < 32:
        tp1 = 1 << i
        tp2 = 1 << (i-1)
        diff = (0x0, 0x0, 0x0, tp1 + tp2)
    elif i < 64:
        if i == 32:
            diff = (0x0, 0x0, 1, 1 << 31)
        else:
            tp1 = 1 << (i - 32)
            tp2 = 1 << (i - 1 - 32)
            diff = (0x0, 0x0, tp1 + tp2, 0x0)
    elif i < 96:
        if i == 64:
            diff = (0x0, 1, 1 << 31, 0x0)
        else:
            tp1 = 1 << (i - 64)
            tp2 = 1 << (i - 1 - 64)
            diff = (0x0, tp1 + tp2, 0x0, 0x0)
    else:
        if i == 96:
            diff = (1, 1 << 31, 0x0, 0x0)
        else:
            tp1 = 1 << (i - 96)
            tp2 = 1 << (i - 1 - 96)
            diff = (tp1 + tp2, 0x0, 0x0, 0x0)
    print('diff is [{}, {}]'.format(i, i-1))
    cor_weight_arr = find_biased_bits(n=2**22, nr=nr, diff=diff, fixedKey=0)
    two_bit_DLA_cor_weight.append(cor_weight_arr)
    strong_unbalanced_bits = [j for j in range(blockSize) if cor_weight_arr[j] < bound]
    print('the number of B_S is ', len(strong_unbalanced_bits))
    print('strong unbalanced bits are ', strong_unbalanced_bits)
np.save('./{}r_twoBitDiff_oneBitMask_cor_w.npy'.format(nr), two_bit_DLA_cor_weight)
