'''
This file aims at verifying the 34-D subspace.
Since 4 out of 34 basis elements do not affect the difference transition, i.e., Pr=1,
we only need to verify the 30-D subspace composed of the remaining 30 basis elements.

To quickly verify the 30-D subspace, we adopt a two-stage method:
1. build three 22-D subspaces using 22 out of 30 basis elements,
and check whether the plaintext structure consisting of 2^22 pairs passes the 4-round DC.
This step is able to filter invalid plaintext structures very quickly.

2. if a plaintext structure created from a plaintext pair pass the test in the first step,
create from the same plaintext pair a plaintext structure consisting of 2^30 pairs,
then check whether the large plaintext structure passes the 4-round DC.
'''

import numpy as np
from os import urandom
import lea
import random


WORD_SIZE = 32
BLOCK_SIZE = 128
MASK_VAL = (2**WORD_SIZE) - 1

diffs = [[0x8a000080, 0x80402080, 0x80402210, 0xc0402234],
         [0x80400014, 0x80000014, 0x88000004, 0x8a000080],
         [0x80000000, 0x80400000, 0x80400010, 0x80400014],
         [0x80000000, 0x80000000, 0x80000000, 0x80000000],
         [0x0, 0x0, 0x0, 0x80000000]]

# Basis elements :
# Pr = 1:  2, [4, 36], [22, 54, 86], 31
# Pr>= 0.9:  14 ~ 21, [50, 82], 51, 52, [63, 95], 110 ~ 114, 124 ~ 127
# Pr>= 0.8:  23, [46, 78], 53, 83, 104, 105, 115
# Pr>= 0.7:  24, [47, 79]

# 4 basis elements with Pr = 1
NBs = [[2], [4, 36], [22, 54, 86], [31]]

# 30 basis elements with Pr < 1
PNBs = [[14], [15], [16], [17], [18], [19], [20], [21],
        [50, 82], [51], [52], [63, 95],
        [110], [111], [112], [113], [114], [124], [125], [126], [127],
        [23], [46, 78], [53], [83], [104], [105], [115],
        [24], [47, 79]]

# 22 out of 30 basis elements with Pr < 1
PNBs_1 = [[50, 82], [51], [52], [63, 95],
          [110], [111], [112], [113], [114], [124], [125], [126], [127],
          [23], [46, 78], [53], [83], [104], [105], [115],
          [24], [47, 79]]

# 22 out of 30 basis elements with Pr < 1
PNBs_2 = [[14], [15], [16], [17], [18], [19], [20], [21], [50, 82], [51], [52],
          [126], [127],
          [23], [46, 78], [53], [83], [104], [105], [115],
          [24], [47, 79]]

# 22 out of 30 basis elements with Pr < 1
PNBs_3 = [[14], [15], [16], [17], [18], [19], [20], [21],
          [50, 82], [51], [52], [63, 95],
          [110], [111], [112], [113], [114], [124], [125], [126], [127],
          [23]]


def generate_plaintext_structure(arr=None, NBs=None):
    pl0, pl1, pl2, pl3 = arr[0], arr[1], arr[2], arr[3]
    for i in NBs:
        if isinstance(i, int):
            i = [i]
        d0, d1, d2, d3 = 0, 0, 0, 0
        for j in i:
            d = 1 << j
            d0 |= (d >> (WORD_SIZE * 3)) & MASK_VAL
            d1 |= (d >> (WORD_SIZE * 2)) & MASK_VAL
            d2 |= (d >> (WORD_SIZE * 1)) & MASK_VAL
            d3 |= d & MASK_VAL
        pl0 = np.concatenate([pl0, pl0 ^ d0])
        pl1 = np.concatenate([pl1, pl1 ^ d1])
        pl2 = np.concatenate([pl2, pl2 ^ d2])
        pl3 = np.concatenate([pl3, pl3 ^ d3])
    pr0 = pl0 ^ diffs[0][0]
    pr1 = pl1 ^ diffs[0][1]
    pr2 = pl2 ^ diffs[0][2]
    pr3 = pl3 ^ diffs[0][3]
    return pl0, pl1, pl2, pl3, pr0, pr1, pr2, pr3


