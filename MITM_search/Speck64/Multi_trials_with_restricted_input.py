'''
1、searching for linear hulls $\gamma _m ---> \gamma _{out}$
that satisfies two conditions:
(1) the absolute correlation is greater or equal than the UpperBound
(2) $\gamma _m [i] = 0 for i \notin B_S$ where $B_S$ is the strong unbalanced bit set

2、We add an extra constraint to avoid returned linear hulls having duplicate mask $\gamma _m$

3、when $2^{2n}$ chosen-plaintext pairs are used to estimate bit bias (i.e., correlation),
then we advise that the bit_bias_bound (i.e., the absolute correlation weight)
should not exceed $n - 3$.

4、if you want to run this code in your local environment,
please download cadical and replace the path in line 467
'''

import os
import time
import numpy as np


FullRound = 26
BlockSize = 64
HalfBlockSize = 32

pool = []

bit_bias = np.load('./6r_oneBitDiff_oneBitMask_cor_w.npy')
# bit_bias_bound: the weight of the absolute correlation threshold $c$
bit_bias_bound = 8
diff_index = 31         # set the one bit difference $\varDelta _m$
# active_input_bits: the set of strong unbalanced bits
active_input_bits = [i for i in range(BlockSize) if bit_bias[diff_index][i] < bit_bias_bound]

SearchRoundStart = 4
SearchRoundEnd = 5
InitialLowerBound = 0
# the upper bound of the cor
UpperBound = 7

alpha = 8   # 7
beta = 3    # 2

GroupConstraintChoice = 1

# Parameters for choice 1
GroupNumForChoice1 = 1

LinearBiasBound = list([])
for i in range(FullRound):
    LinearBiasBound += [0]


def CountClausesInRoundFunction(Round, Bias, clausenum):
    count = clausenum
    # Nonzero input mask
    count += 1
    for r in range(Round):
        # left modular
        count += 1
        count += 8
        for i in range(HalfBlockSize - 2):
            count += 16
        for i in range(HalfBlockSize):
            count += 4
        # right branch
        for i in range(HalfBlockSize):
            count += 4
        # left branch
        for i in range(HalfBlockSize):
            count += 4
        # right XOR
        for i in range(HalfBlockSize):
            count += 4
    return count


def CountClausesInSequentialEncoding(main_var_num, cardinalitycons, clause_num):
    count = clause_num
    n = main_var_num
    k = cardinalitycons
    if (k > 0):
        count += 1
        for j in range(1, k):
            count += 1
        for i in range(1, n-1):
            count += 3
        for j in range(1, k):
            for i in range(1, n-1):
                count += 2
        count += 1
    if (k == 0):
        for i in range(n):
            count += 1
    return count


def CountClausesForMatsuiStrategy(n, k, left, right, m, clausenum):
    count = clausenum
    if (m > 0):
        if ((left == 0) and (right < n-1)):
            for i in range(1, right + 1):
                count += 1
        if ((left > 0) and (right == n-1)):
            for i in range(0, k-m):
                count += 1
            for i in range(0, k-m+1):
                count += 1
        if ((left > 0) and (right < n-1)):
            for i in range(0, k-m):
                count += 1
    if (m == 0):
        for i in range(left, right + 1):
            count += 1
    return count


def GenSequentialEncoding(x, u, main_var_num, cardinalitycons, fout):
    n = main_var_num
    k = cardinalitycons
    if (k > 0):
        clauseseq = "-" + str(x[0]+1) + " " + str(u[0][0]+1) + " 0" + "\n"
        fout.write(clauseseq)
        for j in range(1, k):
            clauseseq = "-" + str(u[0][j]+1) + " 0" + "\n"
            fout.write(clauseseq)
        for i in range(1, n-1):
            clauseseq = "-" + str(x[i]+1) + " " + str(u[i][0]+1) + " 0" + "\n"
            fout.write(clauseseq)
            clauseseq = "-" + str(u[i-1][0]+1) + " " + str(u[i][0]+1) + " 0" + "\n"
            fout.write(clauseseq)
            clauseseq = "-" + str(x[i]+1) + " " + "-" + str(u[i-1][k-1]+1) + " 0" + "\n"
            fout.write(clauseseq)
        for j in range(1, k):
            for i in range(1, n-1):
                clauseseq = "-" + str(x[i]+1) + " " + "-" + str(u[i-1][j-1]+1) + " " + str(u[i][j]+1) + " 0" + "\n"
                fout.write(clauseseq)
                clauseseq = "-" + str(u[i-1][j]+1) + " " + str(u[i][j]+1) + " 0" + "\n"
                fout.write(clauseseq)
        clauseseq = "-" + str(x[n-1]+1) + " " + "-" + str(u[n-2][k-1]+1) + " 0" + "\n"
        fout.write(clauseseq)
    if (k == 0):
        for i in range(n):
            clauseseq = "-" + str(x[i]+1) + " 0" + "\n"
            fout.write(clauseseq)


