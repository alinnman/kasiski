'''
Contains a python implementation of Kasiski's attack vs the Vigenère cipher.
Simple code which can be used for demonstration/education etc. For more information see https://en.wikipedia.org/wiki/Kasiski_examination
Contains a python implementation of Kasiski's attack vs the Vigenère cipher. Simple code which can be used for demonstration/education etc. For more information see https://en.wikipedia.org/wiki/Kasiski_examination

Currently it only works for Swedish text since it depends on a language sample. (Kasiski's attack is based on statistical analysis).

/August Linnman, June 2022

'''

import string
from math import log
import random
import time
import argparse
import configparser

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

def setupLanguage ():
    '''Setup all used language parameters from the ini file'''
    global langAlphaChars
    global langSampleText
    global lang
    global langExtraChars
    global langNumChars
    global langSpecialChars

    config = configparser.RawConfigParser()
    config.read('kasiski.ini')
    lang             = config ['LanguageSpecific']['lang']
    langExtraChars   = config ['LanguageSpecific']['langExtraChars']
    langNumChars     = config ['LanguageSpecific']['langNumChars']
    langSpecialChars = config ['LanguageSpecific']['langSpecialChars'] 

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

    with open('sample.txt', 'r', encoding='utf-8') as file:
        langSampleText = file.read().replace('\n', '')

    for i in range (0, len(langChars)):
        langMap      [langChars[i]] = i
    for i in range (0, len(langAlphaChars)):
        langAlphaMap [langAlphaChars[i]] = i

def setupMonograms (s, alpha=False):
    global monogramCache
    
    try:
        return monogramCache [(s,alpha)]
    except KeyError:
        pass
    
    result = {}
    if alpha:
        charsChosen = langAlphaChars
        mapChosen = langAlphaMap
    else:
        charsChosen = langChars
        mapChosen = langMap 
    for c in charsChosen:
        result [c] = 0
    for i in range(0,len(s)):
        a = s [i]
        aPos = -1
        try:
            aPos = mapChosen [a]
        except KeyError:
            pass
        if aPos != -1:
            monogram = str(a) 
            count = 0
            try:
                count = result [monogram]
            except KeyError:
                pass
            result [monogram] = count + 1
    summing = sum (result.values())
    for e in result:
        v = result [e]
        if summing == 0:
            result [e] = 0
        else:
            result [e] = v / summing
    monogramCache [(s,alpha)] = result
    return result

def setupBigrams (s):
    global bigramCache
    
    s = s.lower()
    
    try:
        return bigramCache [s]
    except KeyError:
        pass    
    
    result = {}
 
    for i in range(0,len(s)-1):
        a = s [i]
        b = s [i+1]
        aPos = -1
        bPos = -1
        try:
            aPos = langAlphaMap [a]
        except KeyError:
            pass
        try:
            bPos = langAlphaMap [b]
        except KeyError:
            pass
        if (aPos != -1) and (bPos != -1):
            bigram = str(a) + str(b)
            count = 0
            try:
                count = result [bigram]
            except KeyError:
                pass
            result [bigram] = count + 1
    summing = sum (result.values())
    for e in result:
        v = result [e]
        result [e] = v / summing
    bigramCache [s] = result
    return result

def freqAnalysis (s, lang=langSampleText, alpha=False):
    s = s.lower ()
    langNgrams = setupMonograms (lang, alpha)
    sNgrams = setupMonograms (s, alpha)
    count = 0
    summed = 0
    for m in sNgrams:
        a = sNgrams [m]
        b = langNgrams [m]
        summed += (a - b)**2
        count += 1
    retval = summed 
    return -log(retval)

def freqAnalysisBigrams (s, lang=langSampleText):
    s = s.lower ()
    langBgrams = setupBigrams (lang)
    sBgrams = setupBigrams (s)
    count = 0
    summed = 0
    for m in sBgrams:
        a = sBgrams [m]
        b = 0
        try:
            b = langBgrams [m]
        except KeyError:
            pass
        if b == 0:
            b = -0.1
        summed += (a - b)**2
        count += 1
    retval = summed 
    if retval == 0:
        retval = -1
    else:
        retval = -log(retval)
    return retval

def indexOfCoincidence (s):
    s = s.lower ()
    monograms = setupMonograms (s)
    result = 0
    for m in monograms:
        result += monograms[m]**2
    return result    
    
