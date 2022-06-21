# kasiski
Contains a python implementation of Kasiski's attack vs the Vigenère cipher. Simple code which can be used for demonstration/education etc. For more information see https://en.wikipedia.org/wiki/Kasiski_examination

Currently it only works for Swedish text since it depends on a language sample. (Kasiski's attack is based on statistical analysis). 

### Contents

    sample.txt = A sample of Swedish text (taken from recent newspaper articles). You may replace this file with a sample of any language. 
    
    kasiski.ini = Configuration file with language specific parameters.

    kasiski.py = A python program. 
    
    test_kasiski.py = Test code (uses pytest)

### Building and dependencies

    It is plain Python code, and runs under v 3.10. Only built-in modules used. 
    The test is based on pytest (which has to be installed using "pip")

### To use the python program

    >> python kasiski.py [parameters]

    where parameters are

    -enc   'clear text'  ## Encrypt a text string. The key has length 4 and is randomized.  

    -crack 'cipher text' ## Crack a decrypted text string. TIP: Use an encryption retrieved from "python kasiski.py -ct <cleartext>"

    -test 'clear text'  ## Run a prolonged test sequence (100 iterations with randomly generated keys) to see if cracking is feasible. 
    
    -if <input file name> ## Use this to read input from disk
    
    -of <output file name> ## Use this to write output to disk
    
    -h ## For help message.
    
### Testing

    First you need to install pytest using "pip install pytest"
    
    Then just run the tests using
    >> pytest