def GenMatsuiConstraint(x, u, n, k, left, right, m, fout):
    if (m > 0):
        if ((left == 0) and (right < n-1)):
            for i in range(1, right + 1):
                clauseseq = "-" + str(x[i] + 1) + " " + "-" + str(u[i-1][m-1] + 1) + " 0" + "\n"
                fout.write(clauseseq)
        if ((left > 0) and (right == n-1)):
            for i in range(0, k-m):
                clauseseq = str(u[left-1][i] + 1) + " " + "-" + str(u[right - 1][i+m] + 1) + " 0" + "\n"
                fout.write(clauseseq)
            for i in range(0, k-m+1):
                clauseseq = str(u[left-1][i] + 1) + " " + "-" + str(x[right] + 1) + " " + "-" + str(u[right - 1][i+m-1] + 1) + " 0" + "\n"
                fout.write(clauseseq)
        if ((left > 0) and (right < n-1)):
            for i in range(0, k-m):
                clauseseq = str(u[left-1][i] + 1) + " " + "-" + str(u[right][i+m] + 1) + " 0" + "\n"
                fout.write(clauseseq)
    if (m == 0):
        for i in range(left, right + 1):
            clauseseq = "-" + str(x[i] + 1) + " 0" + "\n"
            fout.write(clauseseq)


