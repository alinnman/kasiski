'''
Contains a python implementation of Kasiski's attack vs the Vigenère cipher.
Simple code which can be used for demonstration/education etc. For more information see https://en.wikipedia.org/wiki/Kasiski_examination

Currently it only works for Swedish text since it depends on a language sample. (Kasiski's attack is based on statistical analysis).

/August Linnman, June 2022

'''

import string
from math import log
import random
import time
import argparse
import configparser
import sys

# The setup for the languate
langChars        = []
langAlphaChars   = []
langExtraChars   = ""
langNumChars     = ""
langSpecialChars = ""
lang             = ""

# Reverse lookup maps used
langMap        = {}
langAlphaMap   = {}

# Caches for monogram/bigram maps
monogramCache  = {}
bigramCache    = {}

# Contains the read sample text for the language
langSampleText = ""

# Set to the ini file used. Prevents re-loading of parameters.
languageSetup = ""

def setupLanguage (iniFileName):
    '''Setup all used language parameters from the ini file'''
    global languageSetup
    if languageSetup == iniFileName:
        return
    
    global langAlphaChars
    global langSampleText
    global lang
    global langExtraChars
    global langNumChars
    global langSpecialChars
    
    # Reset the monogram and bigram table cache objects.
    monogramCache  = {}
    bigramCache    = {}    

    # Initialize config parser and basic variables
    config = configparser.RawConfigParser()
    config.read(iniFileName)
    lang             = config ['LanguageSpecific']['lang']
    langExtraChars   = config ['LanguageSpecific']['langExtraChars']
    langNumChars     = config ['LanguageSpecific']['langNumChars']
    langSpecialChars = config ['LanguageSpecific']['langSpecialChars']
    sampleFileName   = config ['LanguageSpecific']['sampleFileName']
 
    # Set up the language strings
    langChars.append (' ')
    for c in string.ascii_lowercase:
        langChars.append (c)
    for c in langExtraChars:
        langChars.append (c)
    langAlphaChars = list(langChars)
    for c in langSpecialChars:
        langChars.append (c)
    for c in langNumChars:
        langChars.append (c) 
    
    # Read the sample text and store it
    with open(sampleFileName, 'r', encoding='utf-8') as file:
        langSampleText = file.read().replace('\n', '')

    # Set up the reverse maps
    for i in range (0, len(langChars)):
        langMap      [langChars[i]] = i
    for i in range (0, len(langAlphaChars)):
        langAlphaMap [langAlphaChars[i]] = i
        
    # Set this variable to prevent unnecessary re-loads.    
    languageSetup = iniFileName

def setupMonograms (s, alpha=False):
    '''Setup a monogram table
       s : String to use
       alpha : Indicates whether we only use alpha characters or not.
    '''
    global monogramCache

    # If the monogram table already exists then reuse it
    try:
        return monogramCache [(s,alpha)]
    except KeyError:
        pass

    result = {}
    
    # Select chars and reverse map based on alpha parameter.
    if alpha:
        charsChosen = langAlphaChars
        mapChosen = langAlphaMap
    else:
        charsChosen = langChars
        mapChosen = langMap
        
    # Initialize everything to zeros.    
    for c in charsChosen:
        result [c] = 0
        
    # Go through language string for every character.
    for i in range(0,len(s)):
        a = s [i]
        aPos = -1
        
        # Find the position of the character
        try:
            aPos = mapChosen [a]
        except KeyError:
            pass
            
        # If the character was found, the increase the monogram counter
        if aPos != -1:
            monogram = str(a)
            count = 0
            try:
                count = result [monogram]
            except KeyError:
                pass
            result [monogram] = count + 1
            
    # Sum all occurrences
    summing = sum (result.values())
    
    # Divide all values, i.e. normalize. 
    for e in result:
        v = result [e]
        if summing == 0:
            result [e] = 0
        else:
            result [e] = v / summing
    
    # Store the result in the cache
    monogramCache [(s,alpha)] = result
    # Return result
    return result

