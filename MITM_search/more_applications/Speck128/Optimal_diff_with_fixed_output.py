import os
import time
import random

# fixed output difference
# diff_out = (1 << (64 - 64), 0)
# for speck32
# diff_out = (0x0040, 0x0)    # [2, 6, 11, 17, 23, 28, 32]
# diff_out = (1 << (22 - 16), 0x0)    # [2, 6, 11]
# diff_out = (0x2800, 0x0010)


# for speck32
# diff_out = (0x0, 1 << 0)    # [1, 4, 8]
# diff_out = (0x0, 1 << 1)    # [0, 3, 7]
# diff_out = (0x0, 1 << 2)    # [1, 4, 8]
# diff_out = (0x0, 1 << 3)    # [1, 3, 6]
# diff_out = (0x0, 1 << 4)    # [1, 4, 8]
# diff_out = (0x0, 1 << 5)    # [1, 4, 7]
# diff_out = (0x0, 1 << 6)    # [1, 4, 8]
# diff_out = (0x0, 1 << 7)    # [1, 4, 7]
# diff_out = (0x0, 1 << 8)    # [1, 4, 8]
# diff_out = (0x0, 1 << 9)    # [1, 4, 8]
# diff_out = (0x0, 1 << 10)   # [1, 3, 7]
# diff_out = (0x0, 1 << 11)   # [1, 4, 8]
# diff_out = (0x0, 1 << 12)   # [1, 3, 6]
# diff_out = (0x0, 1 << 13)   # [1, 4, 8]
# diff_out = (0x0, 1 << 14)   # [1, 4, 8]
# diff_out = (0x0, 1 << 15)   # [1, 4, 8]
# diff_out = (1 << 0, 0x0)   # [2, 6, 11]
# diff_out = (1 << 1, 0x0)   # [1, 5, 9]
# diff_out = (1 << 2, 0x0)   # [2, 6, 11]
# diff_out = (1 << 3, 0x0)   # [2, 5, 9]
# diff_out = (1 << 4, 0x0)   # [2, 6, 11]
# diff_out = (1 << 5, 0x0)   # [2, 6, 10]
# diff_out = (1 << 6, 0x0)   # [2, 6, 11]
# diff_out = (1 << 7, 0x0)   # [2, 6, 10]
# diff_out = (1 << 8, 0x0)   # [2, 5, 10]
# diff_out = (1 << 9, 0x0)   # [2, 6, 11]
# diff_out = (1 << 10, 0x0)   # [2, 5, 10]
# diff_out = (1 << 11, 0x0)   # [2, 6, 11]
# diff_out = (1 << 12, 0x0)   # [2, 5, 9]
# diff_out = (1 << 13, 0x0)   # [2, 6, 11]
# diff_out = (1 << 14, 0x0)   # [2, 6, 11]
# diff_out = (1 << 15, 0x0)   # [1, 5, 10]


# for speck48
# diff_out = (0x0, 1 << 0)    # [1, 4, 9]
# diff_out = (0x0, 1 << 1)    # [1, 4, 9]
# diff_out = (0x0, 1 << 2)    # [0, 3, 8]
# diff_out = (0x0, 1 << 3)    # [1, 4, 9]
# diff_out = (0x0, 1 << 4)    # [1, 4, 9]
# diff_out = (0x0, 1 << 5)    # [1, 3, 8]
# diff_out = (0x0, 1 << 6)    # [1, 4, 9]
# diff_out = (0x0, 1 << 7)    # [1, 4, 9]
# diff_out = (0x0, 1 << 8)    # [1, 4, 8]
# diff_out = (0x0, 1 << 9)    # [1, 4, 9]
# diff_out = (0x0, 1 << 10)    # [1, 4, 8]
# diff_out = (0x0, 1 << 11)    # [1, 4, 9]
# diff_out = (0x0, 1 << 12)    # [1, 4, 9]
# diff_out = (0x0, 1 << 13)    # [1, 4, 8]
# diff_out = (0x0, 1 << 14)    # [1, 4, 9]
# diff_out = (0x0, 1 << 15)    # [1, 4, 9]
# diff_out = (0x0, 1 << 16)    # [1, 4, 8]
# diff_out = (0x0, 1 << 17)    # [1, 4, 9]
# diff_out = (0x0, 1 << 18)    # [1, 3, 8]
# diff_out = (0x0, 1 << 19)    # [1, 4, 9]
# diff_out = (0x0, 1 << 20)    # [1, 4, 9]
# diff_out = (0x0, 1 << 21)    # [1, 3, 7]
# diff_out = (0x0, 1 << 22)    # [1, 4, 9]
# diff_out = (0x0, 1 << 23)    # [1, 4, 9]
# diff_out = (1 << (24 - 24), 0x0)    # [2, 6, 12]
# diff_out = (1 << (25 - 24), 0x0)    # [2, 6, 12]
# diff_out = (1 << (26 - 24), 0x0)    # [1, 5, 11]
# diff_out = (1 << (27 - 24), 0x0)    # [2, 6, 12]
# diff_out = (1 << (28 - 24), 0x0)    # [2, 6, 12]
# diff_out = (1 << (29 - 24), 0x0)    # [2, 5, 11]
# diff_out = (1 << (30 - 24), 0x0)    # [2, 6, 12]
# diff_out = (1 << (31 - 24), 0x0)    # [2, 6, 11]
# diff_out = (1 << (32 - 24), 0x0)    # [2, 6, 11]
# diff_out = (1 << (33 - 24), 0x0)    # [2, 6, 12]
# diff_out = (1 << (34 - 24), 0x0)    # [2, 6, 11]
# diff_out = (1 << (35 - 24), 0x0)    # [2, 6, 12]
# diff_out = (1 << (36 - 24), 0x0)    # [2, 6, 12]
# diff_out = (1 << (37 - 24), 0x0)    # [2, 6, 11]
# diff_out = (1 << (38 - 24), 0x0)    # [2, 6, 12]
# diff_out = (1 << (39 - 24), 0x0)    # [2, 5, 11]
# diff_out = (1 << (40 - 24), 0x0)    # [2, 6, 11]
# diff_out = (1 << (41 - 24), 0x0)    # [2, 6, 12]
# diff_out = (1 << (42 - 24), 0x0)    # [2, 5, 11]
# diff_out = (1 << (43 - 24), 0x0)    # [2, 6, 12]
# diff_out = (1 << (44 - 24), 0x0)    # [2, 6, 12]
# diff_out = (1 << (45 - 24), 0x0)    # [2, 5, 10]
# diff_out = (1 << (46 - 24), 0x0)    # [2, 6, 12]
# diff_out = (1 << (47 - 24), 0x0)    # [1, 5, 11]


