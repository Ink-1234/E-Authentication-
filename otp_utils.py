import time

def generate_otp():
    return str(int(time.time()) % 1000000).zfill(6)

def verify_otp(secret, otp):
    return otp == secret