def gen_linear_constraint_in_round_function(Round_st, Round_ed, xin, xout, w, a, b, c, d, fout):
    # Round function
    for round in range(Round_st, Round_ed):
        # right branch
        for i in range(HalfBlockSize):
            x = xin[round][i + HalfBlockSize] + 1
            y = a[round][i] + 1
            z = b[round][i] + 1
            clauseseq = str(x) + " " + str(y) + " " + "-" + str(z) + " 0\n"
            fout.write(clauseseq)
            clauseseq = str(x) + " " + "-" + str(y) + " " + str(z) + " 0\n"
            fout.write(clauseseq)
            clauseseq = "-" + str(x) + " " + str(y) + " " + str(z) + " 0\n"
            fout.write(clauseseq)
            clauseseq = "-" + str(x) + " " + "-" + str(y) + " " + "-" + str(z) + " 0\n"
            fout.write(clauseseq)
        # left modular
        # the first condition
        clauseseq = "-" + str(w[round][0] + 1) + " 0\n"
        fout.write(clauseseq)
        # the second condition
        x = xin[round][(HalfBlockSize - alpha) % HalfBlockSize] + 1
        y = a[round][0] + 1
        z = c[round][0] + 1
        w1 = w[round][1] + 1
        clauseseq = str(x) + " " + str(y) + " " + str(z) + " " + "-" + str(w1) + " 0\n"
        fout.write(clauseseq)
        clauseseq = str(x) + " " + str(y) + " " + "-" + str(z) + " " + str(w1) + " 0\n"
        fout.write(clauseseq)
        clauseseq = str(x) + " " + "-" + str(y) + " " + str(z) + " " + str(w1) + " 0\n"
        fout.write(clauseseq)
        clauseseq = "-" + str(x) + " " + str(y) + " " + str(z) + " " + str(w1) + " 0\n"
        fout.write(clauseseq)
        clauseseq = str(x) + " " + "-" + str(y) + " " + "-" + str(z) + " " + "-" + str(w1) + " 0\n"
        fout.write(clauseseq)
        clauseseq = "-" + str(x) + " " + "-" + str(y) + " " + str(z) + " " + "-" + str(w1) + " 0\n"
        fout.write(clauseseq)
        clauseseq = "-" + str(x) + " " + str(y) + " " + "-" + str(z) + " " + "-" + str(w1) + " 0\n"
        fout.write(clauseseq)
        clauseseq = "-" + str(x) + " " + "-" + str(y) + " " + "-" + str(z) + " " + str(w1) + " 0\n"
        fout.write(clauseseq)
        # the third condition
        for i in range(HalfBlockSize - 2):
            x = xin[round][(i + 1 + HalfBlockSize - alpha) % HalfBlockSize] + 1
            y = a[round][i + 1] + 1
            z = c[round][i + 1] + 1
            w1 = w[round][i + 1] + 1
            w2 = w[round][i + 2] + 1
            clauseseq = str(x) + " " + str(y) + " " + str(z) + " " + str(w1) + " " + "-" + str(w2) + " 0\n"
            fout.write(clauseseq)
            clauseseq = str(x) + " " + str(y) + " " + str(z) + " " + "-" + str(w1) + " " + str(w2) + " 0\n"
            fout.write(clauseseq)
            clauseseq = str(x) + " " + str(y) + " " + "-" + str(z) + " " + str(w1) + " " + str(w2) + " 0\n"
            fout.write(clauseseq)
            clauseseq = str(x) + " " + "-" + str(y) + " " + str(z) + " " + str(w1) + " " + str(w2) + " 0\n"
            fout.write(clauseseq)
            clauseseq = "-" + str(x) + " " + str(y) + " " + str(z) + " " + str(w1) + " " + str(w2) + " 0\n"
            fout.write(clauseseq)

            clauseseq = str(x) + " " + str(y) + " " + "-" + str(z) + " " + "-" + str(w1) + " " + "-" + str(
                w2) + " 0\n"
            fout.write(clauseseq)
            clauseseq = str(x) + " " + "-" + str(y) + " " + "-" + str(z) + " " + str(w1) + " " + "-" + str(
                w2) + " 0\n"
            fout.write(clauseseq)
            clauseseq = "-" + str(x) + " " + "-" + str(y) + " " + str(z) + " " + str(w1) + " " + "-" + str(
                w2) + " 0\n"
            fout.write(clauseseq)
            clauseseq = str(x) + " " + "-" + str(y) + " " + str(z) + " " + "-" + str(w1) + " " + "-" + str(
                w2) + " 0\n"
            fout.write(clauseseq)
            clauseseq = "-" + str(x) + " " + str(y) + " " + "-" + str(z) + " " + str(w1) + " " + "-" + str(
                w2) + " 0\n"
            fout.write(clauseseq)
            clauseseq = "-" + str(x) + " " + str(y) + " " + str(z) + " " + "-" + str(w1) + " " + "-" + str(
                w2) + " 0\n"
            fout.write(clauseseq)

            clauseseq = "-" + str(x) + " " + "-" + str(y) + " " + "-" + str(z) + " " + str(w1) + " " + str(
                w2) + " 0\n"
            fout.write(clauseseq)
            clauseseq = "-" + str(x) + " " + "-" + str(y) + " " + str(z) + " " + "-" + str(w1) + " " + str(
                w2) + " 0\n"
            fout.write(clauseseq)
            clauseseq = "-" + str(x) + " " + str(y) + " " + "-" + str(z) + " " + "-" + str(w1) + " " + str(
                w2) + " 0\n"
            fout.write(clauseseq)
            clauseseq = str(x) + " " + "-" + str(y) + " " + "-" + str(z) + " " + "-" + str(w1) + " " + str(
                w2) + " 0\n"
            fout.write(clauseseq)

            clauseseq = "-" + str(x) + " " + "-" + str(y) + " " + "-" + str(z) + " " + "-" + str(
                w1) + " " + "-" + str(
                w2) + " 0\n"
            fout.write(clauseseq)

        # the fourth condition
        for i in range(HalfBlockSize):
            x = xin[round][(i + HalfBlockSize - alpha) % HalfBlockSize] + 1
            y = a[round][i] + 1
            z = c[round][i] + 1
            clauseseq = str(x) + " " + "-" + str(z) + " " + str(w[round][i] + 1) + " 0\n"
            fout.write(clauseseq)
            clauseseq = "-" + str(x) + " " + str(z) + " " + str(w[round][i] + 1) + " 0\n"
            fout.write(clauseseq)
            clauseseq = str(y) + " " + "-" + str(z) + " " + str(w[round][i] + 1) + " 0\n"
            fout.write(clauseseq)
            clauseseq = "-" + str(y) + " " + str(z) + " " + str(w[round][i] + 1) + " 0\n"
            fout.write(clauseseq)

        # left branch
        for i in range(HalfBlockSize):
            x = c[round][i] + 1
            y = d[round][i] + 1
            z = xout[round][i] + 1
            clauseseq = str(x) + " " + str(y) + " " + "-" + str(z) + " 0\n"
            fout.write(clauseseq)
            clauseseq = str(x) + " " + "-" + str(y) + " " + str(z) + " 0\n"
            fout.write(clauseseq)
            clauseseq = "-" + str(x) + " " + str(y) + " " + str(z) + " 0\n"
            fout.write(clauseseq)
            clauseseq = "-" + str(x) + " " + "-" + str(y) + " " + "-" + str(z) + " 0\n"
            fout.write(clauseseq)

        # right XOR
        for i in range(HalfBlockSize):
            x = b[round][(i + beta) % HalfBlockSize] + 1
            y = d[round][i] + 1
            z = xout[round][i + HalfBlockSize] + 1
            clauseseq = str(x) + " " + "-" + str(y) + " 0\n"
            fout.write(clauseseq)
            clauseseq = "-" + str(x) + " " + str(y) + " 0\n"
            fout.write(clauseseq)
            clauseseq = str(x) + " " + "-" + str(z) + " 0\n"
            fout.write(clauseseq)
            clauseseq = "-" + str(x) + " " + str(z) + " 0\n"
            fout.write(clauseseq)