def setupBigrams (s):
    '''Setup a bigram table
       s : String to use
    '''
    global bigramCache

    s = s.lower()

    # If the bigram table already exists then reuse it
    try:
        return bigramCache [s]
    except KeyError:
        pass

    result = {}

    # Go through string and select all pairs of adjacent characters
    for i in range(0,len(s)-1):
        a = s [i]
        b = s [i+1]
        aPos = -1
        bPos = -1
        # Make sure both characters are part of the language
        try:
            aPos = langAlphaMap [a]
        except KeyError:
            pass
        try:
            bPos = langAlphaMap [b]
        except KeyError:
            pass
        # Add the pair to the bigram table
        if (aPos != -1) and (bPos != -1):
            bigram = str(a) + str(b)
            count = 0
            try:
                count = result [bigram]
            except KeyError:
                pass
            result [bigram] = count + 1
    # Normalize the structure
    summing = sum (result.values())
    for e in result:
        v = result [e]
        result [e] = v / summing
    # Add result to cache
    bigramCache [s] = result
    # Return result
    return result

def freqAnalysis (s, lang=langSampleText, alpha=False):
    '''
    Analyze frequency of letters in a string, and compare with corresponding frequencies in a language
    s : String to analyze
    lang : Compared language
    alpha : Indicates whether we only consider alpha characters or not.
    '''
    s = s.lower ()
    langNgrams = setupMonograms (lang, alpha)
    sNgrams = setupMonograms (s, alpha)
    count = 0
    summed = 0
    
    # We construct a sum of squared differences in frequency (Least-squares loss function). 
    # This should be as low as possible to indicate positive correlation between string and language
    for m in sNgrams:
        a = sNgrams [m]
        b = langNgrams [m]
        summed += (a - b)**2
        count += 1
    retval = summed
    # Avoid log (0)
    if retval == 0:
        retval = -1
    else:
        retval = -log(retval)    
    return retval

def freqAnalysisBigrams (s, lang=langSampleText):
    '''
    Analyze frequency of bigrams in a string, and compare with corresponding frequencies in a language
    s : String to analyze
    lang : Compared language
    '''
    s = s.lower ()
    langBgrams = setupBigrams (lang)
    sBgrams = setupBigrams (s)
    count = 0
    summed = 0
    # We construct a sum of squared differences in frequency (Least-squares loss function). 
    # This should be as low as possible to indicate positive correlation between string and language    
    for m in sBgrams:
        a = sBgrams [m]
        b = 0
        try:
            b = langBgrams [m]
        except KeyError:
            pass
        # Punish score if bigram not found
        if b == 0:
            b = -0.1
        summed += (a - b)**2
        count += 1
    retval = summed
    # Avoid log (0)
    if retval == 0:
        retval = -1
    else:
        retval = -log(retval)
    return retval

def indexOfCoincidence (s):
    '''
    See if the string seems to have reduced entropy, i.e. if it seems non-random. 
    E.g. "AAAAA" has higher index of coindidence compared to "xwore"
    s : String to analyze
    '''
    s = s.lower ()
    monograms = setupMonograms (s)
    result = 0
    for m in monograms:
        result += monograms[m]**2
    return result

def Viginere (s, K, alpha=False):
    '''
    The Viginere encryption algorithm. 
    s : String to encrypt
    K : Key to use (list of integers). Note: If len(K) == 1 then this is reduced to a Caesar cipher
    alpha : Indicates whether we only consider alpha characters or not. 
    '''
    result = []
    s = s.lower()
    if alpha:
        C = langAlphaChars
        M = langAlphaMap
    else:
        C = langChars
        M = langMap
    cl = len (C)
    if cl == 0:
        raise Exception ("len(C) must be > 0")
    kl = len (K)
    if kl == 0:
        raise Exception ("len(K) must be > 0")
    kCount = 0
    # Go through string and construct encrypted string
    for c in s:
        # If the character cannot be found then we encrypt a ' ' character
        try:
            cn = M [c]
        except KeyError:
            cn = M [' ']
        pn = (cn + K[kCount]) % cl 
        rn = C [pn]
        result.append (rn)
        kCount = (kCount + 1) % kl
    resultS = ""
    return resultS.join (result)