# for Speck64
# diff_out = (0x0, 1 << 0)    # [1, 4, 9, 17]
# diff_out = (0x0, 1 << 1)    # [1, 4, 9, 18]
# diff_out = (0x0, 1 << 2)    # [0, 3, 8, 17]
# diff_out = (0x0, 1 << 3)    # [1, 4, 9, 17]
# diff_out = (0x0, 1 << 4)    # [1, 4, 9, 18]
# diff_out = (0x0, 1 << 5)    # [1, 3, 8, 17]
# diff_out = (0x0, 1 << 6)    # [1, 4, 9, 18]
# diff_out = (0x0, 1 << 7)    # [1, 4, 9, 18]
# diff_out = (0x0, 1 << 8)    # [1, 4, 8, 17]
# diff_out = (0x0, 1 << 9)    # [1, 4, 9, 18]
# diff_out = (0x0, 1 << 10)    # [1, 4, 9, 17]
# diff_out = (0x0, 1 << 11)    # [1, 4, 9, 17]
# diff_out = (0x0, 1 << 12)    # [1, 4, 9, 18]
# diff_out = (0x0, 1 << 13)    # [1, 4, 9, 17]
# diff_out = (0x0, 1 << 14)    # [1, 4, 9, 18]
# diff_out = (0x0, 1 << 15)    # [1, 4, 9, 18]
# diff_out = (0x0, 1 << 16)    # [1, 4, 9, 17]
# diff_out = (0x0, 1 << 17)    # [1, 4, 9, 18]
# diff_out = (0x0, 1 << 18)    # [1, 4, 8, 17]
# diff_out = (0x0, 1 << 19)    # [1, 4, 9, 17]
# diff_out = (0x0, 1 << 20)    # [1, 4, 9, 18]
# diff_out = (0x0, 1 << 21)    # [1, 4, 8, 16]
# diff_out = (0x0, 1 << 22)    # [1, 4, 9, 18]
# diff_out = (0x0, 1 << 23)    # [1, 4, 9, 18]
# diff_out = (0x0, 1 << 24)    # [1, 4, 8, 17]
# diff_out = (0x0, 1 << 25)    # [1, 4, 9, 18]
# diff_out = (0x0, 1 << 26)    # [1, 3, 8, 17]
# diff_out = (0x0, 1 << 27)    # [1, 4, 9, 17]
# diff_out = (0x0, 1 << 28)    # [1, 4, 9, 18]
# diff_out = (0x0, 1 << 29)    # [1, 3, 7, 16]
# diff_out = (0x0, 1 << 30)    # [1, 4, 9, 18]
# diff_out = (0x0, 1 << 31)    # [1, 4, 9, 18]
# diff_out = (1 << (32 - 32), 0x0)    # [2, 6, 12, 21]
# diff_out = (1 << (33 - 32), 0x0)    # [2, 6, 12, 22]
# diff_out = (1 << (34 - 32), 0x0)    # [1, 5, 11, 21]
# diff_out = (1 << (35 - 32), 0x0)    # [2, 6, 12, 21]
# diff_out = (1 << (36 - 32), 0x0)    # [2, 6, 12, 22]
# diff_out = (1 << (37 - 32), 0x0)    # [2, 5, 11, 21]
# diff_out = (1 << (38 - 32), 0x0)    # [2, 6, 12, 22]
# diff_out = (1 << (39 - 32), 0x0)    # [2, 6, 12, 21]
# diff_out = (1 << (40 - 32), 0x0)    # [2, 6, 11, 21]
# diff_out = (1 << (41 - 32), 0x0)    # [2, 6, 12, 21]
# diff_out = (1 << (42 - 32), 0x0)    # [2, 6, 12, 21]
# diff_out = (1 << (43 - 32), 0x0)    # [2, 6, 12, 21]
# diff_out = (1 << (44 - 32), 0x0)    # [2, 6, 12, 22]
# diff_out = (1 << (45 - 32), 0x0)    # [2, 6, 12, 21]
# diff_out = (1 << (46 - 32), 0x0)    # [2, 6, 12, 22]
# diff_out = (1 << (47 - 32), 0x0)    # [2, 6, 11, 21]
# diff_out = (1 << (48 - 32), 0x0)    # [2, 6, 12, 21]
# diff_out = (1 << (49 - 32), 0x0)    # [2, 6, 12, 22]
# diff_out = (1 << (50 - 32), 0x0)    # [2, 6, 11, 21]
# diff_out = (1 << (51 - 32), 0x0)    # [2, 6, 12, 21]
# diff_out = (1 << (52 - 32), 0x0)    # [2, 6, 12, 22]
# diff_out = (1 << (53 - 32), 0x0)    # [2, 6, 11, 20]
# diff_out = (1 << (54 - 32), 0x0)    # [2, 6, 12, 22]
# diff_out = (1 << (55 - 32), 0x0)    # [2, 5, 11, 21]
# diff_out = (1 << (56 - 32), 0x0)    # [2, 6, 11, 21]
# diff_out = (1 << (57 - 32), 0x0)    # [2, 6, 12, 22]
# diff_out = (1 << (58 - 32), 0x0)    # [2, 5, 11, 21]
# diff_out = (1 << (59 - 32), 0x0)    # [2, 6, 12, 21]
# diff_out = (1 << (60 - 32), 0x0)    # [2, 6, 12, 22]
# diff_out = (1 << (61 - 32), 0x0)    # [2, 5, 10, 20]
# diff_out = (1 << (62 - 32), 0x0)    # [2, 6, 12, 22]
# diff_out = (1 << (63 - 32), 0x0)    # [1, 5, 11, 21]


