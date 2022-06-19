# kasiski
Contains a python implementation of Kasiski's cryptanalysis vs Vigenere cipher. Simple code which can be used for demonstration/education etc.

Currently it only works for Swedish text since it depends on a language sample. (Kasiski's method is based on statistical analysis). 

Contents:

sample.txt = A sample of Swedish text (taken from recent newspaper articles). 
kasiski.py = A python program. 

To use the python program:

>python kasiski.py [parameters]

where parameters are
--ct   "clear text"  : Encrypt a text string
--cit  "cipher text" : Crack a decrypted text string
--test "clear text"  : Run a prolonged test sequence (100 iterations with randomly generated keys) to see if cracking is feasible. 
