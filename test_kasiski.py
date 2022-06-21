import pytest
import kasiski

textToEncrypt = "Nisse är en kul typ som ofta går ut i skogen och plockar blåbär tillsammans med Pelle"+\
                " som arbetar som snickare inne i staden och de har ofta roligt tillsammans."+\
                "Men ibland bråkar de, men de kommer sen nästan alltid överens igen"

def test_encrypt_crack ():
    kasiski.main (["-enc", "KAKA"])

    clearTextFileName = "clear.txt"
    encryptedTextFileName = "encrypted.txt"
    crackedTextFileName = "cracked.txt"
    
    kasiski.main (["-enc", textToEncrypt])
    kasiski.main (["-enc", textToEncrypt, "-of", "encrypted.txt"])
    with open(clearTextFileName, 'w', encoding='utf-8') as file:
            file.write(textToEncrypt)
    kasiski.main (["-enc", textToEncrypt, "-if",clearTextFileName,"-of", encryptedTextFileName])
    kasiski.main (["-crack", "-if", encryptedTextFileName, "-of", crackedTextFileName])
    with open(crackedTextFileName, 'r', encoding='utf-8') as file:
        crackedText = file.read().replace('\n', '')
    similarity = kasiski.stringSimilarity (crackedText.lower (), textToEncrypt.lower ())
    assert (similarity >= 0.95)
    
def test_test ():
    kasiski.main (["-test", textToEncrypt])
    kasiski.main (["-test", textToEncrypt,"-of","foo.txt"])
    

    

