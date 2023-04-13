'''
This file aims at searching for right pairs of a 4-round DC of LEA.
We adopt the work proposed in [1] to accelerate the process of collecting right pairs.
Concretely, by letting plaintext and the first round key satisfy some conditions
(see Observation 1 in [1]),
a given one round differential will hold with a probability of 1.

[1] Yi Chen and Zhenzhen Bao and Yantian Shen and Hongbo Yu.
    A Deep Learning aided Key Recovery Framework for Large-State Block Ciphers.
    Cryptology ePrint Archive, Paper 2022/1659. Doi:10.1360/SSI-2022-0298.

Note that we use the real key schedule of LEA, instead of a free key schedule.
'''

import numpy as np
from os import urandom
import lea
import random


WORD_SIZE = 32
BLOCK_SIZE = 128
MASK_VAL = (2**WORD_SIZE) - 1

delta = [0xc3efe9db, 0x44626b02, 0x79e27c8a, 0x78df30ec, 0x715ea49e, 0xc785da0a, 0xe04ef22a, 0xe5c40957]
delta = np.array(delta, dtype=np.uint32).reshape(8, 1)

# for our implementation,
# the time complexity of collecting a right pair is about 2^{16} * c where c is a constant whose value is related
# to the process of adjusting one plaintext and the first round key.
diffs = [[0x8a000080, 0x80402080, 0x80402210, 0xc0402234],      # Diff. Prob. Weight
         [0x80400014, 0x80000014, 0x88000004, 0x8a000080],      # -17
         [0x80000000, 0x80400000, 0x80400010, 0x80400014],      # -10
         [0x80000000, 0x80000000, 0x80000000, 0x80000000],      # -6
         [0x0, 0x0, 0x0, 0x80000000]]                           # 0


# two inputs of a modulo addition are px ^ xk and py ^ yk.
# adjust (xk, py) to make the XOR differential holds with a probability of 1
def meta_adjust(px, py, xk, yk, dx, dy, dz):
    new_arr = [px, py, xk, yk]
    d_xyz = dx ^ dy ^ dz
    for i in range(31):
        t_px, t_py, t_xk, t_yk = new_arr[0], new_arr[1], new_arr[2], new_arr[3]
        x, y = t_px ^ t_xk, t_py ^ t_yk
        xi = (x >> i) & 1
        yi = (y >> i) & 1
        dxi, dyi, dzi = (dx >> i) & 1, (dy >> i) & 1, (dz >> i) & 1
        if dxi == dyi and dxi == dzi:
            continue
        if dxi == dyi:
            tb = ((d_xyz >> (i + 1)) & 1) ^ dxi ^ ((y >> i) & 1)
            if tb != xi:
                new_arr[2] = t_xk ^ (1 << i)
        else:
            if i == 0:
                ci = 0
            else:
                mask_x = new_arr[0] ^ new_arr[2]
                mask_y = new_arr[1] ^ new_arr[3]
                ans = (mask_x + mask_y) ^ mask_x ^ mask_y
                ci = (ans >> i) & 1

            cp = (d_xyz >> i) & 1
            if dxi == cp:
                tb = ((d_xyz >> (i + 1)) & 1) ^ dxi ^ ci
                if tb != xi:
                    new_arr[2] = t_xk ^ (1 << i)
            else:
                tb = ((d_xyz >> (i + 1)) & 1) ^ dyi ^ ci
                if tb != yi:
                    new_arr[1] = t_py ^ (1 << i)
    return new_arr[0], new_arr[1], new_arr[2], new_arr[3]


# compute the master key according to the first round key
def compute_master_key(sk, key_length=128):
    m = key_length // WORD_SIZE
    dt = delta[0]
    mk = np.zeros((m, 1), dtype=np.uint32)
    for i in range(m):
        mk[i][0] = random.randint(0, MASK_VAL)
    if key_length == 128:
        T = [sk[0], sk[1], sk[2], sk[4]]
        T[0] = lea.ror(T[0], 1) - lea.rol(dt, 0)
        T[1] = lea.ror(T[1], 3) - lea.rol(dt, 1)
        T[2] = lea.ror(T[2], 6) - lea.rol(dt, 2)
        T[3] = lea.ror(T[3], 11) - lea.rol(dt, 3)
        mk[0][0], mk[1][0], mk[2][0], mk[3][0] = T[0].copy(), T[1].copy(), T[2].copy(), T[3].copy()
    elif key_length == 192:
        T = [sk[0], sk[1], sk[2], sk[3], sk[4], sk[5]]
        T[0] = lea.ror(T[0], 1) - lea.rol(dt, 0)
        T[1] = lea.ror(T[1], 3) - lea.rol(dt, 1)
        T[2] = lea.ror(T[2], 6) - lea.rol(dt, 2)
        T[3] = lea.ror(T[3], 11) - lea.rol(dt, 3)
        T[4] = lea.ror(T[4], 13) - lea.rol(dt, 4)
        T[5] = lea.ror(T[5], 17) - lea.rol(dt, 5)
        mk[0][0], mk[1][0], mk[2][0], mk[3][0], mk[4][0], mk[5][0] = T[0].copy(), T[1].copy(), \
                                                                     T[2].copy(), T[3].copy(), \
                                                                     T[4].copy(), T[5].copy()
    else:
        T = [sk[0], sk[1], sk[2], sk[3], sk[4], sk[5]]
        T[0] = lea.ror(T[0], 1) - lea.rol(dt, 0)
        T[1] = lea.ror(T[1], 3) - lea.rol(dt, 1)
        T[2] = lea.ror(T[2], 6) - lea.rol(dt, 2)
        T[3] = lea.ror(T[3], 11) - lea.rol(dt, 3)
        T[4] = lea.ror(T[4], 13) - lea.rol(dt, 4)
        T[5] = lea.ror(T[5], 17) - lea.rol(dt, 5)
        mk[0][0], mk[1][0], mk[2][0], mk[3][0], mk[4][0], mk[5][0] = T[0].copy(), T[1].copy(), \
                                                                     T[2].copy(), T[3].copy(), \
                                                                     T[4].copy(), T[5].copy()
    return mk