def gen_constraint_for_restricted_input(xin, fout):
    non_active_bits = [i for i in range(BlockSize) if i not in active_input_bits]
    for v in non_active_bits:
        clauseseq = "-" + str(xin[0][BlockSize - 1 - v] + 1) + " 0\n"
        fout.write(clauseseq)


# add conditions for linear mask $\gamma _m$ that have been searched
def gen_constraint_for_searched_paths_v1(Round, xin, xout, fout):
    # add constraints for linear hulls that have been searched
    tp = len(pool)
    for i in range(tp):
        cur_path = pool[i]
        assert len(cur_path) == (Round + 1) * BlockSize
        clauseseq = ""
        # the input linear mask
        for j in range(BlockSize):
            index = 0 * BlockSize + j
            if cur_path[index] == 0:
                clauseseq += str(xin[0][j] + 1) + " "
            else:
                clauseseq += "-" + str(xin[0][j] + 1) + " "
        clauseseq += "0\n"
        fout.write(clauseseq)


# add conditions for linear hulls that have been searched
def gen_constraint_for_searched_paths_v2(Round, xin, xout, fout):
    # add constraints for linear hulls that have been searched
    tp = len(pool)
    for i in range(tp):
        cur_path = pool[i]
        assert len(cur_path) == (Round + 1) * BlockSize
        clauseseq = ""
        # the input linear mask
        for j in range(BlockSize):
            index = 0 * BlockSize + j
            if cur_path[index] == 0:
                clauseseq += str(xin[0][j] + 1) + " "
            else:
                clauseseq += "-" + str(xin[0][j] + 1) + " "
        # the output linear mask
        for j in range(BlockSize):
            index = Round * BlockSize + j
            if cur_path[index] == 0:
                clauseseq += str(xout[Round - 1][j] + 1) + " "
            else:
                clauseseq += "-" + str(xout[Round - 1][j] + 1) + " "
        clauseseq += "0\n"
        fout.write(clauseseq)