def negateKey (K):
    '''
    Decryption is made with decK <- (-encK)
    K : key list
    '''
    result = []
    for i in range (0, len(K)):
        result.append (-K[i])
    # Return a negated key (decryption key)
    return result

def findBlockSizes (c, minSize, maxSize, numBs=2):
    '''
    Performs a statistical analysis to find a likely used block sized used for Viginère encryption.
    This is done by calculating the index of coincidence for increasing possible block sizes, and trying 
    to find a sudden increase. This may indicate a used block size. 
    c : Encrypted string
    minSize : The shortest blocksize to consider
    maxSize : The largest blocksize to consider
    numBs : Number of possible blocksizes to investigate
    '''
    assert (maxSize >= minSize)
    
    prevIoc = sys.maxsize # A very large number
    foundRaises = {}
    # Iterate through all possible block sizes
    for blockSize in range (minSize, maxSize+1):
        iocSum = 0
        counter = 0
        # Collect all strings from the respective block sizes
        for testStringIndex in range (0,blockSize):
            testString = ""
            currentPos = testStringIndex
            while currentPos < len(c):
                testString = testString + c[currentPos]
                currentPos += blockSize
            # Does this string show low entropy? 
            ioc = indexOfCoincidence (testString)
            iocSum += ioc
            counter += 1
        # Now make an average of all coincidence values found
        averageIoc = iocSum / counter
        # Can we see an increase ("raise") in the coincidence mean value compared to previously computed value
        foundRaises [blockSize] = averageIoc / prevIoc
        prevIoc = averageIoc
    # Just return if nothing is found
    if len(foundRaises) == 0:
        return []
    # Find the sharpest "raise" value found.
    bestBlockSize = max(foundRaises.items(), key=lambda x: x[1])[0]
    # Sort the other found block sized
    sortedBlockSizes = dict(sorted(foundRaises.items(), key=lambda item: item[1], reverse=True))
    retVal = []
    counter = 0
    # Pack the result structure
    for bs in sortedBlockSizes:
        retVal.append (bs)
        counter += 1
        if counter >= numBs:
            break
    return retVal

def getExtract (s, bs, index):
    '''Helper function to get a "zebra" substring from a string
    s : String to extract from
    bs : The block size used
    index : Start position
    '''
    result = []
    currentPos = index
    while currentPos < len(s):
        result.append (s[currentPos])
        currentPos += bs
    retVal = ""
    return retVal.join(result)

