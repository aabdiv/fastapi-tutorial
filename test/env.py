import os

secret = os.getenv("SECRET", "no secret")

print(f"we found {secret}")