# for Speck96
# diff_out = (0x0, 1 << 0)    # [1, 4, 9, 17]
# diff_out = (0x0, 1 << 1)    # [1, 4, 9, 18]
# diff_out = (0x0, 1 << 2)    # [0, 3, 8, 17]
# diff_out = (0x0, 1 << 3)    # [1, 4, 9, 17]
# diff_out = (0x0, 1 << 4)    # [1, 4, 9, 18]
# diff_out = (0x0, 1 << 5)    # [1, 3, 8, 17]
# diff_out = (0x0, 1 << 6)    # [1, 4, 9, 18]
# diff_out = (0x0, 1 << 7)    # [1, 4, 9, 18]
# diff_out = (0x0, 1 << 8)    # [1, 4, 8, 17]
# diff_out = (0x0, 1 << 9)    # [1, 4, 9, 18]
# diff_out = (0x0, 1 << 10)    # [1, 4, 9, 18]
# diff_out = (0x0, 1 << 11)    # [1, 4, 9, 17]
# diff_out = (0x0, 1 << 12)    # [1, 4, 9, 18]
# diff_out = (0x0, 1 << 13)    # [1, 4, 9, 18]
# diff_out = (0x0, 1 << 14)    # [1, 4, 9, 18]
# diff_out = (0x0, 1 << 15)    # [1, 4, 9, 18]
# diff_out = (0x0, 1 << 16)    # [1, 4, 9, 18]
# diff_out = (0x0, 1 << 17)    # [1, 4, 9, 18]
# diff_out = (0x0, 1 << 18)    # [1, 4, 9, 18]
# diff_out = (0x0, 1 << 19)    # [1, 4, 9, 18]
# diff_out = (0x0, 1 << 20)    # [1, 4, 9, 18]
# diff_out = (0x0, 1 << 21)    # [1, 4, 9, 18]
# diff_out = (0x0, 1 << 22)    # [1, 4, 9, 18]
# diff_out = (0x0, 1 << 23)    # [1, 4, 9, 18]
# diff_out = (0x0, 1 << 24)    # [1, 4, 9, 18]
# diff_out = (0x0, 1 << 25)    # [1, 4, 9, 18]
# diff_out = (0x0, 1 << 26)    # [1, 4, 9, 17]
# diff_out = (0x0, 1 << 27)    # [1, 4, 9, 18]
# diff_out = (0x0, 1 << 28)    # [1, 4, 9, 18]
# diff_out = (0x0, 1 << 29)    # [1, 4, 9, 17]
# diff_out = (0x0, 1 << 30)    # [1, 4, 9, 18]
# diff_out = (0x0, 1 << 31)    # [1, 4, 9, 18]
# diff_out = (0x0, 1 << 32)    # [1, 4, 9, 17]
# diff_out = (0x0, 1 << 33)    # [1, 4, 9, 18]
# diff_out = (0x0, 1 << 34)    # [1, 4, 8, 17]
# diff_out = (0x0, 1 << 35)    # [1, 4, 9, 17]
# diff_out = (0x0, 1 << 36)    # [1, 4, 9, 18]
# diff_out = (0x0, 1 << 37)    # [1, 4, 8, 16]
# diff_out = (0x0, 1 << 38)    # [1, 4, 9, 18]
# diff_out = (0x0, 1 << 39)    # [1, 4, 9, 18]
# diff_out = (0x0, 1 << 40)    # [1, 4, 8, 17]
# diff_out = (0x0, 1 << 41)    # [1, 4, 9, 18]
# diff_out = (0x0, 1 << 42)    # [1, 3, 8, 17]
# diff_out = (0x0, 1 << 43)    # [1, 4, 9, 17]
# diff_out = (0x0, 1 << 44)    # [1, 4, 9, 18]
# diff_out = (0x0, 1 << 45)    # [1, 3, 7, 16]
# diff_out = (0x0, 1 << 46)    # [1, 4, 9, 18]
# diff_out = (0x0, 1 << 47)    # [1, 4, 9, 18]
# diff_out = (1 << (48 - 48), 0x0)    # [2, 6, 12, 21]
# diff_out = (1 << (49 - 48), 0x0)    # [2, 6, 12, 22]
# diff_out = (1 << (50 - 48), 0x0)    # [1, 5, 11, 21]
# diff_out = (1 << (51 - 48), 0x0)    # [2, 6, 12, 21]
# diff_out = (1 << (52 - 48), 0x0)    # [2, 6, 12, 22]
# diff_out = (1 << (53 - 48), 0x0)    # [2, 5, 11, 21]
# diff_out = (1 << (54 - 48), 0x0)    # [2, 6, 12, 22]
# diff_out = (1 << (55 - 48), 0x0)    # [2, 6, 12, 22]
# diff_out = (1 << (56 - 48), 0x0)    # [2, 6, 11, 21]
# diff_out = (1 << (57 - 48), 0x0)    # [2, 6, 12, 22]
# diff_out = (1 << (58 - 48), 0x0)    # [2, 6, 12, 22]
# diff_out = (1 << (59 - 48), 0x0)    # [2, 6, 12, 21]
# diff_out = (1 << (60 - 48), 0x0)    # [2, 6, 12, 22]
# diff_out = (1 << (61 - 48), 0x0)    # [2, 6, 12, 22]
# diff_out = (1 << (62 - 48), 0x0)    # [2, 6, 12, 22]
# diff_out = (1 << (63 - 48), 0x0)    # [2, 6, 12, 22]
# diff_out = (1 << (64 - 48), 0x0)    # [2, 6, 12, 22]
# diff_out = (1 << (65 - 48), 0x0)    # [2, 6, 12, 22]
# diff_out = (1 << (66 - 48), 0x0)    # [2, 6, 12, 22]
# diff_out = (1 << (67 - 48), 0x0)    # [2, 6, 12, 22]
# diff_out = (1 << (68 - 48), 0x0)    # [2, 6, 12, 22]
# diff_out = (1 << (69 - 48), 0x0)    # [2, 6, 12, 22]
# diff_out = (1 << (70 - 48), 0x0)    # [2, 6, 12, 22]
# diff_out = (1 << (71 - 48), 0x0)    # [2, 6, 12, 21]
# diff_out = (1 << (72 - 48), 0x0)    # [2, 6, 12, 22]
# diff_out = (1 << (73 - 48), 0x0)    # [2, 6, 12, 22]
# diff_out = (1 << (74 - 48), 0x0)    # [2, 6, 12, 21]
# diff_out = (1 << (75 - 48), 0x0)    # [2, 6, 12, 22]
# diff_out = (1 << (76 - 48), 0x0)    # [2, 6, 12, 22]
# diff_out = (1 << (77 - 48), 0x0)    # [2, 6, 12, 21]
# diff_out = (1 << (78 - 48), 0x0)    # [2, 6, 12, 22]
# diff_out = (1 << (79 - 48), 0x0)    # [2, 6, 11, 21]
# diff_out = (1 << (80 - 48), 0x0)    # [2, 6, 12, 21]
# diff_out = (1 << (81 - 48), 0x0)    # [2, 6, 12, 22]
# diff_out = (1 << (82 - 48), 0x0)    # [2, 6, 11, 21]
# diff_out = (1 << (83 - 48), 0x0)    # [2, 6, 12, 21]
# diff_out = (1 << (84 - 48), 0x0)    # [2, 6, 12, 22]
# diff_out = (1 << (85 - 48), 0x0)    # [2, 6, 11, 20]
# diff_out = (1 << (86 - 48), 0x0)    # [2, 6, 12, 22]
# diff_out = (1 << (87 - 48), 0x0)    # [2, 5, 11, 21]
# diff_out = (1 << (88 - 48), 0x0)    # [2, 6, 11, 21]
# diff_out = (1 << (89 - 48), 0x0)    # [2, 6, 12, 22]
# diff_out = (1 << (90 - 48), 0x0)    # [2, 5, 11, 21]
# diff_out = (1 << (91 - 48), 0x0)    # [2, 6, 12, 21]
# diff_out = (1 << (92 - 48), 0x0)    # [2, 6, 12, 22]
# diff_out = (1 << (93 - 48), 0x0)    # [2, 5, 10, 20]
# diff_out = (1 << (94 - 48), 0x0)    # [2, 6, 12, 22]
# diff_out = (1 << (95 - 48), 0x0)    # [1, 5, 11, 21]