def attack (s,minSize,maxSize,bsExamined, look=-1, alphaOnly=False):
    ''' 
    Core cryptanalysis routine for Viginère cipher.
    s : String to crack
    minSize : minimum block size to consider
    maxSize : maximum block size to consider
    bsExamined : max number of block sizes to consider
    look : For debugging. Shows data about a particular block size. Default = -1 (no debugging)
    alphaOnly : Indicates whether we consider only alpha strings or not
    '''

    # Start by finding possible block sizes
    bss = findBlockSizes (s,minSize,maxSize,bsExamined)
    comparedResults = {}

    # Iterate through all considered block sizes
    for bs in bss:

        if bs == -1:
            return "-"

        candidateKeys = []
        bestIml = sys.maxsize # A very large number
        
        # Now iterate for a single item in a possible key, i.e. try to find a 'Caesar' number to use for decryption
        # and see if this can reveal a favourable frequence analysis. 
        for i in range (0, bs):
            candidateKeys.append ([])
            testString = getExtract (s, bs, i)

            examinedTestKeys = {}

            # Iterate through all key item values
            for testKey in range(0, len(langChars)):
                Ktest = [-testKey]
                # Decrypt "Caesar style"
                decPermutedTestKey = Viginere (testString, Ktest, alpha=alphaOnly)

                if look == i:
                    print ("Look at decrypted string for K = "+str(Ktest)+ " = <" + str(decPermutedTestKey) + ">")

                # Does it look like some kind of language here? 
                freqPoint = freqAnalysis (decPermutedTestKey, langSampleText, False)  
                examinedTestKeys [testKey] = freqPoint

            # Now sort on best key item values found
            B = max(examinedTestKeys.items(), key=lambda x: x[1])
            bestKey = B [0]
            bestValue = B [1]

            if look == i:
                print ("Best key was = " + str(bestKey))

            # Store and save the results
            candidateKeys [i].append (bestKey)
        # Do final collection of the results
        decryptKey = []
        for i in range (0, len(candidateKeys)):
            try:
                decryptKey.append (-(candidateKeys[i][0]))
            except IndexError:
                # Failed to find suitable key.
                pass
        # Now make an attempt to decrypt the string used a possible decryption key
        result = Viginere (s, decryptKey, alpha=alphaOnly)

        ST = langSampleText
        # Give this decryption a score based on a weighted calculation of frequency analysis on monograms and bigrams
        freqDecrypted = 2*freqAnalysis (result, ST) + freqAnalysisBigrams (result, ST)
        comparedResults [bs] = (result, freqDecrypted, decryptKey)

    # Very long keys, or short plaintexts will be almost impossible to crack. 
    if len(comparedResults) == 0:
        raise Exception ("Cannot find any suitable decryption key. Cleartext is probably too short.")
        
    # Pack the final results and return
    B = max(comparedResults.items(), key=lambda x: x[1][1])
    bestResult = B [1][0]
    bestKey    = B [1][2]
    return bestResult, bestKey

def stringSimilarity (a, b):
    '''
    Helper routine to find the similarity between two strings
    a, b : Strings to compare
    Returns a value  0 <= r <= 1.0
    '''
    toCheck = min (len(a), len(b))
    matches = 0
    for i in range (0, toCheck):
        if (a[i] == b[i]):
            matches += 1
    return matches / toCheck

def doEncryption (clearText, minKeyLength, maxKeyLength, alphaOnly=False):
    '''
    Encrypt a string used a randomized key. 
    clearText : String to encrypt
    minKeyLength : minimum key length to use
    maxKeyLength : maximum key length to use
    alphaOnly : indicates whether we consider only alpha strings or not
    '''

    assert (maxKeyLength >= minKeyLength)

    # Select used key length
    KL = int(random.uniform (minKeyLength, maxKeyLength))

    # Randomize a key
    K = []
    if alphaOnly:
        LC = len(langAlphaChars)
    else:
        LC = len(langChars)
    for i in range (0, KL):
        shift = int(random.uniform (0, LC))
        K.append (shift)

    # Encrypt the string
    encrypted = Viginere (clearText, K, alpha=alphaOnly)
    
    # Make sure we can decrypt back
    decrypted = Viginere (encrypted, negateKey(K), alpha=alphaOnly)
    assert (decrypted.lower () == clearText.lower())
    
    return encrypted, K

def testAttack (testText, minKeyLength, maxKeyLength, maxSize, bsExamined, look=-1, alphaOnly=False): 
    '''
    Perform an attack test.
    testText : cleartext to use for encryption and attack.
    minKeyLength : minimum key length to use for encryption
    maxKeyLength : maximum key length to use for encryption
    maxSize : maximum key length used for *cracking*
    bsExamined : number of block sizes to consider while *cracking*
    look : Debug variable
    alphaOnly : indicates whether we consider only alpha strings or not
    '''
    encrypted, usedKey = doEncryption (testText, minKeyLength, maxKeyLength, alphaOnly=alphaOnly)

    result, bestKey = attack (encrypted, 1, maxSize, bsExamined, look=look, alphaOnly=alphaOnly)

    return stringSimilarity (result.lower(), testText.lower()), bestKey, result

