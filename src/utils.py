def str_to_bool(val):
    if isinstance(val, str):
        val = val.lower()
    if val in (True, "true"):
        return True
    if val in (False, "false"):
        return False
    msg = f"Cannot convert value to bool: {val!r}"
    raise ValueError(msg)
