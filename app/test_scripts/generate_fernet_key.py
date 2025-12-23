from cryptography.fernet import Fernet

key = Fernet.generate_key()     
cipher_suite = Fernet(key)

print(key)