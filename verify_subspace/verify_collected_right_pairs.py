import numpy as np
import lea

diffs = [[0x8a000080, 0x80402080, 0x80402210, 0xc0402234],
         [0x80400014, 0x80000014, 0x88000004, 0x8a000080],
         [0x80000000, 0x80400000, 0x80400010, 0x80400014],
         [0x80000000, 0x80000000, 0x80000000, 0x80000000],
         [0x0, 0x0, 0x0, 0x80000000]]


def verify_collected_plaintext_pairs(plaintexts=None, round_keys=None):
    num = len(plaintexts)
    assert num == len(round_keys)

    for i in range(num):
        pl0, pl1, pl2, pl3 = plaintexts[i][0], plaintexts[i][1], plaintexts[i][2], plaintexts[i][3]
        pr0, pr1, pr2, pr3 = plaintexts[i][0] ^ diffs[0][0], plaintexts[i][1] ^ diffs[0][1], \
                             plaintexts[i][2] ^ diffs[0][2], plaintexts[i][3] ^ diffs[0][3]
        rk = round_keys[i]
        print('Plaintext pair: {}'.format(i))
        for j in range(4):
            cl0, cl1, cl2, cl3 = lea.encrypt((pl0, pl1, pl2, pl3), rk[:j+1])
            cr0, cr1, cr2, cr3 = lea.encrypt((pr0, pr1, pr2, pr3), rk[:j+1])
            d0, d1, d2, d3 = cl0 ^ cr0, cl1 ^ cr1, cl2 ^ cr2, cl3 ^ cr3
            d0, d1, d2, d3 = np.squeeze(d0), np.squeeze(d1), np.squeeze(d2), np.squeeze(d3)
            print('state difference at round {} is ({}, {}, {}, {})'.format(j+1, hex(d0), hex(d1),
                                                                            hex(d2), hex(d3)))


for key_length in [128, 192, 256]:
    for file_no in [0, 1, 2, 3]:
        pair_num = 256
        print('check collected pairs in {}_256_{}_right_pairs.npy'.format(file_no, key_length))
        plaintexts = np.load('./good_data/{}_{}_{}_right_pairs.npy'.format(file_no, pair_num, key_length))
        plaintexts = np.squeeze(plaintexts)
        round_keys = np.load('./good_data/{}_{}_{}_corresponding_rks.npy'.format(file_no, pair_num,
                                                                                 key_length))
        verify_collected_plaintext_pairs(plaintexts=plaintexts, round_keys=round_keys)


