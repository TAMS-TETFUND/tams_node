import time


def rego():
    count = 250
    print(count)
    return True


count = 0
while True:
    print(count)
    if count == 5:
        rego()
    count += 1
    time.sleep(1)
    if count == 200:
        break
