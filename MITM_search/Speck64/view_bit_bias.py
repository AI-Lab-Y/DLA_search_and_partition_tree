import numpy as np

file = './6r_oneBitDiff_oneBitMask_cor_w.npy'
bit_bias = np.load(file, allow_pickle=True)

cor_weight_bound = 8
print('current absolute correlation weight threshold: ', cor_weight_bound)
block_size = 64

for i in range(block_size):
    tp = [j for j in range(block_size) if bit_bias[i][j] < cor_weight_bound]
    print('bit index: ', i)
    print('the number of strong unbalanced bit is ', len(tp))
    print('strong unbalanced bits are ', tp)