def testAttacks (clearText, minKl=4, maxKl=4, outputFileName=None,\
                 successiveAttacks=False, verbose=False, maxKeyLengthSearch=None):
    '''
    A test sequence for cracking attempts. Can be used for measuring performance (cpu time and successful cracking)
    clearText : cleartext to use
    minKl : minimum key length used for *encryption*
    maxKl : maximum key length used for *encryption*
    outputFileName : file to use for writing report. Default = None (use stdout)
    '''
    NROFTESTS = 100
    MINKL = minKl
    MAXKL = maxKl
    TESTTEXT = clearText
    ALPHA = False
    BSEXAMINED = 3
    LOOK = -1
    if maxKeyLengthSearch is None:
        MAXKEYLENGTHSEARCH = max(1,len(TESTTEXT)) // 10
    else:
        MAXKEYLENGTHSEARCH = maxKeyLengthSearch

    original_stdout = sys.stdout
    if outputFileName is not None:
        f = open(outputFileName, 'w')
        sys.stdout = f 
        
    if successiveAttacks:
        startIndex = minKl
        endIndex   = maxKl
    else:
        startIndex = 1
        endIndex   = 1
        
    for attack in range (startIndex, endIndex+1):
    
        startTime = time.time()        
        successMeasure = 0.0
        if verbose:
            print ("Listing the results of cracking")
        for i in range (0, NROFTESTS):
            if successiveAttacks:
                kl1 = attack
                kl2 = attack
            else:
                kl1 = MINKL
                kl2 = MAXKL
            sm, bestKey, result = testAttack (TESTTEXT, kl1, kl2, MAXKEYLENGTHSEARCH, BSEXAMINED, LOOK, alphaOnly=ALPHA)
            if verbose:
                print ("Using key : " + str(bestKey))
                print (result)
            successMeasure += sm
            endTime = time.time()
            avgSuccessMeasure = successMeasure / NROFTESTS
        if verbose:
            print ("")
        if successiveAttacks:
            insertKlText = "Key length for encryption = " + str(attack) + ". "
        else:
            insertKlText = ""
        print (str(NROFTESTS) + " attacks performed. "+insertKlText+\
        "Success measure is " + str(round(avgSuccessMeasure*100,2)) +\
        " %. Time taken = " + str(endTime-startTime) + " sec.")

    sys.stdout = original_stdout
    if outputFileName is not None:
        print ("Done. Report written to " + outputFileName)


def encrypt (s, kl) :
    '''
    Encrypt a string using a randomized key
    s : String to encrypt
    kl : Used key length
    '''
    encrypted, usedKey = doEncryption (s, kl, kl, False)
    return encrypted, usedKey

