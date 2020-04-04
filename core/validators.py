

def is_iin(v):
    if not all((isinstance(v, str), len(v) == 12, v.isdigit())):
        # невалидная форма
        return False
    if v[4] in '456':
        # БИН
        return False

    checksum = int(v[-1])

    try:
        return checksum == calculate_checksum(v)
    except ValueError:
        return False


def calculate_checksum(v) -> int:
    value = v[:11]
    first_run = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    first = sum([int(value[i]) * first_run[i] for i in range(11)]) % 11

    if first > 10:
        raise ValueError('IIN cannot have check digit')

    if first == 10:
        second_run = [3, 4, 5, 6, 7, 8, 9, 10, 11, 1, 2]
        second = sum([int(value[i]) * second_run[i] for i in range(11)]) % 11
        if second >= 10:
            raise ValueError('IIN cannot have check digit')
        return second
    else:
        return first