# for Speck128
# diff_out = (0x0, 1 << 0)    # [1, 4, 9, 17, 28, 41]
# diff_out = (0x0, 1 << 1)    # [1, 4, 9, 18, 29, 42]
# diff_out = (0x0, 1 << 2)    # [0, 3, 8, 17, 28, 41]
# diff_out = (0x0, 1 << 3)    # [1, 4, 9, 17, 27, 40]
# diff_out = (0x0, 1 << 4)    # [1, 4, 9, 18, 29, 42]
# diff_out = (0x0, 1 << 5)    # [1, 3, 8, 17, 28, 41]
# diff_out = (0x0, 1 << 6)    # [1, 4, 9, 18, 29, 41]
# diff_out = (0x0, 1 << 7)    # [1, 4, 9, 18, 29, 42]
# diff_out = (0x0, 1 << 8)    # [1, 4, 8, 17, 28, 41]
# diff_out = (0x0, 1 << 9)    # [1, 4, 9, 18, 29, 41]
# diff_out = (0x0, 1 << 10)    # [1, 4, 9, 18, 29, 42]
# diff_out = (0x0, 1 << 11)    # [1, 4, 9, 17, 28, 41]
# diff_out = (0x0, 1 << 12)    # [1, 4, 9, 18, 29, 42]
# diff_out = (0x0, 1 << 13)    # [1, 4, 9, 18, 29, 42]
# diff_out = (0x0, 1 << 14)    # [1, 4, 9, 18, 28, 41]
# diff_out = (0x0, 1 << 15)    # [1, 4, 9, 18, 29, 42]
# diff_out = (0x0, 1 << 16)    # [1, 4, 9, 18, 29, 42]
# diff_out = (0x0, 1 << 17)    # [1, 4, 9, 18, 29, 41]
# diff_out = (0x0, 1 << 18)    # [1, 4, 9, 18, 29, 42]
# diff_out = (0x0, 1 << 19)    # [1, 4, 9, 18, 29, 42]
# diff_out = (0x0, 1 << 20)    # [1, 4, 9, 18, 29, 42]
# diff_out = (0x0, 1 << 21)    # [1, 4, 9, 18, 29, 42]
# diff_out = (0x0, 1 << 21)    # [1, 4, 9, 18, 29, 42]
# diff_out = (0x0, 1 << 22)    # [1, 4, 9, 18, 29, 42]
# diff_out = (0x0, 1 << 23)    # [1, 4, 9, 18, 29, 42]
# diff_out = (0x0, 1 << 24)    # [1, 4, 9, 18, 29, 42]
# diff_out = (0x0, 1 << 25)    # [1, 4, 9, 18, 29, 42]
# diff_out = (0x0, 1 << 26)    # [1, 4, 9, 18, 29, 41]
# diff_out = (0x0, 1 << 27)    # [1, 4, 9, 18, 29, 42]
# diff_out = (0x0, 1 << 28)    # [1, 4, 9, 18, 29, 42]
# diff_out = (0x0, 1 << 29)    # [1, 4, 9, 18, 29, 41]
# diff_out = (0x0, 1 << 30)    # [1, 4, 9, 18, 29, 42]
# diff_out = (0x0, 1 << 31)    # [1, 4, 9, 18, 29, 42]
# diff_out = (0x0, 1 << 32)    # [1, 4, 9, 18, 29, 41]
# diff_out = (0x0, 1 << 33)    # [1, 4, 9, 18, 29, 42]
# diff_out = (0x0, 1 << 34)    # [1, 4, 9, 18, 28, 41]
# diff_out = (0x0, 1 << 35)    # [1, 4, 9, 18, 29, 41]
# diff_out = (0x0, 1 << 36)    # [1, 4, 9, 18, 29, 42]
# diff_out = (0x0, 1 << 37)    # [1, 4, 9, 18, 28, 40]
# diff_out = (0x0, 1 << 38)    # [1, 4, 9, 18, 29, 41]
# diff_out = (0x0, 1 << 39)    # [1, 4, 9, 18, 29, 42]
# diff_out = (0x0, 1 << 40)    # [1, 4, 9, 18, 28, 40]
# diff_out = (0x0, 1 << 41)    # [1, 4, 9, 18, 29, 41]
# diff_out = (0x0, 1 << 42)    # [1, 4, 9, 17, 28, 41]
# diff_out = (0x0, 1 << 43)    # [1, 4, 9, 18, 28, 40]
# diff_out = (0x0, 1 << 44)    # [1, 4, 9, 18, 29, 42]
# diff_out = (0x0, 1 << 45)    # [1, 4, 9, 17, 27, 40]
# diff_out = (0x0, 1 << 46)    # [1, 4, 9, 18, 28, 41]
# diff_out = (0x0, 1 << 47)    # [1, 4, 9, 18, 29, 41]
# diff_out = (0x0, 1 << 48)    # [1, 4, 9, 17, 28, 40]
# diff_out = (0x0, 1 << 49)    # [1, 4, 9, 18, 29, 41]
# diff_out = (0x0, 1 << 50)    # [1, 4, 8, 17, 28, 41]
# diff_out = (0x0, 1 << 51)    # [1, 4, 9, 17, 27, 39]
# diff_out = (0x0, 1 << 52)    # [1, 4, 9, 18, 29, 41]
# diff_out = (0x0, 1 << 53)    # [1, 4, 8, 16, 27, 40]
# diff_out = (0x0, 1 << 54)    # [1, 4, 9, 18, 29, 42]
# diff_out = (0x0, 1 << 55)    # [1, 4, 9, 18, 29, 41]
# diff_out = (0x0, 1 << 56)    # [1, 4, 8, 17, 27, 39]
# diff_out = (0x0, 1 << 57)    # [1, 4, 9, 18, 29, 42]
# diff_out = (0x0, 1 << 58)    # [1, 3, 8, 17, 28, 41]
# diff_out = (0x0, 1 << 59)    # [1, 4, 9, 17, 27, 38]
# diff_out = (0x0, 1 << 60)    # [1, 4, 9, 18, 29, 42]
# diff_out = (0x0, 1 << 61)    # [1, 3, 7, 16, 27, 40]
# diff_out = (0x0, 1 << 62)    # [1, 4, 9, 18, 29, 42]
# diff_out = (0x0, 1 << 63)    # [1, 4, 9, 18, 29, 42]
# diff_out = (1 << (64 - 64), 0x0)    # [2, 6, 12, 21, 31, 42]
# diff_out = (1 << (65 - 64), 0x0)    # [2, 6, 12, 22, 32, 43]
# diff_out = (1 << (66 - 64), 0x0)    # [1, 5, 11, 21, 31, 42]
# diff_out = (1 << (67 - 64), 0x0)    # [2, 6, 12, 21, 30, 41]
# diff_out = (1 << (68 - 64), 0x0)    # [2, 6, 12, 22, 32, 43]
# diff_out = (1 << (69 - 64), 0x0)    # [2, 5, 11, 21, 31, 42]
# diff_out = (1 << (70 - 64), 0x0)    # [2, 6, 12, 22, 32, 42]
# diff_out = (1 << (71 - 64), 0x0)    # [2, 6, 12, 22, 32, 43]
# diff_out = (1 << (72 - 64), 0x0)    # [2, 6, 11, 21, 31, 42]
# diff_out = (1 << (73 - 64), 0x0)    # [2, 6, 12, 22, 32, 42]
# diff_out = (1 << (74 - 64), 0x0)    # [2, 6, 12, 22, 32, 43]
# diff_out = (1 << (75 - 64), 0x0)    # [2, 6, 12, 21, 31, 42]
# diff_out = (1 << (76 - 64), 0x0)    # [2, 6, 12, 22, 32, 43]
# diff_out = (1 << (77 - 64), 0x0)    # [2, 6, 12, 22, 32, 43]
# diff_out = (1 << (78 - 64), 0x0)    # [2, 6, 12, 22, 31, 42]
# diff_out = (1 << (79 - 64), 0x0)    # [2, 6, 12, 22, 32, 43]
# diff_out = (1 << (80 - 64), 0x0)    # [2, 6, 12, 22, 32, 43]
# diff_out = (1 << (81 - 64), 0x0)    # [2, 6, 12, 22, 32, 42]
# diff_out = (1 << (82 - 64), 0x0)    # [2, 6, 12, 22, 32, 43]
# diff_out = (1 << (83 - 64), 0x0)    # [2, 6, 12, 22, 32, 43]
# diff_out = (1 << (84 - 64), 0x0)    # [2, 6, 12, 22, 32, 43]
# diff_out = (1 << (85 - 64), 0x0)    # [2, 6, 12, 22, 32, 43]
# diff_out = (1 << (86 - 64), 0x0)    # [2, 6, 12, 22, 32, 43]
# diff_out = (1 << (87 - 64), 0x0)    # [2, 6, 12, 22, 32, 43]
# diff_out = (1 << (88 - 64), 0x0)    # [2, 6, 12, 22, 32, 43]
# diff_out = (1 << (89 - 64), 0x0)    # [2, 6, 12, 22, 32, 43]
# diff_out = (1 << (90 - 64), 0x0)    # [2, 6, 12, 22, 32, 43]
# diff_out = (1 << (91 - 64), 0x0)    # [2, 6, 12, 22, 32, 43]
# diff_out = (1 << (92 - 64), 0x0)    # [2, 6, 12, 22, 32, 43]
# diff_out = (1 << (93 - 64), 0x0)    # [2, 6, 12, 22, 32, 43]
# diff_out = (1 << (94 - 64), 0x0)    # [2, 6, 12, 22, 32, 43]
# diff_out = (1 << (95 - 64), 0x0)    # [2, 6, 12, 22, 31, 43]
# diff_out = (1 << (96 - 64), 0x0)    # [2, 6, 12, 22, 32, 43]
# diff_out = (1 << (97 - 64), 0x0)    # [2, 6, 12, 22, 32, 43]
# diff_out = (1 << (98 - 64), 0x0)    # [2, 6, 12, 22, 31, 43]
# diff_out = (1 << (99 - 64), 0x0)    # [2, 6, 12, 22, 32, 43]
# diff_out = (1 << (100 - 64), 0x0)    # [2, 6, 12, 22, 32, 43]
# diff_out = (1 << (101 - 64), 0x0)    # [2, 6, 12, 22, 32, 43]
# diff_out = (1 << (102 - 64), 0x0)    # [2, 6, 12, 22, 32, 43]
# diff_out = (1 << (103 - 64), 0x0)    # [2, 6, 12, 21, 31, 42]
# diff_out = (1 << (104 - 64), 0x0)    # [2, 6, 12, 22, 32, 42]
# diff_out = (1 << (105 - 64), 0x0)    # [2, 6, 12, 22, 32, 44]
# diff_out = (1 << (106 - 64), 0x0)    # [2, 6, 12, 21, 31, 44]
# diff_out = (1 << (107 - 64), 0x0)    # [2, 6, 12, 22, 31, 41]
# diff_out = (1 << (108 - 64), 0x0)    # [2, 6, 12, 22, 31, 43]
# diff_out = (1 << (109 - 64), 0x0)    # [2, 6, 12, 21, 30, 43]
# diff_out = (1 << (110 - 64), 0x0)    # [2, 6, 12, 22, 31, 43]
# diff_out = (1 << (111 - 64), 0x0)    # [2, 6, 11, 21, 31, 42]
# diff_out = (1 << (112 - 64), 0x0)    # [2, 6, 12, 21, 31, 40]
# diff_out = (1 << (113 - 64), 0x0)    # [2, 6, 12, 22, 32, 44]
# diff_out = (1 << (114 - 64), 0x0)    # [2, 6, 11, 21, 31, 44]
# diff_out = (1 << (115 - 64), 0x0)    # [2, 6, 12, 21, 30, 40]
# diff_out = (1 << (116 - 64), 0x0)    # [2, 6, 12, 22, 32, 42]
# diff_out = (1 << (117 - 64), 0x0)    # [2, 6, 11, 20, 30, 44]
# diff_out = (1 << (118 - 64), 0x0)    # [2, 6, 12, 22, 32, 43]
# diff_out = (1 << (119 - 64), 0x0)    # [2, 5, 11, 21, 31, 42]
# diff_out = (1 << (120 - 64), 0x0)    # [2, 6, 11, 21, 30, 41]
# diff_out = (1 << (121 - 64), 0x0)    # [2, 6, 12, 22, 32, 43]
# diff_out = (1 << (122 - 64), 0x0)    # [2, 5, 11, 21, 31, 42]
# diff_out = (1 << (123 - 64), 0x0)    # [2, 6, 12, 21, 30, 40]
# diff_out = (1 << (124 - 64), 0x0)    # [2, 6, 12, 22, 32, 43]
# diff_out = (1 << (125 - 64), 0x0)    # [2, 5, 10, 20, 30, 41]
# diff_out = (1 << (126 - 64), 0x0)    # [2, 6, 12, 22, 32, 43]
# diff_out = (1 << (127 - 64), 0x0)    # [1, 5, 11, 21, 31, 42]




