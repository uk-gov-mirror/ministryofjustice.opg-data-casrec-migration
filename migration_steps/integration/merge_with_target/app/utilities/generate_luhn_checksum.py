from typing import List

min_number = 70000000000
max_number = 79999999999


def double_alternate_digits(list_of_digits: List[int]) -> List[int]:
    digits = list_of_digits

    if len(digits) % 2 == 0:
        double_alternate = [x * 2 if i % 2 != 0 else x for i, x in enumerate(digits)]
    else:
        double_alternate = [x * 2 if i % 2 == 0 else x for i, x in enumerate(digits)]

    return double_alternate


def sum_big_digits(list_of_digits: List[int]) -> List[int]:
    return [int(str(x)[0]) + int(str(x)[1]) if x > 9 else x for x in list_of_digits]


def sum_all_digits(list_of_digits: List[int]) -> int:
    total = 0
    for x in list_of_digits:
        total += x
    return total


def multiply_by_9_and_return_unit(number: int) -> int:
    return int(str(number * 9)[-1:])


def generate_luhn_checksum(original_number):
    """
    1. double every other digit starting from the right hand side
    2. if the resulting number is >9, sum the two digits
    3. sum all the digits
    4. multiple the total by 9 - the units part of the result is your checksum

    stick this on the end of your original number and voila!
    """
    digits = [int(x) for x in str(original_number)]
    step_1 = double_alternate_digits(list_of_digits=digits)
    step_2 = sum_big_digits(list_of_digits=step_1)
    step_3 = sum_all_digits(list_of_digits=step_2)
    step_4 = multiply_by_9_and_return_unit(number=step_3)

    return step_4


def append_checksum(original_number: int) -> int:
    checksum = generate_luhn_checksum(original_number=original_number)

    return int(str(original_number) + str(checksum))
