This project is an typical example of the MITM searching (Algorithm 2)
of differential-linear approximation (shortly denoted by DLA).

Algorithm 2: 
The target is searching for good DLAs
$\varDelta _m \xrightarrow {E_m} \gamma _m \xrightarrow {E_2} \gamma _{out}$
through three stages below:

1. for a given difference $\varDelta _m$, 
identify the set $\mathcal{B}_S$ of strong unbalanced bits;

2. searching for linear hulls $\gamma _m \xrightarrow {E_2} \gamma _{out}$
that satisfy two conditions:
	a) $\gamma _m [i] = 0$ for $i \notin \mathcal{B}_S$;
	b) the absolute correlation doesn't exceeds a given threshold.

3. experimentally verify the correlation of DLA
$\varDelta _m \xrightarrow {E_m} \gamma _m$
where $\gamma _m$ is returned in Stage 2.


Remark:
The above process is introduced in Algorithm 2 
of the submission.

Stage 3 only needs $\gamma _m$,
thus DLAs with non-duplicate mask $\gamma _m$
are returned in Stage 2.

The number of DLAs to be verified in Stage 3
does not exceed $2^{|B_S|}$ where $|B_S|$ 
is the size of the set of strong unbalanced bits.
Besides, stage 3 is performed by using N plaintext pairs
and N random master keys.


Notes:

1. the results of the folder "linear_hulls"
   is obtained under the following settings:

   a) $E_m$ and $E_2$ cover $6$ and $4$ rounds respectively;
   b) the absolute correlation of the linear hull
      $\gamma _m \rightarrow \gamma _{out}$
      should be greater or equal to $cor_w_6 = 2^{-6}$.

   Thus, the number of files in the folder
   "./linear_hulls/cor_w_6/diff_i/4_round/"
   ('diff_i' means that $\varDelta _m = [i]$)
   stands for the number of DLAs returned in Stage 2.

2. If you try to run Multi_LAs_with_restricted_input.py,
   please download cadical.
   If you want to modify the code or have any questions,
   refer to the following paper:

   Ling Sun, Wei Wang, Meiqin Wang.
   Accelerating the Search of Differential and
   Linear Characteristics with the SAT Method.
   IACR Trans. Symmetric Cryptol. 2021(1): 269-315 (2021)