def check_structure_type(pl=None, pr=None, rk=None, nr=None):
    pl0, pl1, pl2, pl3 = pl[0], pl[1], pl[2], pl[3]
    pr0, pr1, pr2, pr3 = pr[0], pr[1], pr[2], pr[3]
    cl0, cl1, cl2, cl3 = lea.encrypt((pl0, pl1, pl2, pl3), rk)
    cr0, cr1, cr2, cr3 = lea.encrypt((pr0, pr1, pr2, pr3), rk)
    d0 = cl0 ^ cr0 ^ diffs[nr][0]
    d1 = cl1 ^ cr1 ^ diffs[nr][1]
    d2 = cl2 ^ cr2 ^ diffs[nr][2]
    d3 = cl3 ^ cr3 ^ diffs[nr][3]
    if np.any(d0 != 0) or np.any(d1 != 0) or np.any(d2 != 0) or np.any(d3 != 0):
        return 0
    else:
        return 1


def check_structure_type_with_reduced_memory(bs=None, pl=None, NBs=None, rk=None, nr=None):
    # select bs PNBs to form a small subspace, save this small subspace in advance
    NBs_help = [NBs[i] for i in range(bs)]
    space_help_d0 = np.array([0], dtype=np.uint32)
    space_help_d1 = np.array([0], dtype=np.uint32)
    space_help_d2 = np.array([0], dtype=np.uint32)
    space_help_d3 = np.array([0], dtype=np.uint32)
    for i in NBs_help:
        if isinstance(i, int):
            i = [i]
        d0, d1, d2, d3 = 0, 0, 0, 0
        for j in i:
            d = 1 << j
            d0 |= (d >> (WORD_SIZE * 3)) & MASK_VAL
            d1 |= (d >> (WORD_SIZE * 2)) & MASK_VAL
            d2 |= (d >> (WORD_SIZE * 1)) & MASK_VAL
            d3 |= d & MASK_VAL
        space_help_d0 = np.concatenate([space_help_d0, space_help_d0 ^ d0])
        space_help_d1 = np.concatenate([space_help_d1, space_help_d1 ^ d1])
        space_help_d2 = np.concatenate([space_help_d2, space_help_d2 ^ d2])
        space_help_d3 = np.concatenate([space_help_d3, space_help_d3 ^ d3])
    # traverse space_help, and check the structure type using the (|NBs| - bs)-d space
    num = len(space_help_d0)
    reduced_NBs = [NBs[i] for i in range(bs, len(NBs))]
    pl0, pl1, pl2, pl3, pr0, pr1, pr2, pr3 = generate_plaintext_structure(arr=pl, NBs=reduced_NBs)
    for i in range(num):
        d0, d1, d2, d3 = space_help_d0[i], space_help_d1[i], space_help_d2[i], space_help_d3[i]
        tl0, tl1, tl2, tl3 = pl0 ^ d0, pl1 ^ d1, pl2 ^ d2, pl3 ^ d3
        tr0, tr1, tr2, tr3 = pr0 ^ d0, pr1 ^ d1, pr2 ^ d2, pr3 ^ d3
        flag = check_structure_type(pl=[tl0, tl1, tl2, tl3], pr=[tr0, tr1, tr2, tr3], rk=rk, nr=nr)
        if flag == 0:
            return 0
    return 1


