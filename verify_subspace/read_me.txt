good_data:    
collected right pairs (x_y_z_right_pairs.npy) 
and corresponding round keys (x_y_z_corresponding_rks.npy),
where x is the file number, y is the number of right pairs,
and z is the key length 

fast_find_right_pairs.py:    
the code for collecting plaintext pairs conforming to the 4-round DC,
and the real key schedules of LEA-128, LEA-192, LEA-256 are used.

fast_verify_subspace.py:
the code for checking whether plaintext structures created from right pairs
pass the 4-round DC.

test_result_for-lea-128.txt,  test_result_for-lea-192.txt,  test_result_for-lea-192.txt:
the test results of running fast_verify_subspace.py