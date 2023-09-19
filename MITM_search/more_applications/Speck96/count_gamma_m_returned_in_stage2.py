import os

# the results saved in
block_size = 96
nr = 5
# the upper bound of the absolute correlation weight of the linear hull
# $\gamma _m \xrightarrow {E_2} \gamma _{out}$
upper_bound = 8
root = './linear_hulls/cor_{}/'.format(upper_bound)

sum = 0
for i in range(block_size):
    dictionary_path = root + 'diff_{}/'.format(i) + '{}_round/'.format(nr)
    files = os.listdir(dictionary_path)
    print('the difference is [{}]'.format(i))
    print('the number of $\gamma _m$ returned in Stage 2 is ', len(files))
    sum += len(files)

print('the total number of returned \gamma_m is ', sum)