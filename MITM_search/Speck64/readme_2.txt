
1、linear_hulls/cor_w_i/diff_j/k_round/ :  
linear trails with non-duplicate input linear masks $\gamma_m$
returned in Stage 2 under the following settings:
1) E_2 covers k rounds
2) the input difference $\varDelta _m$ is $[j]$
3) when we search linear trails in stage 2,
    the upper bound of the weight of absolute correlation.

2、6r_oneBitDiff_oneBitMask_cor_w.npy  :
the weight of absolute correlation of the following DLAs of E_m:
$\varDelta_m = [i] \rightarrow \gamma_m = [j]$
for $i, j \in \{0, \cdots, n-1\}$ where $n$ is blocksize.

These weights are estimated using 2^22 plainttext pairs.

3、6r_oneBitDiff_oneBitMask_cor_w.txt  :
the details of the file (6r_oneBitDiff_oneBitMask_cor_w.npy),
including: 
1)  the number of strong unbalanced bits, i.e., $|\mathcal{B}_S|$
2)  concrete strong unbalanced bits

4、compute_bit_bias.py  :  
the code used in Stage 1 to estimate correlation of DLAs.

5、diff_prob_with_one_bit_output.txt  :
the optimal probability of prepended differential
under fixed output difference $[i]$

6、Multi_LAs_with_restricted_input.py  :
Search linear trails (with non-duplicate input linear mask) 
of E_2 in Stage 2 by setting weak unbalanced bits to 0.

This is an SAT-based implementation.

7、Optimal_diff_with_fixed_output.py  :
Search optimal prepended differential 
$\varDelta _{in} \rightarrow \varDelta_m$
under fixed output difference $\varDelta_m$

This is an SAT-based implementation.

8、parse_search_result.py  :
Parse linear masks returned in Stage 2

9、 speck.py  :  
the implementation of the current Speck member

10、verify_DLA_Cor.py  :
the code used in Stage 3 to verify the correlalation of DLAs

