# speck32,  22, 32, 16, 7, 2
# speck48,  22, 48, 24, 8, 3
FullRound = 22

BlockSize = 64
HalfBlockSize = 32

alpha = 8
beta = 3

SearchRoundStart = 1
SearchRoundEnd = 5
InitialLowerBound = 0

GroupConstraintChoice = 1

# Parameters for choice 1
GroupNumForChoice1 = 1

DifferentialProbabilityBound = list([])
for i in range(FullRound):
    DifferentialProbabilityBound += [0]


def CountClausesInRoundFunction(Round, Prob, clausenum):
    count = clausenum
    # Nonzero input
    count += 1
    for round in range(Round):
        # branch in right part
        for i in range(HalfBlockSize):
            count += 4
        # modular operation
        for i in range(HalfBlockSize - 1):
            count += 8
        count += 4
        # modular probability weight
        for i in range(HalfBlockSize - 1):
            count += 5
        # branch in left part
        for i in range(HalfBlockSize):
            count += 4
        # XOR in right part
        for i in range(HalfBlockSize):
            count += 4
    return count


def CountClausesInSequentialEncoding(main_var_num, cardinalitycons, clause_num):
    count = clause_num
    n = main_var_num
    k = cardinalitycons
    if k > 0:
        count += 1
        for j in range(1, k):
            count += 1
        for i in range(1, n - 1):
            count += 3
        for j in range(1, k):
            for i in range(1, n - 1):
                count += 2
        count += 1
    if (k == 0):
        for i in range(n):
            count += 1
    return count


def CountClausesForMatsuiStrategy(n, k, left, right, m, clausenum):
    count = clausenum
    if m > 0:
        if left == 0 and right < n - 1:
            for i in range(1, right + 1):
                count += 1
        if left > 0 and right == n - 1:
            for i in range(0, k - m):
                count += 1
            for i in range(0, k - m + 1):
                count += 1
        if left > 0 and right < n - 1:
            for i in range(0, k - m):
                count += 1
    if m == 0:
        for i in range(left, right + 1):
            count += 1
    return count