def parseArguments (args):
    '''
    Parse command line and initialize variables. Also setup language data.
    '''
    parser = argparse.ArgumentParser(description='Kasiski method',\
                                     epilog='This is a simple test program for Kasiski\'s attack on Vigenère ciphers')

    parser.add_argument("-if", "--input_file",\
    help="input file (to use if input parameter values are left blank)", \
                        action="store")
    parser.add_argument("-of", "--output_file",\
    help="output file (to use instead of standard output for encrypted or cracked strings)", \
                        action="store")
    parser.add_argument("-ini", "--ini_file",\
    help="Ini file to use (default is 'kasiski.ini')", \
                        action="store", nargs='?', default="kasiski.ini")                        
    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument("-enc",  "--cleartext_to_encrypt", \
                       help="Encrypt a string.",\
                       action="store", nargs='?', default="",metavar="Cleartext")  
    group.add_argument("-crack", "--ciphertext_to_crack", \
                       help="Crack a ciphertext string.",\
                       action="store", nargs='?', default="",metavar="Ciphertext")
    group.add_argument("-test","--run_sequence_of_tests", \
                       help="Run a sequence (100 iterations) of encryption and cracking attempts. Keys are randomized.",\
                       action="store", nargs='?', default="",metavar="Cleartext")    
    parser.add_argument("-succ","--successive_test", \
                       help="Indicate if successive test should be run (Used for the -test command)", \
                       action="store_const", const="True")                                            
    #group2 = group.add_argument_group ()                       
                     
    '''
    group.add_argument("-test","--run_sequence_of_tests", \
                       help="Cleartext to use for encryption and cracking attempts in a test sequence",\
                       action="store", nargs='?', default="")
    '''

    #group3 = group2.add_argument_group()                       
    parser.add_argument("-minkl","--min_key_length", \
                       help="Min key length used in encryption for the -enc and -test commands. (default is 4)", \
                       action="store", nargs='?', default="4")
    parser.add_argument("-maxkl","--max_key_length", \
                       help="Max key length used in encryption for the -enc and -test commands."+\
                       " (must be greater than -minkl, set == -minkl if omitted)", \
                       action="store", nargs='?', default="-1") 

    verbose = False

    argsParsed = parser.parse_args(args)
    va = vars(argsParsed)
    if verbose:
        print ("va = " + str(va)) 

    ct             =     va ['cleartext_to_encrypt' ]
    cit            =     va ['ciphertext_to_crack'  ]
    test           =     va ['run_sequence_of_tests']
    minkl          = int(va ['min_key_length'       ])
    maxkl          = int(va ['max_key_length'       ])
    succTest       =     va ['successive_test'      ]
    
    if succTest is None:
        succTest = False
    else:
        succTest = True
        
    if maxkl == -1:
        maxkl = minkl

    inputFileName  =     va ['input_file'           ]
    outputFileName =     va ['output_file'          ]

    if (ct is None or cit is None or test is None) and inputFileName is None:
        parser.error ("You need to specify -if since one of -enc, -crack or -test have been set but not assigned a value")
        
    if maxkl < minkl :
        parser.error ("-maxkl parameter must be >= -minkl parameter")
    
    iniFileName = 'kasiski.ini' 
    setupLanguage (va ['ini_file'])

    return ct, cit, test, inputFileName, outputFileName, minkl, maxkl, succTest 

def main (args=None):
    '''
    Main routine of program
    '''

    def readFromFile (fileName) :
        with open(fileName, 'r', encoding='utf-8') as file:
            return (file.read().replace('\n', ''))

    def writeToFile (fileName, s) :
        with open(fileName, 'w', encoding='utf-8') as file:
            file.write(s)

    if args == None:
        args = sys.argv[1:]
    clearText, cipherText, test, inputFileName, outputFileName, minkl, maxkl, succTest =\
        parseArguments (args)

    if clearText != "" :
        if inputFileName is not None:
            clearText = readFromFile (inputFileName)
        encryptedText, usedKey = encrypt (clearText, minkl)
        if outputFileName is not None:
            writeToFile (outputFileName, encryptedText)
            print ("Encrypted text written to " + outputFileName)
        else:
            print ("This is the encryption: <" + encryptedText + ">")
        print ("Used key = " + str(usedKey))
    elif cipherText != "":
        if inputFileName is not None:
            cipherText = readFromFile (inputFileName)
        startTime = time.time()
        result, bestKey = attack (cipherText, 1, len(cipherText), 3)
        endTime = time.time()
        probKeyMsg = " This key was likely used while encrypting : " + str(negateKey(bestKey)) + ". "
        if outputFileName is not None:
            writeToFile (outputFileName, result)
            print ("Cracking attempt written to " + outputFileName + probKeyMsg +\
             ". Time taken = "+str(endTime-startTime)+" sec.")
        else:
            print ("This is the cracking attempt <" + result + ">."+probKeyMsg+" Time taken = "+str(endTime-startTime)+" sec.")
    elif test != "":
        if inputFileName is not None:
            test = readFromFile (inputFileName)
        testAttacks(test, outputFileName=outputFileName, minKl=minkl, maxKl=maxkl, successiveAttacks=succTest)
    else:
        raise Exception ("Invalid arguments specified")

if __name__ == "__main__":
    main ()