def Viginere (s, K, alpha=False):
 
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
    for c in s:
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
    result = []
    for i in range (0, len(K)):
        result.append (-K[i])
    return result

def findBlockSizes (c, minSize, maxSize, numBs=2):
    prevIoc = 2**32
    foundRaises = {}
    for blockSize in range (minSize, maxSize+1):
        iocSum = 0
        counter = 0
        for testStringIndex in range (0,blockSize):
            testString = ""
            currentPos = testStringIndex
            while currentPos < len(c):
                testString = testString + c[currentPos]
                currentPos += blockSize
            ioc = indexOfCoincidence (testString)
            iocSum += ioc
            counter += 1
        averageIoc = iocSum / counter  
        foundRaises [blockSize] = averageIoc / prevIoc
        prevIoc = averageIoc
    if len(foundRaises) == 0:
        return []
    bestBlockSize = max(foundRaises.items(), key=lambda x: x[1])[0]
    sortedBlockSizes = dict(sorted(foundRaises.items(), key=lambda item: item[1], reverse=True))
    retVal = []
    counter = 0
    for bs in sortedBlockSizes:
        retVal.append (bs)
        counter += 1
        if counter >= numBs: 
            break
    return retVal

def getExtract (s, bs, index):
    result = []
    currentPos = index
    while currentPos < len(s):
        result.append (s[currentPos])
        currentPos += bs
    retVal = ""
    return retVal.join(result)

def attack (s,minSize,maxSize,bsExamined, look=-1, alphaOnly=False):
 
    bss = findBlockSizes (s,minSize,maxSize,bsExamined)
    comparedResults = {}
    
    for bs in bss: 
    
        if bs == -1:
            return "-"

        candidateKeys = []
        bestIml = 2**20
        for i in range (0, bs):
            candidateKeys.append ([])
            testString = getExtract (s, bs, i)
            
            examinedTestKeys = {}

            for testKey in range(0, len(langChars)):
                Ktest = [-testKey]
                decPermutedTestKey = Viginere (testString, Ktest, alpha=alphaOnly)
                
                if look == i:
                    print ("Look at decrypted string for K = "+str(Ktest)+ " = <" + str(decPermutedTestKey) + ">")
                
                freqPoint = freqAnalysis (decPermutedTestKey, langSampleText, False)  
                examinedTestKeys [testKey] = freqPoint
            
            B = max(examinedTestKeys.items(), key=lambda x: x[1])
            bestKey = B [0]
            bestValue = B [1]
            
            if look == i:
                print ("Best key was = " + str(bestKey))

            candidateKeys [i].append (bestKey)
        decryptKey = []
        for i in range (0, len(candidateKeys)):
            try:
                decryptKey.append (-(candidateKeys[i][0]))
            except IndexError:
                # Failed to find suitable key. 
                return "-"
        result = Viginere (s, decryptKey, alpha=alphaOnly)
 
        ST = langSampleText
        freqDecrypted = 2*freqAnalysis (result, ST) + freqAnalysisBigrams (result, ST)
        comparedResults [bs] = (result, freqDecrypted, decryptKey)

    if len(comparedResults) == 0:
        raise Exception ("Cannot find any suitable decryption key. Cleartext is probably too short.")
    B = max(comparedResults.items(), key=lambda x: x[1][1])
    bestResult = B [1][0]
    bestKey    = B [1][2]
    return bestResult, bestKey

def stringSimilarity (a, b):
    toCheck = min (len(a), len(b))
    matches = 0
    for i in range (0, toCheck):
        if (a[i] == b[i]):
            matches += 1
    return matches / toCheck

def doEncryption (clearText, minKeyLength, maxKeyLength, alphaOnly=False):
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

    encrypted = Viginere (clearText, K, alpha=alphaOnly)
    ''' This code is just for verification
    decrypted = Viginere (encrypted, negateKey(K), alpha=alphaOnly)
    
    if (clearText.lower() != decrypted.lower()):
        raise Exception ("Cipher doesn't work!")
    '''
    return encrypted, K
    
