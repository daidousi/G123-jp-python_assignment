#######################################################################################################################################################
# Description : 
#     This program will decrypted the API Key from encrypted files "refKey.txt" and "encryptedAPIKEY.txt" under "key" folder.
#     If one of the key files doesn't exist, it will return None. 
#
# Remark : 
#     This program is referenced to https://ch-nabarun.medium.com/how-to-encrypt-and-decrypt-application-password-using-python-15893cd28bef
#     This program can be called multiple times when any program want to get the API Key from encrypted files.
#######################################################################################################################################################


# Encrypt the API Key
from cryptography.fernet import Fernet
# File operation
import os


# This functoin is used to check the both key files
# output : result = True  - both key files exist
#          result = False - One of the key file does not exist
def check_key_file():
    # Check if both key file is existed
    if os.path.exists('key/refKey.txt') and os.path.exists('key/encryptedAPIKEY.txt'):
        result = True
    else:       
        result = False
        print('Error : Key file [key/refKey.txt] or [key/encryptedAPIKEY.txt] does not exist')
    return result


# This function is the main function
def main():
    # Init the API Key
    apikey = None
    # Check the key file befor to decrypt API KEY
    ret = check_key_file()
    if not ret:
        return
    # Read encrypted API Key and convert into byte
    with open('key/encryptedAPIKEY.txt') as fenk:
        encpwd = ''.join(fenk.readlines())
        encpwdbyt = bytes(encpwd, 'utf-8')
    # Read ref key and convert into byte
    with open('key/refKey.txt') as frk:
        refKey = ''.join(frk.readlines())
        refKeybyt = bytes(refKey, 'utf-8')
    # use the key and encrypt pwd
    keytouse = Fernet(refKeybyt)
    apikey = keytouse.decrypt(encpwdbyt).decode()
    return apikey


if __name__ == '__main__':
    main()