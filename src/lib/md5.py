import hashlib


def get_md5_str(hash_str):
    hl = hashlib.md5()
    hl.update(hash_str.encode("utf-8"))
    hash_strs = hl.hexdigest()
    return hash_strs
