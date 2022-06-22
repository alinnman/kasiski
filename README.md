# kasiski

Contains a python implementation (CLI) of Kasiski's attack vs the Vigenère cipher. Simple code which can be used for demonstration/education etc. 
Currently it only works for Swedish text since it depends on a language sample. (Kasiski's attack is based on statistical analysis). New languages can be added easily using configuration files only.

- For more information see https://en.wikipedia.org/wiki/Kasiski_examination
- Also see Introduction to Modern Cryptography (Katz & Lindell, CRC Press), page 12 (ISBN: 978-0815354369 )

### Contents

    sample.txt = A sample of Swedish text (taken from recent newspaper articles). You may replace this file with a sample of any language. 
    
    kasiski.ini = Configuration file with language specific parameters.

    kasiski.py = A python program. 
    
    test_kasiski.py = Test code (uses pytest)
    
    requirements.txt = Dependencies on external packages (managed by "pip")

### Building and dependencies

    The program runs under v 3.10. Only built-in modules are used. 
    The test is based on pytest (which has to be installed using "pip install -r requirements.txt")

### To use the python program

    >> python kasiski.py [parameters]

    where parameters are

    -enc   'clear text'  ## Encrypt a text string. The key has length 4 and is randomized.  

    -crack 'cipher text' ## Crack a decrypted text string. TIP: Use an encryption retrieved from "python kasiski.py -enc <cleartext>"

    -test 'clear text'  ## Run a prolonged test sequence (100 iterations with randomly generated keys) to see if cracking is feasible. 
    
    -if <input file name> ## Use this to read input from disk
    
    -of <output file name> ## Use this to write output to disk
    
    -ini <ini file name> ## To switch to another ini file. (Default = "kasiski.ini") 
    
    -h ## For help message.
    
### Testing
    
    Just run the tests using
    >> pytest
