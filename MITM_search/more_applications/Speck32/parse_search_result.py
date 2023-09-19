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
                    # print('index is {}, val is {}'.format(index, val))
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
    hull = []

    fileNames = get_file_paths(root=root)
    for file in fileNames:
        path = root + file
        mask = read_File_Get_linear_mask(filePath=path, nr=Round, Blocksize=Blocksize)

        if mask not in hull:
            hull.append(mask)
            print('cur file is : {}'.format(file))
            print('cur linear mask is {}'.format(mask))
            print('')


diff = 28
nr = 3
bound = 4
root = './linear_hulls/cor_{}/diff_{}/{}_round/'.format(bound, diff, nr)
Blocksize = 32
get_searched_linear_masks(root=root, Round=nr, Blocksize=Blocksize)