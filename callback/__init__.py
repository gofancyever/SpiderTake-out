import time


def callback(state):
    print(state)
def request(func):
    time.sleep(2)
    func(True)




if __name__ == '__main__':
    request(callback)