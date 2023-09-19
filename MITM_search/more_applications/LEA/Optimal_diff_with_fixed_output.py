import os
import time
import random


diff_out = ((1 << 1) + (1 << 0), 0x0, 0x0, 0x0)     # [4, 10, 21, 36]


# for LEA128/128
FullRound = 22

BlockSize = 128
QuarterBlockSize = 32

alpha = 9
beta = 5
gamma = 3

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
        # for the first 32-bit word
        for i in range(QuarterBlockSize):
            count += 2
        # for the second 32-bit word, modular operation
        for i in range(QuarterBlockSize - 1):
            count += 8
        count += 4
        # modular probability weight
        for i in range(QuarterBlockSize - 1):
            count += 5

        # for the third 32-bit word, modular operation
        for i in range(QuarterBlockSize - 1):
            count += 8
        count += 4
        # modular probability weight
        for i in range(QuarterBlockSize - 1):
            count += 5

        # for the fourth 32-bit word, modular operation
        for i in range(QuarterBlockSize - 1):
            count += 8
        count += 4
        # modular probability weight
        for i in range(QuarterBlockSize - 1):
            count += 5
    return count


def CountClausesInSequentialEncoding(main_var_num, cardinalitycons, clause_num):
    count = clause_num
    n = main_var_num
    k = cardinalitycons
    if (k > 0):
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
    if (m > 0):
        if ((left == 0) and (right < n - 1)):
            for i in range(1, right + 1):
                count += 1
        if ((left > 0) and (right == n - 1)):
            for i in range(0, k - m):
                count += 1
            for i in range(0, k - m + 1):
                count += 1
        if ((left > 0) and (right < n - 1)):
            for i in range(0, k - m):
                count += 1
    if (m == 0):
        for i in range(left, right + 1):
            count += 1
    return count


def GenSequentialEncoding(x, u, main_var_num, cardinalitycons, fout):
    n = main_var_num
    k = cardinalitycons
    if (k > 0):
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

    if (k == 0):
        for i in range(n):
            clauseseq = "-" + str(x[i] + 1) + " 0" + "\n"
            fout.write(clauseseq)


def GenMatsuiConstraint(x, u, n, k, left, right, m, fout):
    if (m > 0):
        if ((left == 0) and (right < n - 1)):
            for i in range(1, right + 1):
                clauseseq = "-" + str(x[i] + 1) + " " + "-" + str(u[i - 1][m - 1] + 1) + " 0" + "\n"
                fout.write(clauseseq)

        if ((left > 0) and (right == n - 1)):
            for i in range(0, k - m):
                clauseseq = str(u[left - 1][i] + 1) + " " + "-" + str(u[right - 1][i + m] + 1) + " 0" + "\n"
                fout.write(clauseseq)

            for i in range(0, k - m + 1):
                clauseseq = str(u[left - 1][i] + 1) + " " + "-" + str(x[right] + 1) + " " + "-" + \
                            str(u[right - 1][i + m - 1] + 1) + " 0" + "\n"
                fout.write(clauseseq)

        if ((left > 0) and (right < n - 1)):
            for i in range(0, k - m):
                clauseseq = str(u[left - 1][i] + 1) + " " + "-" + str(u[right][i + m] + 1) + " 0" + "\n"
                fout.write(clauseseq)

    if (m == 0):
        for i in range(left, right + 1):
            clauseseq = "-" + str(x[i] + 1) + " 0" + "\n"
            fout.write(clauseseq)


