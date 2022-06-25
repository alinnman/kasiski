# kasiski

Contains a python implementation (CLI) of Kasiski's attack vs the Vigenère cipher. Simple code which can be used for demonstration/education etc. 
Currently it only works for Swedish text since it depends on a language sample. (Kasiski's attack is based on statistical analysis). New languages can be added easily using configuration files only.

The Viginère cipher was widely used in the 1600:s until the 1800:s and was considered to be unbreakable. It was the crypto of choice for diplomats, military etc. Friedrich Kasiski, a German military officer and cryptographer found an attack method in 1863 and this marked the dawn of modern cryptanalysis (art of attacking ciphers), and raised the bar considerably on what constitutes a secure crypto system. Applying Kasiski's method on a ciphertext using pen and paper makes it possible to attack it in a timespan of days only. Using a computer program, such as this one, the same feat can be accomplished in a fraction of a second.  

Using Python for implementing this attack is non-optimal since it is a not-so-fast programming language. Java, C or assembly language would make the implementation at least one order of magnitude faster. 

The code provided here is intended to provide a pedagogic example and to show how dangerous it is to rely on outdated technology for secure encryption. 

- For more information see https://en.wikipedia.org/wiki/Kasiski_examination
- Also see Introduction to Modern Cryptography (Katz & Lindell, CRC Press), page 12 (ISBN: 978-0815354369 )

### Contents

    sample.txt = A sample of Swedish text (taken from recent newspaper articles). You may replace this file with a sample of any language. 
    
    kasiski.ini = Configuration file with language specific parameters.

    kasiski.py = A python program. (Main module)
    
    test_kasiski.py = Test code (Test module)
    
    requirements.txt = Dependencies on external packages (managed by "pip")

### Building and dependencies

    The program has been developed in Python v 3.9.7. Only built-in modules are used in the main module. 
    The test module is based on pytest (which has to be installed using "pip install -r requirements.txt")

### To use the python program

    >> python kasiski.py [parameters] ## To run the program
    >> python kasisky.py -h ## For help message including parameter descriptions.
    
### Testing
    
    Just run the tests using
    >> pytest