def GenSequentialEncoding(x, u, main_var_num, cardinalitycons, fout):
    n = main_var_num
    k = cardinalitycons
    if k > 0:
        clauseseq = "-" + str(x[0] + 1) + " " + str(u[0][0] + 1) + " 0" + "\n"
        fout.write(clauseseq)

        for j in range(1, k):
            clauseseq = "-" + str(u[0][j] + 1) + " 0" + "\n"
            fout.write(clauseseq)

        for i in range(1, n - 1):
            clauseseq = "-" + str(x[i] + 1) + " " + str(u[i][0] + 1) + " 0" + "\n"
            fout.write(clauseseq)

            clauseseq = "-" + str(u[i - 1][0] + 1) + " " + str(u[i][0] + 1) + " 0" + "\n"
            fout.write(clauseseq)

            clauseseq = "-" + str(x[i] + 1) + " " + "-" + str(u[i - 1][k - 1] + 1) + " 0" + "\n"
            fout.write(clauseseq)

        for j in range(1, k):
            for i in range(1, n - 1):
                clauseseq = "-" + str(x[i] + 1) + " " + "-" + str(u[i - 1][j - 1] + 1) + " " + \
                            str(u[i][j] + 1) + " 0" + "\n"
                fout.write(clauseseq)

                clauseseq = "-" + str(u[i - 1][j] + 1) + " " + str(u[i][j] + 1) + " 0" + "\n"
                fout.write(clauseseq)

        clauseseq = "-" + str(x[n - 1] + 1) + " " + "-" + str(u[n - 2][k - 1] + 1) + " 0" + "\n"
        fout.write(clauseseq)

    if k == 0:
        for i in range(n):
            clauseseq = "-" + str(x[i] + 1) + " 0" + "\n"
            fout.write(clauseseq)


def GenMatsuiConstraint(x, u, n, k, left, right, m, fout):
    if m > 0:
        if left == 0 and right < n - 1:
            for i in range(1, right + 1):
                clauseseq = "-" + str(x[i] + 1) + " " + "-" + str(u[i - 1][m - 1] + 1) + " 0" + "\n"
                fout.write(clauseseq)

        if left > 0 and right == n - 1:
            for i in range(0, k - m):
                clauseseq = str(u[left - 1][i] + 1) + " " + "-" + str(u[right - 1][i + m] + 1) + " 0" + "\n"
                fout.write(clauseseq)

            for i in range(0, k - m + 1):
                clauseseq = str(u[left - 1][i] + 1) + " " + "-" + str(x[right] + 1) + " " + "-" + \
                            str(u[right - 1][i + m - 1] + 1) + " 0" + "\n"
                fout.write(clauseseq)

        if left > 0 and right < n - 1:
            for i in range(0, k - m):
                clauseseq = str(u[left - 1][i] + 1) + " " + "-" + str(u[right][i + m] + 1) + " 0" + "\n"
                fout.write(clauseseq)

    if m == 0:
        for i in range(left, right + 1):
            clauseseq = "-" + str(x[i] + 1) + " 0" + "\n"
            fout.write(clauseseq)


