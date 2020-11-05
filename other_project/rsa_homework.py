import numpy as np
import time
import math


def encrypt(file, e, n, label):
    """
    This is the function for encrypt a text file.
    :param file: a txt file you want to encrypt
    :param e: a integer related to RSA
    :param n: a integer related to RSA
    :return: return the encrypted file name and the file type for the origin file
    """
    label.config(text="Encryption in progress.....")
    file2 = file.split(".")[0] + "_encrypted.txt"
    f_2 = open(file2, "w")
    # open file read the file and encrypt the file
    with open(file) as f:
        for line in f:
            for i in line:
                etc = ord(i)
                etc = etc ** e
                etc = int(np.mod(etc, n))
                f_2.write("%s\n" % etc)
    label.config(text="Encryption Done!")
    return file2, file.split(".")[1]


def decrypt(file, file_type, d, n, label):
    """
    This is the function for decrypt the file
    :param file: the encrypted file
    :param file_type: the origin file's type
    :param d: a integer related to RSA
    :param n: a integer related to RSA
    :return: return 0
    """
    label.config(text="Decryption in progress.....")
    file2 = file.split(".")[0] + "_decrypted." + file_type
    f_2 = open(file2, "w")
    # open the file and read the file and decrypt the file
    with open(file) as f:
        decrypt_list = []
        data_list = []
        for line in f:
            line = line.strip("\n")
            line = int(line)
            data_list.append(line)
        for item in data_list:
            dct = item ** d
            dct = int(np.mod(dct, n))
            data = chr(dct)
            decrypt_list.append(data)
        data_whole = ''.join(decrypt_list)
        f_2.write(data_whole)
    label.config(text="Decryption Done!!!")
    return 0


def is_prime(num):
    """
    This is the function to determine a number is a prime number or not, this function can determine a number
    is a prime or not really fast.
    :param num: the number you want to know is a prime number or not
    :return: if the number is a prime number then return true else return false
    """
    if num % 2 == 0:
        return num == 2
    if num % 3 == 0:
        return num == 3
    if num % 5 == 0:
        return num == 5
    for prime in range(7, int(math.sqrt(num)) + 1, 2):
        if num % prime == 0:
            return False
    return True


def get_two_large_prime_number_under(low, high):
    """
    This is the function that generate two large prime number from given range
    :param low: the lower bound of the range
    :param high: the upper bound of the range
    :return: return a list that contain the two large prime numbers
    """
    candidate = []
    count = 0
    # determine the number in the range is prime or not
    for i in range(low, high):
        b = high - i - 1
        if is_prime(b) is True:
            count += 1
            if count == 3:
                break
            else:
                candidate.append(b)
        else:
            pass
    return candidate


def get_prime_divisors(number):
    """
    calculate the prime divisor of a giver number
    :param number: the number you want to calculate the prime divisor
    :return: a list of all prime divisors
    """
    divisors_list = set([])
    min_div = 2
    if number == min_div:
        divisors_list.add(number)
    else:
        while number >= min_div:
            if number % min_div == 0:
                divisors_list.add(min_div)
                number = number / min_div
            else:
                min_div += 1
    return list(divisors_list)


def generate_key(lower, upper):
    """
    This is the function used to generate the key for RSA encryption.
    this algorithm can generate a key like 9999996000000319 9667267915798924 2272667 from 100000000 in 2.12 seconds
    :param lower: the lower bound for the key generate from
    :param upper: the upper bound for the key generate from
    :return: the N, D, E value for the RSA
    """
    prime_number_list = get_two_large_prime_number_under(lower, upper)
    N = prime_number_list[0] * prime_number_list[1]
    X = (prime_number_list[0] - 1) * (prime_number_list[1] - 1)
    divisor = get_prime_divisors(X)
    aa = get_two_large_prime_number_under(2, max(divisor))
    j = 0
    # find the value for D
    while True:
        if aa[0] in divisor or aa[1] in divisor:
            j += 1
            aa = get_two_large_prime_number_under(2, max(divisor) + j)
        else:
            E = aa[1]
            k = 1
            deter = (k * X + 1) % E
            D = (k * X + 1) / E
            while True:
                if deter != 0:
                    k += 1
                    deter = (k * X + 1) % E
                    D = (k * X + 1) / E
                else:
                    break
            break
    return N, int(D), E


if __name__ == "__main__":
    now = time.time()
    # the key generation process is super fast, BUT
    # please enter the upper bound lower than 10000 to keep the decryption time in a reasonable range.
    n, d, e = generate_key(1, 1000)
    print(n, d, e)
    now2 = time.time()
    print("key generation time is %s seconds" % (now2 - now))
    # encrypt_file, f_type = encrypt("test.txt", e, n)
    # decrypt(encrypt_file, f_type, d, n)

