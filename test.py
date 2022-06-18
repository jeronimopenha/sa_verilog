import random


def test_swap_algorithm():
    random.seed(0)
    n = 4
    a = []
    b = []
    for i in range(n):
        a.append(i)
        b.append(i)
    swap_base(a)
    swap_algorithm(b)


def swap_base(a=[]):
    random.seed(0)
    for i in range(len(a)):
        for j in range(len(a)):
            if j == i:
                continue
            rnd = random.randint(0, 1)
            if rnd:
                a[i], a[j] = a[j], a[i]
    print(a)


def swap_algorithm(a):
    random.seed(0)
    b = [0 for i in range(len(a))]
    p = [False for i in range(len(a))]
    for i in range(len(a)):
        for j in range(len(a)):
            if j == i:
                continue
            rnd = random.randint(0, 1)
            if rnd:
                p_i = p[i]
                p_j = p[j]

                if p_i == True:
                    n1 = b[i]
                else:
                    n1 = a[i]

                if p_j == True:
                    n2 = b[j]
                else:
                    n2 = a[j]

                # troca cell1
                # troca cell2
                if p_i == True:
                    a[j] = n1
                    b[i] = n2
                else:
                    a[i] = n2
                    b[j] = n1

                # acerta ponteiro cell2
                if p_i == p_j:
                    p[j] = not p[j]
    for i in range(len(a)):
        if p[i]:
            print('%d ' % b[i])
        else:
            print('%d ' % a[i])


test_swap_algorithm()