def testAttack (testText, minKeyLength, maxKeyLength, maxSize, bsExamined, look=-1, alphaOnly=False): 
    encrypted, usedKey = doEncryption (testText, minKeyLength, maxKeyLength, alphaOnly=alphaOnly)
 
    result, bestKey = attack (encrypted, 1, maxSize, bsExamined, look=look, alphaOnly=alphaOnly)
 
    return stringSimilarity (result.lower(), testText.lower()), bestKey, result

def testAttacks (clearText):     
    NROFTESTS = 100
    MINKL = 4
    MAXKL = 4
    TESTTEXT = clearText
    ALPHA = False
    BSEXAMINED = 3
    LOOK = -1
    MAXKEYLENGTHSEARCH = len(TESTTEXT) // 10
    
    startTime = time.time()  

    successMeasure = 0.0
    for i in range (0, NROFTESTS):
        sm, bestKey, result = testAttack (TESTTEXT, MINKL, MAXKL, MAXKEYLENGTHSEARCH, BSEXAMINED, LOOK, alphaOnly=ALPHA)
        print (result) ## TODO REMOVE
        successMeasure += sm
    endTime = time.time()        
    avgSuccessMeasure = successMeasure / NROFTESTS
    print ("")
    print (str(NROFTESTS) + " attacks performed. Success measure is " + str(round(avgSuccessMeasure*100,2)) +\
           " %. Time taken = " + str(endTime-startTime) + " sec.")


def encrypt (s, kl) :
    encrypted, usedKey = doEncryption (s, kl, kl, False)
    return encrypted, usedKey

def parseArguments ():
    parser = argparse.ArgumentParser(description='Kasiski method',\
                                     epilog='This is a simple test program for Kasiski\'s attack on Vigenère ciphers')
    
    parser.add_argument("-if", "--input_file",            help="input file for cleartext (-ct or -test commands)", \
                        action="store")
    parser.add_argument("-of", "--output_file",           help="output file", \
                        action="store")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-enc",  "--cleartext_to_encrypt", help="Cleartext to encrypt",\
                       action="store", nargs='?', const=0, type=int)
    group.add_argument("-crack", "--ciphertext_to_crack", help="Ciphertext to crack",\
                       action="store", nargs='?', const=0, type=int)
    group.add_argument("-test","--run_sequence_of_tests", help="Cleartext to use for encryption and cracking attempts in a test sequence",\
                       action="store", nargs='?', const=0, type=int)
 
    args = parser.parse_args()
    va = vars(args)
    
    ct             = va ['cleartext_to_encrypt']
    cit            = va ['ciphertext_to_crack']
    test           = va ['run_sequence_of_tests']
    
    inputFileName  = va ['input_file']
    outputFileName = va ['output_file']

    if (ct == 0 or cit == 0 or test == 0) and inputFileName is None:
        parser.error ("You need to specify -if since one of -enc, -crack or -test have been set but not assigned a value")

    return ct, cit, test, inputFileName, outputFileName 

def main ():

    def readFromFile (fileName) :
        with open(fileName, 'r', encoding='utf-8') as file:
            return (file.read().replace('\n', ''))

    def writeToFile (fileName, s) :
        with open(fileName, 'w', encoding='utf-8') as file:
            file.write(s)
    
    clearText, cipherText, test, inputFileName, outputFileName = parseArguments ()

    if clearText is not None :
        if inputFileName is not None:
            clearText = readFromFile (inputFileName)
        encryptedText, usedKey = encrypt (clearText,4)
        if outputFileName is not None:
            writeToFile (outputFileName, encryptedText)
            print ("Encrypted text written to " + outputFileName)
        else:
            print ("This is the encryption: <" + encryptedText + ">")
        print ("Used key = " + str(usedKey))
    elif cipherText is not None:
        if inputFileName is not None:
            cipherText = readFromFile (inputFileName)
        startTime = time.time()          
        result, bestKey = attack (cipherText, 2, 12, 3)
        endTime = time.time()
        if outputFileName is not None:
            writeToFile (outputFileName, result)
            print ("Cracking attempt written to " + outputFileName + ". Time taken = "+str(endTime-startTime)+" sec.")            
        else:
            print ("This is the cracking attempt <" + result + ">. Time taken = "+str(endTime-startTime)+" sec.")        
    elif test is not None:
        if inputFileName is not None:
            test = readFromFile (inputFileName)
        testAttacks(test)
    else:
        raise Exception ("Invalid arguments specified")

setupLanguage ()
main ()