def Decision(Round, Probability, MatsuiRoundIndex, MatsuiCount, flag):
    TotalProbability = (QuarterBlockSize - 1) * 3 * Round
    count_var_num = 0
    time_start = time.time()
    # Declare variable
    xin = []
    w = []
    xout = []
    for i in range(Round):
        xin.append([])
        w.append([])
        xout.append([])
        for j in range(BlockSize):
            xin[i].append(0)
        for j in range((QuarterBlockSize - 1)*3):
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
        for j in range((QuarterBlockSize - 1)*3):
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
    Main_Var_Num = (QuarterBlockSize - 1) * 3 * Round
    CardinalityCons = Probability
    count_clause_num = CountClausesInSequentialEncoding(Main_Var_Num, CardinalityCons, count_clause_num)

    # when we giev a fixed output, Matsui's strategy can't be used.
    # Count the number of clauses for Matsui's strategy
    # for matsui_count in range(0, MatsuiCount):
    #     StartingRound = MatsuiRoundIndex[matsui_count][0]
    #     EndingRound = MatsuiRoundIndex[matsui_count][1]
    #     LeftNode = (QuarterBlockSize - 1) * 3 * StartingRound
    #     RightNode = (QuarterBlockSize - 1) * 3 * EndingRound - 1
    #     PartialCardinalityCons = Probability - DifferentialProbabilityBound[StartingRound] - \
    #                              DifferentialProbabilityBound[Round - EndingRound]
    #     count_clause_num = CountClausesForMatsuiStrategy(Main_Var_Num, CardinalityCons, LeftNode, RightNode,
    #                                                      PartialCardinalityCons, count_clause_num)

    # count the number of clauses for fixed output diff
    count_clause_num += BlockSize

    # Open file
    file = open("Problem-Round" + str(Round) + "-Probability" + str(Probability) + ".cnf", "w")
    file.write("p cnf " + str(count_var_num) + " " + str(count_clause_num) + "\n")

    # Add constraints to claim nonzero input difference
    clauseseq = ""
    for i in range(BlockSize):
        clauseseq += str(xin[0][i] + 1) + " "
    clauseseq += "0" + "\n"
    file.write(clauseseq)

    # add constraints in the round function
    for round in range(Round):
        # add clauses for the first 32-bit word
        for i in range(QuarterBlockSize):
            clauseseq = str(xin[round][i] + 1) + " " + "-" + \
                        str(xout[round][i + 3 * QuarterBlockSize] + 1) + " " + "0" + "\n"
            file.write(clauseseq)
            clauseseq = "-" + str(xin[round][i] + 1) + " " + \
                        str(xout[round][i + 3 * QuarterBlockSize] + 1) + " " + "0" + "\n"
            file.write(clauseseq)

        # add clauses for modular in the second 32-bit word
        for i in range(QuarterBlockSize - 1):
            index_a = i
            index_b = i + QuarterBlockSize
            index_c = (i + QuarterBlockSize - alpha) % QuarterBlockSize
            index_c_plus = (i + 1 + QuarterBlockSize - alpha) % QuarterBlockSize
            clauseseq = str(xin[round][index_a] + 1) + " " + str(xin[round][index_b] + 1) + " " + \
                        "-" + str(xout[round][index_c] + 1) + " " + str(xin[round][index_a + 1] + 1) + \
                        " " + str(xin[round][index_b + 1] + 1) + " " + \
                        str(xout[round][index_c_plus] + 1) + " " + "0" + "\n"
            file.write(clauseseq)
            clauseseq = str(xin[round][index_a] + 1) + " " + "-" + str(xin[round][index_b] + 1) + \
                        " " + str(xout[round][index_c] + 1) + " " + str(xin[round][index_a + 1] + 1) + \
                        " " + str(xin[round][index_b + 1] + 1) + " " + \
                        str(xout[round][index_c_plus] + 1) + " " + "0" + "\n"
            file.write(clauseseq)
            clauseseq = "-" + str(xin[round][index_a] + 1) + " " + str(xin[round][index_b] + 1) + \
                        " " + str(xout[round][index_c] + 1) + " " + str(xin[round][index_a + 1] + 1) + \
                        " " + str(xin[round][index_b + 1] + 1) + " " + \
                        str(xout[round][index_c_plus] + 1) + " " + "0" + "\n"
            file.write(clauseseq)
            clauseseq = "-" + str(xin[round][index_a] + 1) + " " + "-" + str(xin[round][index_b] + 1) + \
                        " " + "-" + str(xout[round][index_c] + 1) + " " + str(xin[round][index_a + 1] + 1) + \
                        " " + str(xin[round][index_b + 1] + 1) + " " + \
                        str(xout[round][index_c_plus] + 1) + " " + "0" + "\n"
            file.write(clauseseq)
            # another four clauses
            clauseseq = str(xin[round][index_a] + 1) + " " + str(xin[round][index_b] + 1) + \
                        " " + str(xout[round][index_c] + 1) + " " + "-" + str(xin[round][index_a + 1] + 1) + \
                        " " + "-" + str(xin[round][index_b + 1] + 1) + " " + "-" + \
                        str(xout[round][index_c_plus] + 1) + " " + "0" + "\n"
            file.write(clauseseq)
            clauseseq = str(xin[round][index_a] + 1) + " " + "-" + str(xin[round][index_b] + 1) + \
                        " " + "-" + str(xout[round][index_c] + 1) + " " + "-" + str(xin[round][index_a + 1] + 1) + \
                        " " + "-" + str(xin[round][index_b + 1] + 1) + " " + "-" + \
                        str(xout[round][index_c_plus] + 1) + " " + "0" + "\n"
            file.write(clauseseq)
            clauseseq = "-" + str(xin[round][index_a] + 1) + " " + str(xin[round][index_b] + 1) + \
                        " " + "-" + str(xout[round][index_c] + 1) + " " + "-" + str(xin[round][index_a + 1] + 1) + \
                        " " + "-" + str(xin[round][index_b + 1] + 1) + " " + "-" + \
                        str(xout[round][index_c_plus] + 1) + " " + "0" + "\n"
            file.write(clauseseq)
            clauseseq = "-" + str(xin[round][index_a] + 1) + " " + "-" + str(xin[round][index_b] + 1) + \
                        " " + str(xout[round][index_c] + 1) + " " + "-" + str(xin[round][index_a + 1] + 1) + \
                        " " + "-" + str(xin[round][index_b + 1] + 1) + " " + "-" + \
                        str(xout[round][index_c_plus] + 1) + " " + "0" + "\n"
            file.write(clauseseq)
        # add clauses for lsb (modular)
        index_a = QuarterBlockSize - 1
        index_b = QuarterBlockSize - 1 + QuarterBlockSize
        index_c = (QuarterBlockSize * 2 - 1 - alpha) % QuarterBlockSize
        clauseseq = str(xin[round][index_a] + 1) + " " + str(xin[round][index_b] + 1) + \
                    " " + "-" + str(xout[round][index_c] + 1) + " " + "0" + "\n"
        file.write(clauseseq)
        clauseseq = str(xin[round][index_a] + 1) + " " + "-" + str(xin[round][index_b] + 1) + \
                    " " + str(xout[round][index_c] + 1) + " " + "0" + "\n"
        file.write(clauseseq)
        clauseseq = "-" + str(xin[round][index_a] + 1) + " " + str(xin[round][index_b] + 1) + \
                    " " + str(xout[round][index_c] + 1) + " " + "0" + "\n"
        file.write(clauseseq)
        clauseseq = "-" + str(xin[round][index_a] + 1) + " " + "-" + str(xin[round][index_b] + 1) + \
                    " " + "-" + str(xout[round][index_c] + 1) + " " + "0" + "\n"
        file.write(clauseseq)

        # add clauses for prob weight (modular)
        for i in range(QuarterBlockSize - 1):
            index_a = i
            index_b = i + QuarterBlockSize
            index_c = (i + QuarterBlockSize - alpha) % QuarterBlockSize
            index_c_plus = (i + 1 + QuarterBlockSize - alpha) % QuarterBlockSize
            clauseseq = "-" + str(xin[round][index_a + 1] + 1) + " " + str(xout[round][index_c_plus] + 1) + \
                        " " + str(w[round][i] + 1) + " " + "0" + "\n"
            file.write(clauseseq)
            clauseseq = str(xin[round][index_b + 1] + 1) + " " + "-" + str(xout[round][index_c_plus] + 1) + \
                        " " + str(w[round][i] + 1) + " " + "0" + "\n"
            file.write(clauseseq)
            clauseseq = str(xin[round][index_a + 1] + 1) + " " + "-" + str(xin[round][index_b + 1] + 1) + \
                        " " + str(w[round][i] + 1) + " " + "0" + "\n"
            file.write(clauseseq)
            clauseseq = str(xin[round][index_a + 1] + 1) + " " + str(xin[round][index_b + 1] + 1) + \
                        " " + str(xout[round][index_c_plus] + 1) + " " + "-" + \
                        str(w[round][i] + 1) + " " + "0" + "\n"
            file.write(clauseseq)
            clauseseq = "-" + str(xin[round][index_a + 1] + 1) + " " + "-" + str(xin[round][index_b + 1] + 1) + \
                        " " + "-" + str(xout[round][index_c_plus] + 1) + " " + "-" + \
                        str(w[round][i] + 1) + " " + "0" + "\n"
            file.write(clauseseq)

        # add clauses for modular in the third 32-bit word
        for i in range(QuarterBlockSize - 1):
            index_a = i + QuarterBlockSize
            index_b = i + QuarterBlockSize * 2
            index_c = ((i + beta) % QuarterBlockSize) + QuarterBlockSize
            index_c_plus = ((i + 1 + beta) % QuarterBlockSize) + QuarterBlockSize
            clauseseq = str(xin[round][index_a] + 1) + " " + str(xin[round][index_b] + 1) + " " + \
                        "-" + str(xout[round][index_c] + 1) + " " + str(xin[round][index_a + 1] + 1) + \
                        " " + str(xin[round][index_b + 1] + 1) + " " + \
                        str(xout[round][index_c_plus] + 1) + " " + "0" + "\n"
            file.write(clauseseq)
            clauseseq = str(xin[round][index_a] + 1) + " " + "-" + str(xin[round][index_b] + 1) + \
                        " " + str(xout[round][index_c] + 1) + " " + str(xin[round][index_a + 1] + 1) + \
                        " " + str(xin[round][index_b + 1] + 1) + " " + \
                        str(xout[round][index_c_plus] + 1) + " " + "0" + "\n"
            file.write(clauseseq)
            clauseseq = "-" + str(xin[round][index_a] + 1) + " " + str(xin[round][index_b] + 1) + \
                        " " + str(xout[round][index_c] + 1) + " " + str(xin[round][index_a + 1] + 1) + \
                        " " + str(xin[round][index_b + 1] + 1) + " " + \
                        str(xout[round][index_c_plus] + 1) + " " + "0" + "\n"
            file.write(clauseseq)
            clauseseq = "-" + str(xin[round][index_a] + 1) + " " + "-" + str(xin[round][index_b] + 1) + \
                        " " + "-" + str(xout[round][index_c] + 1) + " " + str(xin[round][index_a + 1] + 1) + \
                        " " + str(xin[round][index_b + 1] + 1) + " " + \
                        str(xout[round][index_c_plus] + 1) + " " + "0" + "\n"
            file.write(clauseseq)
            # another four clauses
            clauseseq = str(xin[round][index_a] + 1) + " " + str(xin[round][index_b] + 1) + \
                        " " + str(xout[round][index_c] + 1) + " " + "-" + str(xin[round][index_a + 1] + 1) + \
                        " " + "-" + str(xin[round][index_b + 1] + 1) + " " + "-" + \
                        str(xout[round][index_c_plus] + 1) + " " + "0" + "\n"
            file.write(clauseseq)
            clauseseq = str(xin[round][index_a] + 1) + " " + "-" + str(xin[round][index_b] + 1) + \
                        " " + "-" + str(xout[round][index_c] + 1) + " " + "-" + str(xin[round][index_a + 1] + 1) + \
                        " " + "-" + str(xin[round][index_b + 1] + 1) + " " + "-" + \
                        str(xout[round][index_c_plus] + 1) + " " + "0" + "\n"
            file.write(clauseseq)
            clauseseq = "-" + str(xin[round][index_a] + 1) + " " + str(xin[round][index_b] + 1) + \
                        " " + "-" + str(xout[round][index_c] + 1) + " " + "-" + str(xin[round][index_a + 1] + 1) + \
                        " " + "-" + str(xin[round][index_b + 1] + 1) + " " + "-" + \
                        str(xout[round][index_c_plus] + 1) + " " + "0" + "\n"
            file.write(clauseseq)
            clauseseq = "-" + str(xin[round][index_a] + 1) + " " + "-" + str(xin[round][index_b] + 1) + \
                        " " + str(xout[round][index_c] + 1) + " " + "-" + str(xin[round][index_a + 1] + 1) + \
                        " " + "-" + str(xin[round][index_b + 1] + 1) + " " + "-" + \
                        str(xout[round][index_c_plus] + 1) + " " + "0" + "\n"
            file.write(clauseseq)
        # add clauses for lsb (modular)
        index_a = QuarterBlockSize - 1 + QuarterBlockSize
        index_b = QuarterBlockSize - 1 + QuarterBlockSize * 2
        index_c = ((QuarterBlockSize - 1 + beta) % QuarterBlockSize) + QuarterBlockSize
        clauseseq = str(xin[round][index_a] + 1) + " " + str(xin[round][index_b] + 1) + \
                    " " + "-" + str(xout[round][index_c] + 1) + " " + "0" + "\n"
        file.write(clauseseq)
        clauseseq = str(xin[round][index_a] + 1) + " " + "-" + str(xin[round][index_b] + 1) + \
                    " " + str(xout[round][index_c] + 1) + " " + "0" + "\n"
        file.write(clauseseq)
        clauseseq = "-" + str(xin[round][index_a] + 1) + " " + str(xin[round][index_b] + 1) + \
                    " " + str(xout[round][index_c] + 1) + " " + "0" + "\n"
        file.write(clauseseq)
        clauseseq = "-" + str(xin[round][index_a] + 1) + " " + "-" + str(xin[round][index_b] + 1) + \
                    " " + "-" + str(xout[round][index_c] + 1) + " " + "0" + "\n"
        file.write(clauseseq)

        # add clauses for prob weight (modular)
        for i in range(QuarterBlockSize - 1):
            index_a = i + QuarterBlockSize
            index_b = i + QuarterBlockSize * 2
            index_c = ((i + beta) % QuarterBlockSize) + QuarterBlockSize
            index_c_plus = ((i + 1 + beta) % QuarterBlockSize) + QuarterBlockSize
            index_w = i + QuarterBlockSize - 1
            clauseseq = "-" + str(xin[round][index_a + 1] + 1) + " " + str(xout[round][index_c_plus] + 1) + \
                        " " + str(w[round][index_w] + 1) + " " + "0" + "\n"
            file.write(clauseseq)
            clauseseq = str(xin[round][index_b + 1] + 1) + " " + "-" + str(xout[round][index_c_plus] + 1) + \
                        " " + str(w[round][index_w] + 1) + " " + "0" + "\n"
            file.write(clauseseq)
            clauseseq = str(xin[round][index_a + 1] + 1) + " " + "-" + str(xin[round][index_b + 1] + 1) + \
                        " " + str(w[round][index_w] + 1) + " " + "0" + "\n"
            file.write(clauseseq)
            clauseseq = str(xin[round][index_a + 1] + 1) + " " + str(xin[round][index_b + 1] + 1) + \
                        " " + str(xout[round][index_c_plus] + 1) + " " + "-" + \
                        str(w[round][index_w] + 1) + " " + "0" + "\n"
            file.write(clauseseq)
            clauseseq = "-" + str(xin[round][index_a + 1] + 1) + " " + "-" + str(xin[round][index_b + 1] + 1) + \
                        " " + "-" + str(xout[round][index_c_plus] + 1) + " " + "-" + \
                        str(w[round][i] + 1) + " " + "0" + "\n"
            file.write(clauseseq)

        # add clauses for modular in the fourth 32-bit word
        for i in range(QuarterBlockSize - 1):
            index_a = i + QuarterBlockSize * 2
            index_b = i + QuarterBlockSize * 3
            index_c = ((i + gamma) % QuarterBlockSize) + QuarterBlockSize * 2
            index_c_plus = ((i + 1 + gamma) % QuarterBlockSize) + QuarterBlockSize * 2
            clauseseq = str(xin[round][index_a] + 1) + " " + str(xin[round][index_b] + 1) + " " + \
                        "-" + str(xout[round][index_c] + 1) + " " + str(xin[round][index_a + 1] + 1) + \
                        " " + str(xin[round][index_b + 1] + 1) + " " + \
                        str(xout[round][index_c_plus] + 1) + " " + "0" + "\n"
            file.write(clauseseq)
            clauseseq = str(xin[round][index_a] + 1) + " " + "-" + str(xin[round][index_b] + 1) + \
                        " " + str(xout[round][index_c] + 1) + " " + str(xin[round][index_a + 1] + 1) + \
                        " " + str(xin[round][index_b + 1] + 1) + " " + \
                        str(xout[round][index_c_plus] + 1) + " " + "0" + "\n"
            file.write(clauseseq)
            clauseseq = "-" + str(xin[round][index_a] + 1) + " " + str(xin[round][index_b] + 1) + \
                        " " + str(xout[round][index_c] + 1) + " " + str(xin[round][index_a + 1] + 1) + \
                        " " + str(xin[round][index_b + 1] + 1) + " " + \
                        str(xout[round][index_c_plus] + 1) + " " + "0" + "\n"
            file.write(clauseseq)
            clauseseq = "-" + str(xin[round][index_a] + 1) + " " + "-" + str(xin[round][index_b] + 1) + \
                        " " + "-" + str(xout[round][index_c] + 1) + " " + str(xin[round][index_a + 1] + 1) + \
                        " " + str(xin[round][index_b + 1] + 1) + " " + \
                        str(xout[round][index_c_plus] + 1) + " " + "0" + "\n"
            file.write(clauseseq)
            # another four clauses
            clauseseq = str(xin[round][index_a] + 1) + " " + str(xin[round][index_b] + 1) + \
                        " " + str(xout[round][index_c] + 1) + " " + "-" + str(xin[round][index_a + 1] + 1) + \
                        " " + "-" + str(xin[round][index_b + 1] + 1) + " " + "-" + \
                        str(xout[round][index_c_plus] + 1) + " " + "0" + "\n"
            file.write(clauseseq)
            clauseseq = str(xin[round][index_a] + 1) + " " + "-" + str(xin[round][index_b] + 1) + \
                        " " + "-" + str(xout[round][index_c] + 1) + " " + "-" + str(xin[round][index_a + 1] + 1) + \
                        " " + "-" + str(xin[round][index_b + 1] + 1) + " " + "-" + \
                        str(xout[round][index_c_plus] + 1) + " " + "0" + "\n"
            file.write(clauseseq)
            clauseseq = "-" + str(xin[round][index_a] + 1) + " " + str(xin[round][index_b] + 1) + \
                        " " + "-" + str(xout[round][index_c] + 1) + " " + "-" + str(xin[round][index_a + 1] + 1) + \
                        " " + "-" + str(xin[round][index_b + 1] + 1) + " " + "-" + \
                        str(xout[round][index_c_plus] + 1) + " " + "0" + "\n"
            file.write(clauseseq)
            clauseseq = "-" + str(xin[round][index_a] + 1) + " " + "-" + str(xin[round][index_b] + 1) + \
                        " " + str(xout[round][index_c] + 1) + " " + "-" + str(xin[round][index_a + 1] + 1) + \
                        " " + "-" + str(xin[round][index_b + 1] + 1) + " " + "-" + \
                        str(xout[round][index_c_plus] + 1) + " " + "0" + "\n"
            file.write(clauseseq)
        # add clauses for lsb (modular)
        index_a = QuarterBlockSize - 1 + QuarterBlockSize * 2
        index_b = QuarterBlockSize - 1 + QuarterBlockSize * 3
        index_c = ((QuarterBlockSize - 1 + gamma) % QuarterBlockSize) + QuarterBlockSize * 2
        clauseseq = str(xin[round][index_a] + 1) + " " + str(xin[round][index_b] + 1) + \
                    " " + "-" + str(xout[round][index_c] + 1) + " " + "0" + "\n"
        file.write(clauseseq)
        clauseseq = str(xin[round][index_a] + 1) + " " + "-" + str(xin[round][index_b] + 1) + \
                    " " + str(xout[round][index_c] + 1) + " " + "0" + "\n"
        file.write(clauseseq)
        clauseseq = "-" + str(xin[round][index_a] + 1) + " " + str(xin[round][index_b] + 1) + \
                    " " + str(xout[round][index_c] + 1) + " " + "0" + "\n"
        file.write(clauseseq)
        clauseseq = "-" + str(xin[round][index_a] + 1) + " " + "-" + str(xin[round][index_b] + 1) + \
                    " " + "-" + str(xout[round][index_c] + 1) + " " + "0" + "\n"
        file.write(clauseseq)

        # add clauses for prob weight (modular)
        for i in range(QuarterBlockSize - 1):
            index_a = i + QuarterBlockSize * 2
            index_b = i + QuarterBlockSize * 3
            index_c = ((i + gamma) % QuarterBlockSize) + QuarterBlockSize * 2
            index_c_plus = ((i + 1 + gamma) % QuarterBlockSize) + QuarterBlockSize * 2
            index_w = i + (QuarterBlockSize - 1) * 2
            clauseseq = "-" + str(xin[round][index_a + 1] + 1) + " " + str(xout[round][index_c_plus] + 1) + \
                        " " + str(w[round][index_w] + 1) + " " + "0" + "\n"
            file.write(clauseseq)
            clauseseq = str(xin[round][index_b + 1] + 1) + " " + "-" + str(xout[round][index_c_plus] + 1) + \
                        " " + str(w[round][index_w] + 1) + " " + "0" + "\n"
            file.write(clauseseq)
            clauseseq = str(xin[round][index_a + 1] + 1) + " " + "-" + str(xin[round][index_b + 1] + 1) + \
                        " " + str(w[round][index_w] + 1) + " " + "0" + "\n"
            file.write(clauseseq)
            clauseseq = str(xin[round][index_a + 1] + 1) + " " + str(xin[round][index_b + 1] + 1) + \
                        " " + str(xout[round][index_c_plus] + 1) + " " + "-" + \
                        str(w[round][index_w] + 1) + " " + "0" + "\n"
            file.write(clauseseq)
            clauseseq = "-" + str(xin[round][index_a + 1] + 1) + " " + "-" + str(xin[round][index_b + 1] + 1) + \
                        " " + "-" + str(xout[round][index_c_plus] + 1) + " " + "-" + \
                        str(w[round][index_w] + 1) + " " + "0" + "\n"
            file.write(clauseseq)

    # Add constraints for the original sequential encoding
    Main_Vars = list([])
    for r in range(Round):
        for i in range((QuarterBlockSize - 1)*3):
            Main_Vars += [w[Round - 1 - r][i]]
    GenSequentialEncoding(Main_Vars, auxiliary_var_u, Main_Var_Num, CardinalityCons, file)

    # when a fixed output is given, these conditions can't be used
    # Add constraints for Matsui's strategy
    # for matsui_count in range(0, MatsuiCount):
    #     StartingRound = MatsuiRoundIndex[matsui_count][0]
    #     EndingRound = MatsuiRoundIndex[matsui_count][1]
    #     LeftNode = (QuarterBlockSize - 1) * 3 * StartingRound
    #     RightNode = (QuarterBlockSize - 1) * 3 * EndingRound - 1
    #     PartialCardinalityCons = Probability - DifferentialProbabilityBound[StartingRound] - \
    #                              DifferentialProbabilityBound[Round - EndingRound]
    #     GenMatsuiConstraint(Main_Vars, auxiliary_var_u, Main_Var_Num, CardinalityCons, LeftNode, RightNode,
    #                         PartialCardinalityCons, file)

    # add constraints for fixed output diff
    diff_0, diff_1, diff_2, diff_3 = diff_out[0], diff_out[1], diff_out[2], diff_out[3]
    for i in range(QuarterBlockSize):
        if (diff_0 >> (QuarterBlockSize - 1 - i)) & 1 == 0:
            clauseseq = "-" + str(xout[Round - 1][i] + 1) + " " + "0" + "\n"
            file.write(clauseseq)
        else:
            clauseseq = str(xout[Round - 1][i] + 1) + " " + "0" + "\n"
            file.write(clauseseq)
    for i in range(QuarterBlockSize):
        if (diff_1 >> (QuarterBlockSize - 1 - i)) & 1 == 0:
            clauseseq = "-" + str(xout[Round - 1][i + QuarterBlockSize] + 1) + " " + "0" + "\n"
            file.write(clauseseq)
        else:
            clauseseq = str(xout[Round - 1][i + QuarterBlockSize] + 1) + " " + "0" + "\n"
            file.write(clauseseq)
    for i in range(QuarterBlockSize):
        if (diff_2 >> (QuarterBlockSize - 1 - i)) & 1 == 0:
            clauseseq = "-" + str(xout[Round - 1][i + QuarterBlockSize * 2] + 1) + " " + "0" + "\n"
            file.write(clauseseq)
        else:
            clauseseq = str(xout[Round - 1][i + QuarterBlockSize * 2] + 1) + " " + "0" + "\n"
            file.write(clauseseq)
    for i in range(QuarterBlockSize):
        if (diff_3 >> (QuarterBlockSize - 1 - i)) & 1 == 0:
            clauseseq = "-" + str(xout[Round - 1][i + QuarterBlockSize * 3] + 1) + " " + "0" + "\n"
            file.write(clauseseq)
        else:
            clauseseq = str(xout[Round - 1][i + QuarterBlockSize * 3] + 1) + " " + "0" + "\n"
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

        if flag == False:
            # Removing cnf file
            order = "rm Round" + str(totalround) + "-Probability" + \
                    str(CountProbability) + "-solution.out"
            os.system(order)

        CountProbability += 1

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