def adjust_plaintext_and_master_keys(arr, sk, key_length=256):
    p0, p1, p2, p3 = arr[0], arr[1], arr[2], arr[3]

    # adjust plaintext and the first round key
    # adjust (k0, p1) based on the first addition
    dx, dy, dz = diffs[0][0], diffs[0][1], lea.ror(diffs[1][0], 9)
    p0, p1, k0, k1 = meta_adjust(px=p0, py=p1, xk=sk[0], yk=sk[1], dx=dx, dy=dy, dz=dz)
    sk[0] = k0
    assert k1 == sk[1]

    # adjust (k2, p2) based on the second addition
    dx, dy, dz = diffs[0][1], diffs[0][2], lea.rol(diffs[1][1], 5)
    p1, p2, k2, k3 = meta_adjust(px=p1, py=p2, xk=sk[2], yk=sk[3], dx=dx, dy=dy, dz=dz)
    sk[2] = k2

    # adjust (k4, p3) based on the third addition
    dx, dy, dz = diffs[0][2], diffs[0][3], lea.rol(diffs[1][2], 3)
    p2, p3, k4, k5 = meta_adjust(px=p2, py=p3, xk=sk[4], yk=sk[5], dx=dx, dy=dy, dz=dz)
    sk[4] = k4

    # get the master key according to the adjusted round key
    mk = compute_master_key(sk, key_length=key_length)
    return p0, p1, p2, p3, mk


def find_right_pairs(n=10**3, nr=4, key_length=256, file_no=None):
    rp = []
    rks = []
    num = 0
    cnt = 0
    while num < n:
        cnt += 1
        print('\r {} plaintext pairs generated'.format(cnt), end='')
        # generate master key and one plaintext
        m = key_length // 32
        mk = np.frombuffer(urandom(4 * m * 1), dtype=np.uint32).reshape(m, -1)
        one_round_rk = lea.expand_key(mk, 1, key_bit_length=key_length)
        one_round_rk = np.squeeze(one_round_rk)
        pl0 = np.frombuffer(urandom(4 * 1), dtype=np.uint32)
        pl1 = np.frombuffer(urandom(4 * 1), dtype=np.uint32)
        pl2 = np.frombuffer(urandom(4 * 1), dtype=np.uint32)
        pl3 = np.frombuffer(urandom(4 * 1), dtype=np.uint32)
        # adjust the plaintext and master key for satisfying the necessary conditions
        pl0, pl1, pl2, pl3, mk = \
            adjust_plaintext_and_master_keys(arr=[pl0, pl1, pl2, pl3],
                                             sk=one_round_rk, key_length=key_length)
        rk = lea.expand_key(mk, nr=nr, key_bit_length=key_length)
        # collect encrypted states
        pr0, pr1, pr2, pr3 = pl0 ^ diffs[0][0], pl1 ^ diffs[0][1], \
                             pl2 ^ diffs[0][2], pl3 ^ diffs[0][3]
        flag = 1
        # check the state difference at each round
        for i in range(1, nr+1):
            cl0, cl1, cl2, cl3 = lea.encrypt((pl0, pl1, pl2, pl3), rk[:i])
            cr0, cr1, cr2, cr3 = lea.encrypt((pr0, pr1, pr2, pr3), rk[:i])
            if cl0 ^ cr0 != diffs[i][0] or cl1 ^ cr1 != diffs[i][1]:
                flag = flag & 0
                break
            if cl2 ^ cr2 != diffs[i][2] or cl3 ^ cr3 != diffs[i][3]:
                flag = flag & 0
                break
        if flag:
            num += 1
            print('')
            print('the {}-th right pair is found'.format(num))
            rp.append([pl0, pl1, pl2, pl3])
            rks.append(rk)
    np.save('./{}_{}_{}_right_pairs.npy'.format(file_no, n, key_length), rp)
    np.save('./{}_{}_{}_corresponding_rks.npy'.format(file_no, n, key_length), rks)


if __name__ == '__main__':
    # We generate-and-adjust plaintext pairs one by one.

    # plan A: collect 2^10 right pairs by running this code only once
    # Due to the bad memory management mechanism of Python,
    # the time consumption of collecting 2^8 right pairs will increase rapidly.
    # Thus, we do not recommend plan A.
    # for i in range(4):
    #     find_right_pairs(n=2**8, nr=4, key_length=128, file_no=i)

    # plan B: collect 2^8 right pairs each time
    # when 2^8 pairs are collected, increase the file_no and run this code again.
    # Or you can build four same projects and run them simultaneously.
    # Plan B is far faster than plan A

    find_right_pairs(n=2 ** 8, nr=4, key_length=128, file_no=0)
    # find_right_pairs(n=2 ** 8, nr=4, key_length=128, file_no=1)
    # find_right_pairs(n=2 ** 8, nr=4, key_length=128, file_no=2)
    # find_right_pairs(n=2 ** 8, nr=4, key_length=128, file_no=3)