def Decision(Round, Bias, MatsuiRoundIndex, MatsuiCount, flag, num=0, folder=None):
    TotalBias = HalfBlockSize * Round
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
            w[i][j] = count_var_num
            count_var_num += 1
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

    auxiliary_var_u = []
    for i in range(TotalBias - 1):
        auxiliary_var_u.append([])
        for j in range(Bias):
            auxiliary_var_u[i].append(count_var_num)
            count_var_num += 1
    # Count the number of clauses in the round function
    count_clause_num = 0
    count_clause_num = CountClausesInRoundFunction(Round, Bias, count_clause_num)
    # Count the number of clauses in the original sequential encoding
    Main_Var_Num = HalfBlockSize * Round
    CardinalityCons = Bias
    count_clause_num = CountClausesInSequentialEncoding(Main_Var_Num, CardinalityCons, count_clause_num)

    # count the number of clauses for restriced input
    count_clause_num += BlockSize - len(active_input_bits)

    # count the number of clauses for paths that have been searched
    count_clause_num += len(pool)

    # Open file
    file = open("Problem-Round" + str(Round) + "-Cor" + str(Bias) + ".cnf", "w")
    file.write("p cnf " + str(count_var_num) + " " + str(count_clause_num) + "\n")
    # Add constraints to claim nonzero input difference
    clauseseq = ""
    for i in range(BlockSize):
        clauseseq += str(xin[0][i] + 1) + " "
    clauseseq += "0" + "\n"
    file.write(clauseseq)
    # Round function
    gen_linear_constraint_in_round_function(Round_st=0, Round_ed=Round, xin=xin, xout=xout,
                                            w=w, a=a, b=b, c=c, d=d, fout=file)
    # Add constraints for the original sequential encoding
    Main_Vars = list([])
    for r in range(Round):
        for i in range(HalfBlockSize):
            Main_Vars += [w[Round - 1 - r][i]]
    GenSequentialEncoding(Main_Vars, auxiliary_var_u, Main_Var_Num, CardinalityCons, file)

    # add constraints for restricted input
    gen_constraint_for_restricted_input(xin=xin, fout=file)

    # add constraints for linears mask/hulls that have been searched
    gen_constraint_for_searched_paths_v1(Round=Round, xin=xin, xout=xout, fout=file)

    file.close()
    # Call solver cadical
    order = "/mnt/c/D_file/software/cadical/cadical-master/build/cadical " + \
            "Problem-Round" + str(Round) + "-Cor" + str(Bias) + ".cnf > " + \
            folder + "Round" + str(Round) + "-Cor" + str(Bias) + \
            "-No" + str(num + 1) + "-solution.out"
    os.system(order)
    # Extracting results
    order = "sed -n '/s SATISFIABLE/p' " + folder + "Round" + str(Round) + "-Cor" + str(Bias) + \
            "-No" + str(num + 1) + "-solution.out > SatSolution.out"
    os.system(order)
    order = "sed -n '/s UNSATISFIABLE/p' " + folder + "Round" + str(Round) + "-Cor" + str(Bias) + \
            "-No" + str(num + 1) + "-solution.out > UnsatSolution.out"
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
    order = "rm Problem-Round" + str(Round) + "-Cor" + str(Bias) + ".cnf"
    os.system(order)
    time_end = time.time()
    # Printing solutions
    if (flag == True):
        print("Round:" + str(Round) + "; Cor: " + str(Bias) + "; Sat; TotalCost: " + str(time_end - time_start))
    else:
        print("Round:" + str(Round) + "; Cor: " + str(Bias) + "; Unsat; TotalCost: " + str(time_end - time_start))
    return flag


def parse_result(round=None, Cor=None, num=None, folder=None):
    filePath = folder + "Round" + str(round) + "-Cor" + str(Cor) + "-No" + str(num+1) + "-solution.out"
    print('cur file path is ', filePath)
    n = (round + 1) * BlockSize
    result = []
    index = 0
    res = open(filePath, 'r')
    lines = res.readlines()
    for line in lines:
        line = line.strip('\n')
        x = line.split(" ")
        if x[0] == "v":
            m = len(x) - 1
            if index + m < n:
                for i in range(1, m + 1):
                    val = int(x[i])
                    if val < 0:
                        result.append(0)
                    else:
                        result.append(1)
                    index += 1
            else:
                for i in range(1, n - index + 1):
                    val = int(x[i])
                    if val < 0:
                        result.append(0)
                    else:
                        result.append(1)
                    index += 1
        if index == n:
            break
    res.close()

    return result


# main function
folder = './linear_hulls/diff_{}/{}_round/'.format(diff_index, SearchRoundStart)
if not os.path.exists(folder):
    os.makedirs(folder)

CountBias = InitialLowerBound
TotalTimeStart = time.time()
for totalround in range(SearchRoundStart, SearchRoundEnd):
    flag = False
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

    num = 0
    while (flag == False):
        flag = Decision(totalround, CountBias, MatsuiRoundIndex, MatsuiCount,
                        flag, num=num, folder=folder)
        if flag == False:
            order = "rm " + folder + "Round" + str(totalround) + "-Cor" + str(CountBias) + \
                    "-No" + str(num + 1) + "-solution.out"
            os.system(order)
            CountBias += 1
        else:
            new_path = parse_result(round=totalround, Cor=CountBias, num=num, folder=folder)
            pool.append(new_path)
            flag = False
            num += 1
        if CountBias > UpperBound:
            break

    LinearBiasBound[totalround] = CountBias - 1
    CountBias = CountBias - 1