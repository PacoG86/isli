from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
hash = pwd_context.hash("1234")
print("Hash:", hash)
print("¿Verifica?:", pwd_context.verify("1234", hash))
