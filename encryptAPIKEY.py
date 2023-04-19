#######################################################################################################################################################
# Description : 
#     This program will ask user to input API Key and create encrypted files "refKey.txt" and "encryptedAPIKEY.txt" under "key" folder for using. 
#     If the key folder doesn't exist, it will create the folder first.
#
# Remark : 
#     This program is referenced to https://ch-nabarun.medium.com/how-to-encrypt-and-decrypt-application-password-using-python-15893cd28bef
#     This program only need to be executed once when the first time using or the API Key is changed.
#######################################################################################################################################################


# Encrypt the API Key
from cryptography.fernet import Fernet
# File operation
import os


# This function is the main function
def main():
    # Check and create the folder if does not exist
    path = 'key'
    if not os.path.isdir(path):
        os.mkdir(path)
    # Get the API Key from input
    my_apikey = input('Please enter the API Key : ')
    # Generate the ref key and write into a file for future using
    key = Fernet.generate_key()
    with open('key/refKey.txt', "wb") as frk:
        frk.write(key)
    # Encrypt the API Key and write into a file for future using
    refKey = Fernet(key)
    # Convert the API Key as byte
    my_apikeybyt = bytes(my_apikey, 'utf-8')
    encrypted_apikey = refKey.encrypt(my_apikeybyt)
    with open('key/encryptedAPIKEY.txt', "wb") as fenk:
        fenk.write(encrypted_apikey)
    # Check if both key file is existed
    if os.path.exists('key/refKey.txt') and os.path.exists('key/encryptedAPIKEY.txt'):
        print('Encrypt API Key success')
    else:       
        print('Error : Fail to encrypt API Key')


if __name__ == '__main__':
    main()