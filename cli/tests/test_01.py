#
def is_prime(num):
    # Prime numbers must be greater than 1
    if num < 2:
        return False

def test_prime_prime_number():
    assert is_prime(29)
    