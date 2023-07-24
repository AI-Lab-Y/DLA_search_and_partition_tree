import numpy as np
import math

block_size = 64


def compute_space_size(bit_num=10, hw=2):
    assert bit_num > hw >= 0
    res = 0
    # if your python version >= 3.8, use the following code
    # for i in range(1, hw+1):
    #     res += math.comb(bit_num, hw)

    # if your python version < 3.8, use the following code
    for i in range(1, hw+1):
        r1, r2 = 1, 1
        for j in range(bit_num, bit_num-i, -1):
            r1 = r1 * j
        for j in range(i, 0, -1):
            r2 = r2 * j
        res += r1 // r2

    return res


if __name__ == '__main__':
    pos = 56
    DLAs_with_high_cor = np.load('./diff{}_5r_hw2_DLAs_with_high_cor.npy'.format(pos), allow_pickle=True)

    bit_bias = np.load('./5r_oneBitDiff_oneBitMask_cor_weight.npy')
    bound = 4
    active_bits = [i for i in range(block_size) if bit_bias[pos][i] <= bound]

    print('the number of strong unbalanced bits is ', len(active_bits))
    print('strong unbalanced bits are ', active_bits)

    # set labels for each DLA based on its linear mask
    # label 0: linear mask is only related to weak unbalanced bits
    # label 1: linear mask is only related to strong unbalanced bits
    # label 2: linear mask is related to both weak and strong unbalanced bits
    n = len(DLAs_with_high_cor)
    y = np.zeros(n, dtype=np.uint8)
    for i in range(n):
        cur_mask = DLAs_with_high_cor[i]
        print('mask of the {}-th DLA is {}'.format(i, cur_mask))
        flag = 0
        for j in cur_mask:
            if j in active_bits:
                flag += 1
        if flag == len(cur_mask):
            y[i] = 1
        elif flag > 0:
            y[i] = 2
        else:
            y[i] = 0

    print('the total number of DLAs with high cor in G is ', len(DLAs_with_high_cor))
    # label 0: linear mask is only related to weak unbalanced bits
    print('the number of DLAs with label 0 is ', np.sum(y == 0))
    # label 1: linear mask is only related to strong unbalanced bits
    print('the number of DLAs with label 1 is ', np.sum(y == 1))
    # label 2: linear mask is related to both weak and strong unbalanced bits
    print('the number of DLAs with label 2 is ', np.sum(y == 2))

    hw = 2
    s1 = compute_space_size(bit_num=block_size, hw=2)
    s2 = compute_space_size(bit_num=len(active_bits), hw=2)
    n1 = len(DLAs_with_high_cor)
    n2 = np.sum(y == 1)
    print('the probability that the cor of an DLA picked from Space X_1 is high is ', n1 / s1)
    print('the probability that the cor of an DLA picked from Space X_2 is high is ', n2 / s2)
