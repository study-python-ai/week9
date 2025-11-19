import bcrypt


def hash_password(password: str) -> str:
    """비밀번호를 bcrypt로 해싱

    bcrypt는 72바이트 제한이 있으므로 자동으로 truncate합니다.
    """
    password_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """평문 비밀번호와 해시 비교

    bcrypt는 72바이트 제한이 있으므로 자동으로 truncate합니다.
    """
    password_bytes = plain_password.encode('utf-8')[:72]
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)
