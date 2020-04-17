__all__ = ['bytes_to_str_or_default']


def bytes_to_str_or_default(bytes_arg, default=""):
    return default if not bytes_arg else bytes_arg.decode()