def verify_subspace(pl=None, rk=None, nr=None, bs=None):
    # two-stage tests
    # the first stage: check the structure type using three small subspaces,
    # filter invalid structure rapidly

    # small subspace 1
    pl0, pl1, pl2, pl3, pr0, pr1, pr2, pr3 = generate_plaintext_structure(arr=pl, NBs=PNBs_1)
    flag = check_structure_type(pl=[pl0, pl1, pl2, pl3], pr=[pr0, pr1, pr2, pr3], rk=rk, nr=nr)
    if flag == 0:
        return 0

    # small subspace 2
    pl0, pl1, pl2, pl3, pr0, pr1, pr2, pr3 = generate_plaintext_structure(arr=pl, NBs=PNBs_2)
    flag = check_structure_type(pl=[pl0, pl1, pl2, pl3], pr=[pr0, pr1, pr2, pr3], rk=rk, nr=nr)
    if flag == 0:
        return 0

    # small subspace 3
    pl0, pl1, pl2, pl3, pr0, pr1, pr2, pr3 = generate_plaintext_structure(arr=pl, NBs=PNBs_3)
    flag = check_structure_type(pl=[pl0, pl1, pl2, pl3], pr=[pr0, pr1, pr2, pr3], rk=rk, nr=nr)
    if flag == 0:
        return 0

    # the second stage: check the structure type, identify valid structures
    flag = check_structure_type_with_reduced_memory(bs=bs, pl=pl, NBs=PNBs, rk=rk, nr=nr)
    return flag


def preliminary_verify(plaintexts=None, round_keys=None, nr=None):
    cnt = 0
    num = len(plaintexts)
    for i in range(num):
        pl = plaintexts[i]
        rk = round_keys[i]
        pl0, pl1, pl2, pl3, pr0, pr1, pr2, pr3 = generate_plaintext_structure(arr=pl, NBs=NBs)
        flag = check_structure_type(pl=[pl0, pl1, pl2, pl3], pr=[pr0, pr1, pr2, pr3], rk=rk, nr=nr)
        if flag == 1:
            cnt += 1
    if cnt == num:
        print('The four NBs with Pr=1 pass the preliminary test')


def main(key_length=128, bs=4, file_no=None):
    if key_length == 128:
        plaintexts = np.load('./good_data/{}_256_128_right_pairs.npy'.format(file_no))
        round_keys = np.load('./good_data/{}_256_128_corresponding_rks.npy'.format(file_no))
        assert len(plaintexts) == len(round_keys)
    elif key_length == 192:
        plaintexts = np.load('./good_data/{}_256_192_right_pairs.npy'.format(file_no))
        round_keys = np.load('./good_data/{}_256_192_corresponding_rks.npy'.format(file_no))
        assert len(plaintexts) == len(round_keys)
    else:
        plaintexts = np.load('./good_data/{}_256_256_right_pairs.npy'.format(file_no))
        round_keys = np.load('./good_data/{}_256_256_corresponding_rks.npy'.format(file_no))
        assert len(plaintexts) == len(round_keys)
    # preliminary test for the four NBs with Pr=1
    nr = 4
    preliminary_verify(plaintexts=plaintexts, round_keys=round_keys, nr=nr)
    # verify the remaining 30 PNBs
    cnt = 0
    num = len(plaintexts)
    for i in range(num):
        pl = plaintexts[i]
        rk = round_keys[i]
        flag = verify_subspace(pl=pl, rk=rk, nr=nr, bs=bs)
        if flag == 0:
            print('Test {}: not a valid plaintext structure'.format(i))
        else:
            print('Test {}: a valid plaintext structure'.format(i))
            cnt += 1
    print('{} structures checked, and there are {} valid structures'.format(num, cnt))
    return cnt, num


if __name__ == '__main__':
    # user can split the subspace for reducing the required memory
    # the choice of bs: when your computer has 128 / (2**n) GB memory, let bs=n
    cnt = 0
    num = 0
    for i in range(4):
        cur_cnt, cur_num = main(key_length=256, bs=3, file_no=i)
        cnt += cur_cnt
        num += cur_num
    print('{} structures checked, and there are {} valid structures'.format(num, cnt))

    # A faster test plan: build 4 same projects, and run them simultaneously
    # cur_cnt_0, cur_num = main(key_length=256, bs=3, file_no=0)  # file_no \in {0, 1, 2, 3}