def Decision(Round, Probability, MatsuiRoundIndex, MatsuiCount, flag):
    TotalProbability = (HalfBlockSize - 1) * Round
    count_var_num = 0
    time_start = time.time()
    # Declare variable
    xin = []
    a = []
    b = []
    c = []
    d = []
    w = []
    xout = []
    for i in range(Round):
        xin.append([])
        a.append([])
        b.append([])
        c.append([])
        d.append([])
        w.append([])
        xout.append([])
        for j in range(BlockSize):
            xin[i].append(0)
        for j in range(HalfBlockSize):
            a[i].append(0)
            b[i].append(0)
            c[i].append(0)
            d[i].append(0)
        for j in range(HalfBlockSize - 1):
            w[i].append(0)
        for j in range(BlockSize):
            xout[i].append(0)
    # Allocate variable
    for i in range(Round):
        for j in range(BlockSize):
            xin[i][j] = count_var_num
            count_var_num += 1
    for i in range(Round - 1):
        for j in range(BlockSize):
            xout[i][j] = xin[i + 1][j]
    for j in range(BlockSize):
        xout[Round - 1][j] = count_var_num
        count_var_num += 1

    for i in range(Round):
        for j in range(HalfBlockSize):
            a[i][j] = count_var_num
            count_var_num += 1
        for j in range(HalfBlockSize):
            b[i][j] = count_var_num
            count_var_num += 1
        for j in range(HalfBlockSize):
            c[i][j] = count_var_num
            count_var_num += 1
        for j in range(HalfBlockSize):
            d[i][j] = count_var_num
            count_var_num += 1
        for j in range(HalfBlockSize - 1):
            w[i][j] = count_var_num
            count_var_num += 1
    # var for sequential coding
    auxiliary_var_u = []
    for i in range(TotalProbability - 1):
        auxiliary_var_u.append([])
        for j in range(Probability):
            auxiliary_var_u[i].append(count_var_num)
            count_var_num += 1
    # Count the number of clauses in the round function
    count_clause_num = 0
    count_clause_num = CountClausesInRoundFunction(Round, Probability, count_clause_num)
    # Count the number of clauses in the original sequential encoding
    Main_Var_Num = (HalfBlockSize - 1) * Round
    CardinalityCons = Probability
    count_clause_num = CountClausesInSequentialEncoding(Main_Var_Num, CardinalityCons, count_clause_num)

    # when a fixed output is given, these conditions can't be used
    # Count the number of clauses for Matsui's strategy
    # for matsui_count in range(0, MatsuiCount):
    #     StartingRound = MatsuiRoundIndex[matsui_count][0]
    #     EndingRound = MatsuiRoundIndex[matsui_count][1]
    #     LeftNode = (HalfBlockSize - 1) * StartingRound
    #     RightNode = (HalfBlockSize - 1) * EndingRound - 1
    #     PartialCardinalityCons = Probability - DifferentialProbabilityBound[StartingRound] - \
    #                              DifferentialProbabilityBound[Round - EndingRound]
    #     count_clause_num = CountClausesForMatsuiStrategy(Main_Var_Num, CardinalityCons, LeftNode, RightNode,
    #                                                      PartialCardinalityCons, count_clause_num)

    # count the number of clauses for constrains of output diff
    count_clause_num += BlockSize   # Blocksize clauses for fixed output

    # Open file
    file = open("Problem-Round" + str(Round) + "-Probability" + str(Probability) + ".cnf", "w")
    file.write("p cnf " + str(count_var_num) + " " + str(count_clause_num) + "\n")

    # Add constraints to claim nonzero input difference
    clauseseq = ""
    for i in range(BlockSize):
        clauseseq += str(xin[0][i] + 1) + " "
    clauseseq += "0" + "\n"
    file.write(clauseseq)
    # Add constraints for the round function
    for round in range(Round):
        # add clauses for branch in right part
        for i in range(HalfBlockSize):
            clauseseq = str(xin[round][i + HalfBlockSize] + 1) + " " + "-" + str(a[round][i] + 1) + " " + "0" + "\n"
            file.write(clauseseq)
            clauseseq = "-" + str(xin[round][i + HalfBlockSize] + 1) + " " + str(a[round][i] + 1) + " " + "0" + "\n"
            file.write(clauseseq)
            clauseseq = str(xin[round][i + HalfBlockSize] + 1) + " " + "-" + str(b[round][i] + 1) + " " + "0" + "\n"
            file.write(clauseseq)
            clauseseq = "-" + str(xin[round][i + HalfBlockSize] + 1) + " " + str(b[round][i] + 1) + " " + "0" + "\n"
            file.write(clauseseq)
        # add clauses for modular in left part
        for i in range(HalfBlockSize - 1):
            index = (i + HalfBlockSize - alpha) % HalfBlockSize
            index_plus = (i + 1 + HalfBlockSize - alpha) % HalfBlockSize
            clauseseq = str(xin[round][index] + 1) + " " + str(a[round][i] + 1) + " " + \
                        "-" + str(c[round][i] + 1) + " " + str(xin[round][index_plus] + 1) + \
                        " " + str(a[round][i + 1] + 1) + " " + str(c[round][i + 1] + 1) + " " + "0" + "\n"
            file.write(clauseseq)
            clauseseq = str(xin[round][index] + 1) + " " + "-" + str(a[round][i] + 1) + \
                        " " + str(c[round][i] + 1) + " " + str(xin[round][index_plus] + 1) + \
                        " " + str(a[round][i + 1] + 1) + " " + str(c[round][i + 1] + 1) + " " + "0" + "\n"
            file.write(clauseseq)
            clauseseq = "-" + str(xin[round][index] + 1) + " " + str(a[round][i] + 1) + \
                        " " + str(c[round][i] + 1) + " " + str(xin[round][index_plus] + 1) + \
                        " " + str(a[round][i + 1] + 1) + " " + str(c[round][i + 1] + 1) + " " + "0" + "\n"
            file.write(clauseseq)
            clauseseq = "-" + str(xin[round][index] + 1) + " " + "-" + str(a[round][i] + 1) + \
                        " " + "-" + str(c[round][i] + 1) + " " + str(xin[round][index_plus] + 1) + \
                        " " + str(a[round][i + 1] + 1) + " " + str(c[round][i + 1] + 1) + " " + "0" + "\n"
            file.write(clauseseq)
            # another four clauses
            clauseseq = str(xin[round][index] + 1) + " " + str(a[round][i] + 1) + \
                        " " + str(c[round][i] + 1) + " " + "-" + str(xin[round][index_plus] + 1) + \
                        " " + "-" + str(a[round][i + 1] + 1) + " " + "-" + str(c[round][i + 1] + 1) + " " + "0" + "\n"
            file.write(clauseseq)
            clauseseq = str(xin[round][index] + 1) + " " + "-" + str(a[round][i] + 1) + \
                        " " + "-" + str(c[round][i] + 1) + " " + "-" + str(xin[round][index_plus] + 1) + \
                        " " + "-" + str(a[round][i + 1] + 1) + " " + "-" + str(c[round][i + 1] + 1) + " " + "0" + "\n"
            file.write(clauseseq)
            clauseseq = "-" + str(xin[round][index] + 1) + " " + str(a[round][i] + 1) + \
                        " " + "-" + str(c[round][i] + 1) + " " + "-" + str(xin[round][index_plus] + 1) + \
                        " " + "-" + str(a[round][i + 1] + 1) + " " + "-" + str(c[round][i + 1] + 1) + " " + "0" + "\n"
            file.write(clauseseq)
            clauseseq = "-" + str(xin[round][index] + 1) + " " + "-" + str(a[round][i] + 1) + \
                        " " + str(c[round][i] + 1) + " " + "-" + str(xin[round][index_plus] + 1) + \
                        " " + "-" + str(a[round][i + 1] + 1) + " " + "-" + str(c[round][i + 1] + 1) + " " + "0" + "\n"
            file.write(clauseseq)
        # add clauses for lsb (modular)
        index = (HalfBlockSize - 1 + HalfBlockSize - alpha) % HalfBlockSize
        clauseseq = str(xin[round][index] + 1) + " " + str(a[round][HalfBlockSize - 1] + 1) + \
                    " " + "-" + str(c[round][HalfBlockSize - 1] + 1) + " " + "0" + "\n"
        file.write(clauseseq)
        clauseseq = str(xin[round][index] + 1) + " " + "-" + str(a[round][HalfBlockSize - 1] + 1) + \
                    " " + str(c[round][HalfBlockSize - 1] + 1) + " " + "0" + "\n"
        file.write(clauseseq)
        clauseseq = "-" + str(xin[round][index] + 1) + " " + str(a[round][HalfBlockSize - 1] + 1) + \
                    " " + str(c[round][HalfBlockSize - 1] + 1) + " " + "0" + "\n"
        file.write(clauseseq)
        clauseseq = "-" + str(xin[round][index] + 1) + " " + "-" + str(a[round][HalfBlockSize - 1] + 1) + \
                    " " + "-" + str(c[round][HalfBlockSize - 1] + 1) + " " + "0" + "\n"
        file.write(clauseseq)

        # add clauses for prob weight (modular)
        for i in range(HalfBlockSize - 1):
            index_plus = (i + 1 + HalfBlockSize - alpha) % HalfBlockSize
            clauseseq = "-" + str(xin[round][index_plus] + 1) + " " + str(c[round][i + 1] + 1) + \
                        " " + str(w[round][i] + 1) + " " + "0" + "\n"
            file.write(clauseseq)

            clauseseq = str(a[round][i + 1] + 1) + " " + "-" + str(c[round][i + 1] + 1) + \
                        " " + str(w[round][i] + 1) + " " + "0" + "\n"
            file.write(clauseseq)

            clauseseq = str(xin[round][index_plus] + 1) + " " + "-" + str(a[round][i + 1] + 1) + \
                        " " + str(w[round][i] + 1) + " " + "0" + "\n"
            file.write(clauseseq)

            clauseseq = str(xin[round][index_plus] + 1) + " " + str(a[round][i + 1] + 1) + \
                        " " + str(c[round][i + 1] + 1) + " " + "-" + str(w[round][i] + 1) + " " + "0" + "\n"
            file.write(clauseseq)

            clauseseq = "-" + str(xin[round][index_plus] + 1) + " " + "-" + str(a[round][i + 1] + 1) + \
                        " " + "-" + str(c[round][i + 1] + 1) + " " + "-" + str(w[round][i] + 1) + " " + "0" + "\n"
            file.write(clauseseq)
        # add clauses for branch in left part
        for i in range(HalfBlockSize):
            clauseseq = str(c[round][i] + 1) + " " + "-" + str(xout[round][i] + 1) + " " + "0" + "\n"
            file.write(clauseseq)

            clauseseq = "-" + str(c[round][i] + 1) + " " + str(xout[round][i] + 1) + " " + "0" + "\n"
            file.write(clauseseq)

            clauseseq = str(c[round][i] + 1) + " " + "-" + str(d[round][i] + 1) + " " + "0" + "\n"
            file.write(clauseseq)

            clauseseq = "-" + str(c[round][i] + 1) + " " + str(d[round][i] + 1) + " " + "0" + "\n"
            file.write(clauseseq)
        # add clauses for XOR in right part
        for i in range(HalfBlockSize):
            index = (i + HalfBlockSize + beta) % HalfBlockSize
            clauseseq = str(b[round][index] + 1) + " " + str(d[round][i] + 1) + \
                        " " + "-" + str(xout[round][i + HalfBlockSize] + 1) + " " + "0" + "\n"
            file.write(clauseseq)
            clauseseq = str(b[round][index] + 1) + " " + "-" + str(d[round][i] + 1) + \
                        " " + str(xout[round][i + HalfBlockSize] + 1) + " " + "0" + "\n"
            file.write(clauseseq)
            clauseseq = "-" + str(b[round][index] + 1) + " " + str(d[round][i] + 1) + \
                        " " + str(xout[round][i + HalfBlockSize] + 1) + " " + "0" + "\n"
            file.write(clauseseq)
            clauseseq = "-" + str(b[round][index] + 1) + " " + "-" + str(d[round][i] + 1) + \
                        " " + "-" + str(xout[round][i + HalfBlockSize] + 1) + " " + "0" + "\n"
            file.write(clauseseq)

    # Add constraints for the original sequential encoding
    Main_Vars = list([])
    for r in range(Round):
        for i in range(HalfBlockSize - 1):
            Main_Vars += [w[Round - 1 - r][i]]
    GenSequentialEncoding(Main_Vars, auxiliary_var_u, Main_Var_Num, CardinalityCons, file)

    # when a fixed output is given, these conditions can't be used.
    # Add constraints for Matsui's strategy
    # for matsui_count in range(0, MatsuiCount):
    #     StartingRound = MatsuiRoundIndex[matsui_count][0]
    #     EndingRound = MatsuiRoundIndex[matsui_count][1]
    #     LeftNode = (HalfBlockSize - 1) * StartingRound
    #     RightNode = (HalfBlockSize - 1) * EndingRound - 1
    #     PartialCardinalityCons = Probability - DifferentialProbabilityBound[StartingRound] - \
    #                              DifferentialProbabilityBound[Round - EndingRound]
    #     GenMatsuiConstraint(Main_Vars, auxiliary_var_u, Main_Var_Num, CardinalityCons, LeftNode, RightNode,
    #                         PartialCardinalityCons, file)

    # add constraints for fixed output
    diff_l, diff_r = diff_out[0], diff_out[1]
    for i in range(HalfBlockSize):
        if (diff_l >> (HalfBlockSize - 1 - i)) & 1 == 0:
            clauseseq = "-" + str(xout[Round - 1][i] + 1) + " " + "0" + "\n"
            file.write(clauseseq)
        else:
            clauseseq = str(xout[Round - 1][i] + 1) + " " + "0" + "\n"
            file.write(clauseseq)
    for i in range(HalfBlockSize):
        if (diff_r >> (HalfBlockSize - 1 - i)) & 1 == 0:
            clauseseq = "-" + str(xout[Round - 1][i + HalfBlockSize] + 1) + " " + "0" + "\n"
            file.write(clauseseq)
        else:
            clauseseq = str(xout[Round - 1][i + HalfBlockSize] + 1) + " " + "0" + "\n"
            file.write(clauseseq)
    file.close()
    # Call solver cadical
    order = "/mnt/c/D_file/software/cadical/cadical-master/build/cadical " + "Problem-Round" + str(
        Round) + "-Probability" + str(Probability) + ".cnf > Round" + str(Round) + "-Probability" + str(
        Probability) + "-solution.out"
    os.system(order)
    # Extracting results
    order = "sed -n '/s SATISFIABLE/p' Round" + str(Round) + "-Probability" + str(
        Probability) + "-solution.out > SatSolution.out"
    os.system(order)
    order = "sed -n '/s UNSATISFIABLE/p' Round" + str(Round) + "-Probability" + str(
        Probability) + "-solution.out > UnsatSolution.out"
    os.system(order)
    satsol = open("SatSolution.out")
    unsatsol = open("UnsatSolution.out")
    satresult = satsol.readlines()
    unsatresult = unsatsol.readlines()
    satsol.close()
    unsatsol.close()
    if ((len(satresult) == 0) and (len(unsatresult) > 0)):
        flag = False
    if ((len(satresult) > 0) and (len(unsatresult) == 0)):
        flag = True
    order = "rm SatSolution.out"
    os.system(order)
    order = "rm UnsatSolution.out"
    os.system(order)
    # Removing cnf file
    order = "rm Problem-Round" + str(Round) + "-Probability" + str(Probability) + ".cnf"
    os.system(order)
    time_end = time.time()
    # Printing solutions
    if (flag == True):
        print("Round:" + str(Round) + "; Probability: " + str(Probability) + "; Sat; TotalCost: " + str(
            time_end - time_start))
    else:
        print("Round:" + str(Round) + "; Probability: " + str(Probability) + "; Unsat; TotalCost: " + str(
            time_end - time_start))
    return flag


