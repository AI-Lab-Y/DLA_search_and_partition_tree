'''
get the set of linear mask $\gamma _m$ returned in Stage 2
'''


import numpy as np
import os


trans = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f']


def read_File_Get_linear_mask(filePath=None, nr=None, Blocksize=None):
    n = (nr+1) * Blocksize
    diff = np.zeros(n, dtype=np.uint8)
    index = 0
    res = open(filePath, 'r')
    lines = res.readlines()
    for line in lines:
        line = line.strip('\n')
        x = line.split(" ")
        if x[0] == "v":
            num = len(x) - 1
            if index + num < n:
                for i in range(1, num+1):
                    val = int(x[i])
                    if val < 0:
                        diff[index] = 0
                    else:
                        diff[index] = 1
                    index += 1
            else:
                for i in range(1, n - index + 1):
                    val = int(x[i], base=10)
                    if val < 0:
                        diff[index] = 0
                    else:
                        diff[index] = 1
                    index += 1
        if index == n:
            break
    res.close()

    mask = []
    for j in range(Blocksize):
        st = Blocksize - 1 - j
        if diff[st] == 1:
            mask.append(j)
    return mask


def get_file_paths(root=None):
    fileNames = os.listdir(root)
    return fileNames


def get_searched_linear_masks(root=None, Round=4, Blocksize=128):
    fileNames = get_file_paths(root=root)
    print('the number of good linear masks is ', len(fileNames))
    for file in fileNames:
        print('cur file is : {}'.format(file))
        path = os.path.join(root, file)
        mask = read_File_Get_linear_mask(filePath=path, nr=Round, Blocksize=Blocksize)
        print('cur linear mask \gamma_m is {}'.format(mask))
        print('')


nr_Em = 6
diff = 39
# diff = 47
# diff = 53
nr = 4
root = './linear_hulls/diff_{}/{}_round/'.format(diff, nr)
Blocksize = 64
get_searched_linear_masks(root=root, Round=nr, Blocksize=Blocksize)