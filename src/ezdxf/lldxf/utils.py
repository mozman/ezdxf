def value_to_float(value: str) -> float:
    """
    Safely convert a value to a float.

    Sometimes the value can have a look:
    1.000000E 20
    -1.000000E 20
    and when we put it into a float() we get a ValueError
    """
    try:
        return float(value)
    except ValueError:
        v = value.replace(" ", "+")
        return float(v)