# main function
CountProbability = InitialLowerBound
TotalTimeStart = time.time()
for totalround in range(SearchRoundStart, SearchRoundEnd):
    flag = False
    time_start = time.time()
    MatsuiRoundIndex = []
    MatsuiCount = 0
    # Generate Matsui condition under choice 1
    if (GroupConstraintChoice == 1):
        for group in range(0, GroupNumForChoice1):
            for round in range(1, totalround - group + 1):
                MatsuiRoundIndex.append([])
                MatsuiRoundIndex[MatsuiCount].append(group)
                MatsuiRoundIndex[MatsuiCount].append(group + round)
                MatsuiCount += 1
    # Printing Matsui conditions
    file = open("MatsuiCondition.out", "a")
    resultseq = "Round: " + str(totalround) + "; Partial Constraint Num: " + str(MatsuiCount) + "\n"
    file.write(resultseq)
    file.write(str(MatsuiRoundIndex) + "\n")
    file.close()
    while (flag == False):
        flag = Decision(totalround, CountProbability, MatsuiRoundIndex, MatsuiCount, flag)
        CountProbability += 1

        if flag == False:
            # Removing cnf file
            order = "rm Round" + str(totalround) + "-Probability" + \
                    str(CountProbability - 1) + "-solution.out"
            os.system(order)

    DifferentialProbabilityBound[totalround] = CountProbability - 1
    CountProbability = CountProbability - 1
    time_end = time.time()
    file = open("RunTimeSummarise.out", "a")
    resultseq = "Round: " + str(totalround) + "; Differential Probability: " + str(
        DifferentialProbabilityBound[totalround]) + "; Runtime: " + str(time_end - time_start) + "\n"
    file.write(resultseq)
    file.close()
print(str(DifferentialProbabilityBound))
TotalTimeEnd = time.time()
print("Total Runtime: " + str(TotalTimeEnd - TotalTimeStart))
file = open("RunTimeSummarise.out", "a")
resultseq = "Total Runtime: " + str(TotalTimeEnd - TotalTimeStart)
file.write(resultseq)
