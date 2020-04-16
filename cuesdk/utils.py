__all__ = ['bytes_to_str_or_default']


def bytes_to_str_or_default(bytes, default=""):
    return default if not bytes else bytes.decode()
