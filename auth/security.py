import hashlib

# Function to hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Function to check if the password matches the hashed version
def check_password(password, hashed_password):
    return hash_password(password) == hashed_password
