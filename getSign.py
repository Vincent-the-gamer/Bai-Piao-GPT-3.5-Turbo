"""
逆向接口，对SHA-256的js crypto方法来生成sign
e是13位时间戳
"""

import hashlib
import time

def get_sign(message: str):
    n = "undefined"
    e = int(time.time()*1000)
    signText = f"{e}:{message}:{n}"
    sha256 = hashlib.sha256()

    sha256.update(signText.encode("utf-8"))
    sign = sha256.hexdigest()

    return sign
