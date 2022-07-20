import random


def numbers():
    two = [2 for _ in range(200)]
    three = [3 for _ in range(100)]
    five = [5 for _ in range(50)]
    fifty = [50 for _ in range(5)]
    full_numbers = two + three + five + fifty
    all_numbers = list()
    for i in range(len(full_numbers)):
        try:
            number = full_numbers.pop(random.randint(0, len(full_numbers)))
            all_numbers.append(str(number))
        except IndexError:
            continue

    print(all_numbers)
    return all_numbers


def save_numbers():
    save_number = ' '.join(numbers())
    with open('double_save.txt', 'w') as w:
        w.write(save_number)


def read_and_save_txt():
    with open('double_save.txt', "r") as r:
        read = r.read()
    list_ = read.split(' ')
    save_num = list(map(int, list_))
    # print(save_num)
    return save_num


def return_number():
    save = read_and_save_txt()
    number = random.choice(save)
    return number

#
# for _ in range(100):
#     print(return_number())
